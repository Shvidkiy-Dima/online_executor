import io
import tarfile
import time
import uuid
from textwrap import dedent
from django.conf import settings
from epicbox import start, utils, exceptions
from epicbox.sandboxes import Sandbox as _Sandbox
import structlog
from docker.errors import APIError, DockerException
from requests.exceptions import RequestException

logger = structlog.get_logger()
_SANDBOX_NAME_PREFIX = 'sand_box'


class Volume:

    def __init__(self, host_path, container_path, mode):
        self.volume = {host_path: {'bind': container_path, 'mode': mode},}


class SandBox:

    def __init__(self, workdir, volume=None):
        self.workdir = workdir
        self.volume = volume
        self.docker_image = None
        self.files = None
        self.limits = None
        self.user = 'root'
        self.read_only = False
        self.network_disabled = False

    def _create_sandbox_container(self, sandbox_id, image, command, limits,
                                  user=None, read_only=False, network_disabled=True):
        name = _SANDBOX_NAME_PREFIX + sandbox_id
        mem_limit = str(limits['memory']) + 'm'
        ulimits = utils.create_ulimits(limits)
        environment = None
        docker_client = utils.get_docker_client()
        log = logger.bind(sandbox_id=sandbox_id)
        log.info("Creating a new sandbox container", name=name, image=image,
                 command=command, limits=limits, workdir=self.workdir, user=user,
                 read_only=read_only, network_disabled=network_disabled)
        try:
            c = docker_client.containers.create(image,
                                                command=command,
                                                user=user,
                                                stdin_open=True,
                                                environment=environment,
                                                network_disabled=network_disabled,
                                                name=name,
                                                working_dir=self.workdir,
                                                volumes=self.volume.volume,
                                                read_only=read_only,
                                                mem_limit=mem_limit,
                                                # Prevent from using any swap
                                                memswap_limit=mem_limit,
                                                ulimits=ulimits,
                                                # limit pid
                                                pids_limit=limits["processes"],
                                                # Disable the logging driver
                                                log_config={'type': 'none'})
        except (RequestException, DockerException) as e:
            if isinstance(e, APIError) and e.response.status_code == 409:
                # This may happen because of retries, it's a recoverable error
                log.info("The container with the given name is already created",
                         name=name)
                c = {'Id': name}
            else:
                log.exception("Failed to create a sandbox container")
                raise exceptions.DockerError(str(e))
        log.info("Sandbox container created", container=c)
        return c

    def create(self, command, files=None, limits=None):
        sandbox_id = str(uuid.uuid4())
        command_list = ['/bin/sh', '-c', command]
        limits = utils.merge_limits_defaults(limits)
        c = self._create_sandbox_container(sandbox_id, self.docker_image, command_list,
                                           limits,  user=self.user, read_only=self.read_only,
                                           network_disabled=self.network_disabled)

        if files:
            self._write_files(c, files)
        sandbox = _Sandbox(sandbox_id, c, realtime_limit=limits['realtime'])
        logger.info("Sandbox created and ready to start", sandbox=sandbox)
        return sandbox

    def run(self, command, files=None, stdin=None, limits=None):
        """Run a command in a new sandbox container and wait for it to finish
        running.  Destroy the sandbox when it has finished running.

        The arguments to this function is a combination of arguments passed
        to `create` and `start` functions.

        :return dict: The same as for `start`.

        :raises DockerError: If an error occurred with the underlying
                             docker system.
        """
        with self.create(command=command, files=files, limits=limits) as sandbox:
            return self.start(sandbox, stdin=stdin)

    def start(self, sandbox, stdin=None):
        return start(sandbox, stdin)

    def _write_files(self, container, files):
        """Write files to the working directory in the given container."""
        # Retry on 'No such container' since it may happen when the function
        # is called immediately after the container is created.
        # Retry on 500 Server Error when untar cannot allocate memory.
        docker_client = utils.get_docker_client(retry_status_forcelist=(404, 500))
        log = logger.bind(files=utils.filter_filenames(files), container=container)
        log.info("Writing files to the working directory in container")
        mtime = int(time.time())
        files_written = []
        tarball_fileobj = io.BytesIO()
        with tarfile.open(fileobj=tarball_fileobj, mode='w') as tarball:
            for file in files:
                if not file.get('name') or not isinstance(file['name'], str):
                    continue
                content = file.get('content', b'')
                file_info = tarfile.TarInfo(name=file['name'])
                file_info.size = len(content)
                file_info.mtime = mtime
                tarball.addfile(file_info, fileobj=io.BytesIO(content))
                files_written.append(file['name'])
        try:
            docker_client.api.put_archive(container.id, self.workdir, tarball_fileobj.getvalue())
        except (RequestException, DockerException) as e:
            log.exception("Failed to extract an archive of files to the working "
                          "directory in container")
            raise exceptions.DockerError(str(e))
        log.info("Successfully written files to the working directory",
                 files_written=files_written)


class ModuleRunSandBox(SandBox):

    def __init__(self, module, user, *args, **kwargs):
        super().__init__(workdir='/sandbox', *args, **kwargs)
        self.docker_image = 'ubuntu/online_runner:3.8'
        self.files = [{'name': 'main.py', 'content': module.code}]
        self.limits = {'cputime': 1, 'memory': 64, 'realtime': 5}
        self.volume = Volume(user.venv_path, f'{self.workdir}/venv', 'ro')

    def run(self, *args, **kwargs):
        res = super().run(f'{self.workdir}/venv/bin/python3 main.py',
                          files=self.files, limits=self.limits)
        return res


class ModuleRunAPISandBox(ModuleRunSandBox):

    def __init__(self, module, user, *args, **kwargs):
        super().__init__(module, user, *args, **kwargs)
        code = self._get_code(module.code)
        self.files = [{'name': 'main.py', 'content': code}]

    def _get_code(self, code):

        code = b"from call_me import response\n" \
               + \
               code \
               + \
               b'\nresponse.print_result()'

        return code


class PackageAddSandBox(SandBox):

    def __init__(self, package_name, user, *args, **kwargs):
        super().__init__(workdir='/sandbox', *args, **kwargs)
        self.docker_image = 'ubuntu/online_runner:3.8'
        code = self._get_code(package_name, user.packages_size)
        self.files = [{'name': 'main.py', 'content': code}]
        self.limits = {'cputime': 30, 'memory': 500, 'realtime': 120}
        self.volume = Volume(user.venv_path, f'{self.workdir}/venv', 'rw')

    def run(self, *args, **kwargs):
        res = super().run(f'{self.workdir}/venv/bin/python3 main.py',
                          files=self.files, limits=self.limits)
        return res

    def _get_code(self, package_name, current_size, max_size=261120):
        code = f"""
        from importlib import metadata as importlib_metadata
        import pip, os, subprocess, sys, shutil
        shutil.copytree('venv', 'test_venv', symlinks=True)
        
        res = subprocess.run(['du', '-shk', 'test_venv'], capture_output=True)
        init_size = int(res.stdout.decode().split("\t")[0])
        
        res = subprocess.run(['{self.workdir}/test_venv/bin/python3','-m', 'pip', 'install', '{package_name}'], capture_output=True)
        if res.returncode != 0:
            raise RuntimeError(res.stderr.decode())
        
        res = subprocess.run(['du', '-shk',  'test_venv'], capture_output=True)
        cur_size = int(res.stdout.decode().split("\t")[0])
        
        diff = cur_size - init_size
        
        current_size = {current_size} + diff
        if current_size > {max_size}:
            raise RuntimeError('Max size') 
        
        res = subprocess.run(['{self.workdir}/venv/bin/python3','-m', 'pip', 'install', '{package_name}'], capture_output=True)
        if res.returncode != 0:
            raise RuntimeError(res.stderr.decode())
        
        try:
            version = importlib_metadata.distribution('{package_name}').version
        except Exception:
            version = ''
            
        pcg_size = current_size - {current_size}
        sys.stdout.write(str(pcg_size)+ '|' + version )
        """
        return dedent(code).encode('utf8')


class PackageRemoveSandBox(PackageAddSandBox):

    def _get_code(self, package_name, current_size, max_size=261120):
        code = f"""
        import pip, os, subprocess, sys
    
        res = subprocess.run(['du', '-shk', 'venv'], capture_output=True)
        init_size = int(res.stdout.decode().split("\t")[0])


        res = subprocess.run(['{self.workdir}/venv/bin/python3','-m', 'pip', 'uninstall', '-y', '{package_name}'], capture_output=True)
        if res.returncode != 0:
            raise RuntimeError(res.stderr.decode())
        
        res = subprocess.run(['du', '-shk', 'venv'], capture_output=True)
        cur_size = int(res.stdout.decode().split("\t")[0])
        
        pcg_size = init_size - cur_size
        sys.stdout.write(str(pcg_size))
        """
        return dedent(code).encode('utf8')


class CreateVenvSandBox(SandBox):

    def __init__(self, *args, **kwargs):
        super().__init__(workdir='/sandbox', *args, **kwargs)
        self.docker_image = 'ubuntu/online_runner:3.8'
        code = self._get_code()
        self.files = [{'name': 'main.py', 'content': code}]
        self.limits = {'cputime': 30, 'memory': 500, 'realtime': 120}
        self.volume = Volume(settings.BASE_VENV, f'{self.workdir}/venv', 'rw')

    def run(self, *args, **kwargs):
        res = super().run(f'python3 main.py',
                          files=self.files, limits=self.limits)
        return res

    def _get_code(self):
        code = f"""
        import subprocess
        res = subprocess.run(['python3','-m', 'venv', 'venv'], capture_output=True)
        if res.returncode != 0:
            raise RuntimeError(res.stderr.decode())  
        subprocess.run(['chmod','-R', '777', 'venv'], capture_output=True)
        """
        return dedent(code).encode('utf8')
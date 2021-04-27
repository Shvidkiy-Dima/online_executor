import io
import tarfile
import time
import uuid
from epicbox import start, config, utils, exceptions
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

    def create(self, profile_name, command, files=None, limits=None):
        sandbox_id = str(uuid.uuid4())
        profile = config.PROFILES[profile_name]
        command_list = ['/bin/sh', '-c', command]
        limits = utils.merge_limits_defaults(limits)
        c = self._create_sandbox_container(sandbox_id, profile.docker_image, command_list, limits,  user=profile.user,
                                           read_only=profile.read_only, network_disabled=profile.network_disabled)

        if files:
            self._write_files(c, files)
        sandbox = _Sandbox(sandbox_id, c, realtime_limit=limits['realtime'])
        logger.info("Sandbox created and ready to start", sandbox=sandbox)
        return sandbox

    def run(self, profile_name, command, files=None, stdin=None, limits=None):
        """Run a command in a new sandbox container and wait for it to finish
        running.  Destroy the sandbox when it has finished running.

        The arguments to this function is a combination of arguments passed
        to `create` and `start` functions.

        :return dict: The same as for `start`.

        :raises DockerError: If an error occurred with the underlying
                             docker system.
        """
        with self.create(profile_name, command=command, files=files, limits=limits) as sandbox:
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


#
# import epicbox
# epicbox.configure(
#     profiles=[
#         epicbox.Profile('python', 'python:3.8-alpine')
#     ]
# )
#
# content = b"""
# from django.utils import timezone
# print(timezone.now())
# """
#
#
# files = [{'name': 'main.py', 'content': content}]
# limits = {'cputime': 1, 'memory': 64, 'realtime': 5}
#
# workdir = '/sandbox'
# volume = Volume('/home/borisov/PycharmProjects/startups/online_backend/user_venvs/venv', f'{workdir}/venv', 'ro')
# sandbox = SandBox(volume=volume, workdir=workdir)
# result = sandbox.run('python', f'{workdir}/venv/bin/python3 main.py', files=files, limits=limits)
#
# print(result)


# import os, psutil
# from multiprocessing import Process
# process = psutil.Process(os.getpid())
#
#
# import resource
#
# def set_memory_limit(memory_kilobytes):
#     # ru_maxrss: peak memory usage (bytes on OS X, kilobytes on Linux)
#     rsrc = resource.RLIMIT_DATA
#     soft, hard = resource.getrlimit(rsrc)
#     print(soft, hard, rsrc)
#     resource.setrlimit(rsrc, (memory_kilobytes, hard))
#
#
#
# def main():
#     set_memory_limit(5000000000 * 1024)
#     d = list(range(9999999))
#
#
#
# p = Process(target=main)
# p.start()
# p.join()
# print('END')
# print(process.memory_info().rss // 1024 // 1024)  # in bytes
# and check time

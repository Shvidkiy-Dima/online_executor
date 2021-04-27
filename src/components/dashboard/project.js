import React from "react";
import Tree from '../tree/tree'
import Editor from '../editor/editor'
import { Link, useParams } from "react-router-dom";
import request from '../../utils/request'


export default ()=> {
  const [Project, SetProject] = React.useState(null);
  const [TreeStruct, SetTreeStruct] = React.useState(null)
  let { projectId } = useParams();

  function GetProject() {
    request({ method: "get", url: `api/dashboard/project/${projectId}/` }, (res) => {
      SetProject(res.data);
      let struct = []
      let modules = res.data.modules
      let folders = res.data.folders
      for (let i of folders){
          struct.push({type: 'folder', name: i.name, 
          childrens: i.modules.map((m)=>{
              return {type: 'file', name: m.name, id: m.id}
          })
            })
      } 
      for (let m of modules){
            struct.push({type:'file', name: m.name, id: m.id})
      }
      SetTreeStruct(struct)

    });
  }

React.useEffect(GetProject, [])

if (Project === null | TreeStruct === null){
    return null
}

let InitiaModule = Project.modules[Project.modules.length-1]
  return (
    <div style={{display: 'flex'}}>
      <Tree data={TreeStruct} />
    <Editor initialText={InitiaModule.code}/> 
    </div>
  );
}

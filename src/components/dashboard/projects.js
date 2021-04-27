import React from "react";
import request from '../../utils/request'
import Project from './project'

export default ()=> {


    const [Projects, SetProjects] = React.useState(null);
  
    function GetProjects() {
      request({ method: "get", url: "api/project/" }, (res) => {
        SetProjects(res.data);
      });
    }


  if (Projects === null){
      return null
  }

  return (
    <div>
        {Projects.map(([key, value]) => (
        <Project key={key} monitor={value} />
      ))}
    </div>
  );
}

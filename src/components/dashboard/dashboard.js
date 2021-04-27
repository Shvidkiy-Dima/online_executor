import React from "react";
import Projects from './projects'
import Project from './project'
import {
  Switch,
  Route,
} from "react-router-dom";


const structure = [
  {
    type: "folder",
    name: "src",
    childrens: [
      {
        type: "folder",
        name: "Components",
        childrens: [
          { type: "file", name: "Modal.js" },
          { type: "file", name: "Modal.css" }
        ]
      },
      { type: "file", name: "index.js" },
      { type: "file", name: "index.html" }
    ]
  },
  { type: "file", name: "package.json" }
];

export default ()=> {
  return (
    <Switch>
    <Route path="/project/:projectId">
      <Project/>
    </Route>
    <Route exact path="/">
      <Projects/>
    </Route>
  </Switch>

  );
}


import React from "react";
import Projects from './projects'
import Project from './project_detail'
import {
  HashRouter as Router,
  Switch,
  Link,
  Route,
  Redirect,
} from "react-router-dom"
import WebSocketConnection from "../../utils/ws";


const common_ws = new WebSocketConnection()

export default ({logout, user})=> {


  function WsCommomConnect(){
    common_ws.connect('ws/dashboard/common/')
    return ()=> common_ws.close()
  }
  React.useEffect(WsCommomConnect, [])

  return (
    <Switch>
    <Route path="/dashboard/project/:projectId">
      <Project common_ws={common_ws} logout={logout} user={user} />
    </Route>
    <Route exact path="/dashboard">
      <Projects logout={logout} user={user} />
    </Route>
  </Switch>

  );
}


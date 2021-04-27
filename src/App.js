import React from "react";
import LoginForm from "./components/auth/login_form";
import DashBoard from "./components/dashboard/dashboard";
import ProtectedRoute from "./utils/router";
import ws from './utils/ws'
import './App.css'
import request from "./utils/request";
import {
  HashRouter as Router,
  Switch,
  Route,
} from "react-router-dom";



export default function App() {
  const [isAutheticated, setisAutheticated] = React.useState(null);
  const [User, setUser] = React.useState(null);

  function login() {
    getUser()
  }

  function logout() {
    localStorage.removeItem("token")
    setisAutheticated(false);
    setUser(null)
  }

  function getUser() {
    request(
      { method: "get", url: "api/account/profile/" },
      (res) => {
        setUser(res.data);
        setisAutheticated(true);
      },
      (err) => {
        setisAutheticated(false);
      }
    );
  }

  React.useEffect(getUser, []);

  if (isAutheticated === null){
    return null
  }


  return (
    <Router>
      <Switch>
        {/* <Route exact path="/registration">
          <RegForm auth={isAutheticated} />
        </Route> */}

        <Route exact path="/login">
          <LoginForm auth={isAutheticated} login={login} />
        </Route>

        <ProtectedRoute path="/" auth={isAutheticated}>
          <DashBoard user={User} logout={logout} ws={ws}/>
        </ProtectedRoute>
      </Switch>
    </Router>
  );
}


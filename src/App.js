import React from "react";
import LoginForm from "./components/auth/login_form";
import DashBoard from "./components/dashboard/dashboard";
import Main from './components/main/main'
import ProtectedRoute from "./utils/router";
import './App.css'
import request from "./utils/request";
import {
HashRouter as Router,
  Switch,
  Route,
} from "react-router-dom";
import { createBrowserHistory } from "history";


const customHistory = createBrowserHistory();


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
    <Router history={customHistory}>
      <Switch>
        {/* <Route exact path="/registration">
          <RegForm auth={isAutheticated} />
        </Route> */}

        <Route exact path="/login">
          <LoginForm auth={isAutheticated} login={login} />
        </Route>

        <ProtectedRoute path="/dashboard" auth={isAutheticated}>
          <DashBoard user={User} logout={logout}/>
        </ProtectedRoute>


        <Route exact path="/">
          <Main/>
        </Route>

      </Switch>
    </Router>
  );
}


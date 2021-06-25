import React from "react";
import Tree from "../tree/tree";
import Editor from "./editor";
import Packages from "./packages";
import { Link, useParams } from "react-router-dom";
import request from "../../utils/request";
import {
  Layout,
  Menu,
  Breadcrumb,
  Button,
  Input,
  Row,
  Col,
  Card,
  Divider,
} from "antd";
const { Header, Content, Footer } = Layout;


export default ({initial, project, set_project})=>{

    const [Module, SetModule] = React.useState(null)

    console.log(initial)
    function GetModule(){
        request({method: 'get', url: `api/dashboard/module/${initial.id}/`}, 
        (res)=>{
            SetModule(res.data)
        },
        (err)=>{

        })
    }

    React.useEffect(GetModule, [])

    if (Module === null){
        return null
    }   

    return (
        <Row>
        <Col>
          <div style={{ padding: 24, display: "flex" }}>
            <div
              style={{
                background: "white",
                marginRight: "2%",
                textAlign: "center",
                border: "1px solid black",
              }}
            >
              <Tree project={project} default_module={Module} SetModule={SetModule} />
            </div>
            <div>
              <Editor Module={Module} set_project={set_project} />
            </div>
          </div>
        </Col>
      </Row>
    )
}
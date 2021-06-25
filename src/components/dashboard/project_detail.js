import React from "react";
import Tree from "../tree/tree";
import Editor from "../editor/editor_main";
import Packages from "../editor/packages";
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
import { RollbackOutlined } from '@ant-design/icons';

const { Header, Content, Footer } = Layout;

export default ({ common_ws, logout, user }) => {
  const [Project, SetProject] = React.useState(null);
  const [ShowPackages, SetShowPackages] = React.useState(false);
  let { projectId } = useParams();

  function GetProject() {
    if (Project !== null){
      return
    }
    request(
      { method: "get", url: `api/dashboard/project/${projectId}/` },
      (res) => {
        SetProject(res.data);
      }
    );
  }

  React.useEffect(GetProject);
  if (Project === null) {
    return null
  }

  let InitiaModule = Project.modules[Project.modules.length - 1];

  return (
    <Layout style={{ height: "100%" }}>
      <Header theme='light'
        style={{ position: "fixed", zIndex: 1, width: "100%", padding: 0}}
      >
                    <img
            className='logo'
      src="http://localhost:9000/static/logo.png"
    />
        <Menu
          theme="light"
          mode="horizontal"
          style={{ display: "flex", justifyContent: "end" }}
        >
          <Menu.Item onClick={() => logout()} style={{ fontSize: "1rem" }}>
            Logout
          </Menu.Item>
          <Menu.Item style={{ fontSize: "1rem"}} disabled={true}>
            {user.email}
          </Menu.Item>
        </Menu>
      </Header>
      <Content
        className="site-layout"
        style={{ padding: "0 50px", marginTop: 64 }}
      >
        <Row style={{ marginTop: "2%" }}>
          <Col span={12} offset={6}>
            <div>
            <Button icon={<RollbackOutlined />} type="link" size="large"><Link to="/">All projects</Link></Button>
            <Button type="text" style={{marginRight:'5%'}}><h1>{Project.name}</h1></Button>
              <Button
                type={!ShowPackages ? "danger" : ""}
                onClick={() => {
                  SetShowPackages(false);
                }}
                style={{ marginRight: "5%" }}
              >
                Code
              </Button>
              <Button
                type={ShowPackages ? "danger" : ""}
                onClick={() => {
                  SetShowPackages(true);
                }}
              >
                Packages
              </Button>
            </div>
          </Col>
          <Divider />
        </Row>
        {!ShowPackages ? (
            <Editor initial={InitiaModule} project={Project} set_project={SetProject} />
        ) 
        : 
        (
          <Packages common_ws={common_ws} user={user}/>
        )}
      </Content>
    </Layout>
  );
};

import React from "react";
import request from "../../utils/request";
import Project from "./project";
import ProjectForm from './add_project_form'
import { Layout, Menu, Breadcrumb, Button, Image } from "antd";
import { PlusOutlined } from '@ant-design/icons';

const { Header, Content, Footer } = Layout;


export default ({logout, user}) => {
  const [Projects, SetProjects] = React.useState(null);
  const [ShowForm, SetShowForm] = React.useState(false);


  function GetProjects() {
    request({ method: "get", url: "api/dashboard/project/" }, (res) => {
      SetProjects(res.data);
    });
  }


  React.useEffect(GetProjects, []);

  if (Projects === null) {
    return null;
  }

  return (
    <Layout style={{ height: "100%" }}>
      <Header
        style={{ position: "fixed", zIndex: 1, width: "100%", padding: 0, background: 'white' }}
      >
            <img
            className='logo'
      src="http://localhost:9000/static/logo.png"
    />
        <Menu theme='light' mode="horizontal" style={{display:'flex', justifyContent: 'end'}}>
          <Menu.Item onClick={() => logout()} style={{fontSize: '1rem'}}>
          Logout
          </Menu.Item>
          <Menu.Item style={{fontSize: '1rem'}} disabled={true}>
          {user.email}
          </Menu.Item>
        </Menu>
      </Header>
      <Content
        style={{marginTop: '10%', display: 'flex', justifyContent: 'center' }}
      >
      <ProjectForm
        show={ShowForm}
        setShow={SetShowForm}
      />
        <Button type="primary" size='large' icon={<PlusOutlined />} onClick={()=>SetShowForm(true)}>New poject {Projects.length}/10</Button>
      </Content>
      <Footer style={{background: 'white', paddingBottom: '29%',  background: '#f0f2f5', display: 'flex'}}>

        {Projects.map((value, key) => (
          <Project key={key} project={value} />
        ))}
      </Footer>
    </Layout>
  );
};

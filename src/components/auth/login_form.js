import React from "react";
import { Redirect, Link } from "react-router-dom";
import request from "../../utils/request";
import { Form, Input, Button, Row, Col, Card, Alert, List } from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import "./login.css";

export default function LoginForm({ auth, login }) {
  let [error, setError] = React.useState([]);

  function DoLogin(value) {
    setError([]);
    console.log(value);
    let { password, email } = value;
    console.log(password, email);
    request(
      {
        method: "post",
        url: "api/auth/sign-in/",
        data: { email: email, password: password },
      },
      (res) => {
        localStorage.setItem("token", res.data.token);
        login();
      },
      (err) => {
        console.log(err.response.data.non_field_errors)
        setError(err.response ? err.response.data.non_field_errors : [err.message]);
      }
    );
  }

  if (auth === true) {
    return <Redirect to="/" />;
  }
  console.log(error)
  return (
    <div style={{ height: "100%", overflow: "hidden" }}>
      <Row justify="center" align="space-between" wrap={false}>
        <Col xs={0} sm={0} md={0} lg={6} xl={8}>
          <img src="http://localhost:8000/left.jpg" />
        </Col>
        <Col>
          <Card
            title="Sing in to your account"
            bordered={false}
            style={{ width: 600, marginTop: "40%", textAlign: "center" }}
            headStyle={{
              textAlign: "center",
              fontSize: "2em",
              fontFamily: "Nunito",
            }}
          >
            <Form
              name="normal_login"
              className="login-form"
              onFinish={DoLogin}
              style={{ margin: "auto" }}
            >
              <Form.Item
                name="email"
                rules={[
                  {
                    type: "email",
                    required: true,
                    message: "Please input your Email!",
                  },
                ]}
              >
                <Input
                  prefix={<UserOutlined className="site-form-item-icon" />}
                  placeholder="Email"
                />
              </Form.Item>
              <Form.Item
                name="password"
                rules={[
                  {
                    required: true,
                    message: "Please input your Password!",
                  },
                ]}
              >
                <Input
                  prefix={<LockOutlined className="site-form-item-icon" />}
                  type="password"
                  placeholder="Password"
                />
              </Form.Item>
              <Form.Item>
                <Button
                  type="danger"
                  htmlType="submit"
                  className="login-form-button"
                >
                  Log in
                </Button>
                <Link to="/registration">Or register now!</Link>
              </Form.Item>
              {error.map((e, i)=><Alert message={e} type="error" key={i} />)}
            </Form>
          </Card>
        </Col>
        <Col
          style={{ border: "4px double black" }}
          xs={0}
          sm={0}
          md={0}
          lg={0}
          xl={8}
        >
          <Row justify="center" style={{ height: "100%" }}>
            <Col>
              <Card
                title="Default size card"
                headStyle={{
                  textAlign: "center",
                  fontSize: "2em",
                  fontFamily: "Nunito",
                }}
                bordered={false}
                style={{ marginTop: "30%", width: "80%", textAlign: 'center' }}
              >
                <p>
                  Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed
                </p>
                <p>
                Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed
                </p>
                <p>
                Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed
                </p>
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>
    </div>
  );
}

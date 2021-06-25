import React from "react";
import Tree from "../tree/tree";
import Editor from "../editor/editor";
import Packages from "./packages";
import { Link, useParams } from "react-router-dom";
import request from "../../utils/request";
import { Spin, Button, Input, Table, message, Card } from "antd";

export default ({ common_ws, user }) => {
  const [Packages, SetPackages] = React.useState(null);
  const [Package, SetPackage] = React.useState("");
  const [ShowLoading, SetShowLoading] = React.useState(false);
  const [Size, SetSize] = React.useState(user.packages_size);

  const COLUMNS = [
    {
      title: "Name",
      dataIndex: "name",
    },
    {
      title: "Version",
      dataIndex: "version",
    },
    {
      title: "Added",
      dataIndex: "added",
    },
    {
      title: "",
      dataIndex: "operation",
      render: (pcg) => {
        return (
          <Button
            danger
            onClick={() => {
              request(
                {
                  method: "delete",
                  url: `/api/dashboard/package/${pcg.id}`,
                },
                (res) => {
                  SetPackages(Packages.filter((p) => p.id != pcg.id));
                },
                (err) => {
                  message.error("Something was wrong");
                }
              );
            }}
          >
            Delete
          </Button>
        );
      },
    },
  ];

  function LoadPackages() {
    request({ method: "get", url: "api/dashboard/package/" }, (res) => {
      SetPackages(res.data);
    });
  }

  function InstallPackage() {
    SetShowLoading(true);
    request(
      {
        method: "post",
        url: "api/dashboard/package/",
        data: { name: Package },
      },
      (res) => {},
      (err) => {
        message.error("Something was wrong");
      }
    );
  }

  function ConnectWs() {
    if (Packages === null) {
      return;
    }

    let prev = common_ws.dispatch["add_package"];
    common_ws.dispatch["add_package"] = (res) => {
      if (res.data.success) {
        SetPackages([res.data.package, ...Packages]);
        SetSize(Size + res.data.package.size);
      } else {
        message.error("Something was wrong");
      }
      SetShowLoading(false);
    };

    return () => {
      common_ws.dispatch["add_package"] = prev;
    };
  }

  React.useEffect(LoadPackages, []);
  React.useEffect(ConnectWs);

  if (Packages === null) {
    return null;
  }

  let dataSource = Packages.map((p, key) => {
    return {
      key,
      name: p.name,
      version: p.version,
      added: p.created,
      operation: p,
    };
  });

  return (
    <div style={{ maxWidth: "40%", marginTop: "2%" }}>
      <Card
        title={
          <div style={{ display: "flex", maxWidth: "50%" }}>
            <Input
              addonBefore="pip install"
              onChange={(e) => SetPackage(e.target.value)}
              value={Package}
            />
            <Button onClick={InstallPackage}>install</Button>
            {ShowLoading ? <Spin style={{ marginLeft: "5%" }} /> : ""}
          </div>
        }
      >
        <span style={{ color: "green" }}>Package Storage: {Size} / 250 MB</span>
      </Card>
      <Table columns={COLUMNS} dataSource={dataSource} pagination={false} />
    </div>
  );
};

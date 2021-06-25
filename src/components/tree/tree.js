import React from "react";
import styled from "styled-components";
import File from "./file";
import Folder from "./folder";
import { Button, Popover, Input, message } from "antd";
import request from "../../utils/request";

const StyledTree = styled.div`
  line-height: 2;
`;

const TreeRecursive = ({ data, default_module, set_module }) => {
  // loop through the data
  return data.map((item) => {
    // if its a file render <File />
    if (item.type === "file") {
      return (
        <File
          name={item.name}
          id={item.id}
          selected={item.id === default_module.id}
          set_module={set_module}
        />
      );
    }
    // if its a folder render <Folder />
    if (item.type === "folder") {
      return (
        <Folder name={item.name}>
          {/* Call the <TreeRecursive /> component with the current item.childrens */}
          <TreeRecursive data={item.childrens} />
        </Folder>
      );
    }
  });
};

export default ({ project, default_module, SetModule }) => {
  const [Show, SetShow] = React.useState(false);
  const [Name, SetName] = React.useState("");
  const [Struct, SetStruct] = React.useState(null);

  function AddModule() {
    request(
      {
        method: "post",
        url: "api/dashboard/module/",
        data: { name: Name, project: project.id },
      },
      (res) => {
        let module = res.data;
        SetStruct([
          ...Struct,
          { type: "file", name: module.name, id: module.id },
        ]);
        SetShow(false)
      },
      (err) => {
        message.error("Something was wrong");
        SetShow(false)
      }
    );
  }

  function MakeStruct() {
    let struct = [];
    let modules = project.modules;
    let folders = project.folders;
    for (let i of folders) {
      struct.push({
        type: "folder",
        name: i.name,
        childrens: i.modules.map((m) => {
          return { type: "file", name: m.name, id: m.id };
        }),
      });
    }
    for (let m of modules) {
      struct.push({ type: "file", name: m.name, id: m.id });
    }
    SetStruct(struct);
  }

  React.useState(MakeStruct, []);

  if (Struct === null) {
    return null;
  }

  return (
    <StyledTree>
      <Popover
        content={
          <div>
            <Input onChange={(e) => SetName(e.target.value)} />
            <Button onClick={AddModule}>Module</Button>
          </div>
        }
        title="Name"
        visible={Show}
        onVisibleChange={() => console.log("change")}
      >
        <Button onClick={() => SetShow(!Show)} danger type="link">
          Add+ {project.modules.length}/10
        </Button>
      </Popover>
      <TreeRecursive data={Struct} default_module={default_module} set_module={SetModule} />
    </StyledTree>
  );
};

// const structure = [
//   {
//     type: "folder",
//     name: "src",
//     childrens: [
//           { type: "file", name: "Modal.js" },
//           { type: "file", name: "Modal.css" }
//         ]
//     },
//   { type: "file",
//   name: "package.json" }
// ];

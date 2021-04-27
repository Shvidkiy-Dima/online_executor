import React from 'react'
import styled from "styled-components";
import File from './file'
import Folder from './folder'


const StyledTree = styled.div`
  line-height: 1.5;
`;

const TreeRecursive = ({ data }) => {
    // loop through the data
    return data.map(item => {
      // if its a file render <File />
      if (item.type === "file") {
        return <File name={item.name} id={item.id} />;
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


export default ({ data}) => {
  
    return (
      <StyledTree>
        <TreeRecursive data={data} />
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
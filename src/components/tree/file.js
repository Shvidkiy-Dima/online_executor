import React from 'react'
import styled from "styled-components";
import { AiOutlineFile } from "react-icons/ai";
import FILE_ICONS from './FileIcons'

const StyledFile = styled.div`
  padding-left: 20px;
  display: flex;
  align-items: center;
  span {
    margin-left: 5px;
  }
`;


export default ({ name, id}) => {
    let ext = name.split(".")[1];
  
    return (
      <StyledFile onClick={()=>console.log(id)}>
        {/* render the extension or fallback to generic file icon  */}
        {FILE_ICONS[ext] || <AiOutlineFile />}
        <span>{name}</span>
      </StyledFile>
    );
  };

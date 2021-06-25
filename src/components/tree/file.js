import React from 'react'
import styled from "styled-components";
import { AiOutlineFile } from "react-icons/ai";
import FILE_ICONS from './FileIcons'
import request from '../../utils/request'
import {Button} from 'antd'

const StyledFile = styled.div`
  padding-right: 20px;
  display: flex;
  align-items: center;
  span {
    margin-left: 5px;
  }
`;


export default ({ name, id, selected, set_module}) => {
    let ext = name.split(".")[1];


    function GetModule(id){
      request({method: 'get', url: `api/dashboard/module/${id}/`}, 
      (res)=>{
        set_module(res.data)
      },
      (err)=>{

      })
  }

    return (
      <div style={{background: selected ? '#c8ecf7': '' }}>
      <StyledFile onClick={()=>GetModule(id)}>
        {/* render the extension or fallback to generic file icon  */}
        {FILE_ICONS[ext] || <AiOutlineFile />}
        <Button type='link'>{name}</Button>
      </StyledFile>
      </div> 
    );
  };

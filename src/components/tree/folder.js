import React from 'react'
import styled from "styled-components";
import { AiOutlineFolder } from "react-icons/ai";

const StyledFolder = styled.div`
  padding-left: 20px;

  .folder--label {
    display: flex;
    align-items: center;
    span {
      margin-left: 5px;
    }
  }
`;

const Collapsible = styled.div`
  height: ${p => (p.isOpen ? "auto" : "0")};
  overflow: hidden;
`;


export default ({ name, children }) => {
    const [isOpen, setIsOpen] = React.useState(false);
  
    const handleToggle = e => {
      e.preventDefault();
      setIsOpen(!isOpen);
    };
  
    return (
      <StyledFolder>
        <div className="folder--label" onClick={handleToggle}>
          <AiOutlineFolder />
          <span>{name}</span>
        </div>
        <Collapsible isOpen={isOpen}>{children}</Collapsible>
      </StyledFolder>
    );
  };
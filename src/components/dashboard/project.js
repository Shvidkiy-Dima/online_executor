import React from 'react'
import { Card } from 'antd';
import {
    HashRouter as Router,
    Switch,
    Link,
    Route,
    Redirect,
  } from "react-router-dom"
  

export default ({project}) =>{

    return (

        <div>
            <Link to={`/dashboard/project/${project.id}`}>
            <Card bordered={true} style={{ width: 300 }}>
                <h2>{project.name}</h2>
            </Card>
            </Link>
        </div>
    )

}
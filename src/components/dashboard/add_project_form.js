import React from "react";
import { Popover, Modal, Slider, Form, Input, Alert } from "antd";
import { useHistory } from "react-router-dom";
import request from "../../utils/request"


export default function MonitorForm({ show, setShow }) {
  const [name, setName] = React.useState("");
  const [confirmLoading, setConfirmLoading] = React.useState(false);

  const [NameError, SetNameError] = React.useState('')
  const [CommonErrors, SetCommonErrors] = React.useState([])
  let history = useHistory();

  const handleClose = () => setShow(false);
  const handleOk = () => {
    setConfirmLoading(true);
    let data = {name};
    request(
      { method: "post", url: "api/dashboard/project/", data },
      (res) => {
        history.push(`/dashboard/project/${res.data.id}`);
      },
      (err) => {
        setConfirmLoading(false);
        if (err.response){
          SetNameError(err.response.data.name || '')
          SetCommonErrors(err.response.data.non_field_errors || []) 
        }
 
      }
    );
  };
  return (
      <Modal
        title="Title"
        visible={show}
        onOk={handleOk}
        confirmLoading={confirmLoading}
        onCancel={handleClose}
      >
        <Form>
          <Form.Item>
            Name
            <Input value={name} onChange={(e)=>{setName(e.target.value)}}/>
            {NameError ? <Alert message={NameError} type="error"  />: ""}
          </Form.Item>
          {CommonErrors.map((e, i)=><Alert message={e} type="error" key={i} />)}
        </Form>
      </Modal>
  );
}
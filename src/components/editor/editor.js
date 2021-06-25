import React, { useEffect, useRef, useState } from "react";
import { loader, useMonaco } from "@monaco-editor/react";
import Editor from "@monaco-editor/react";
import _ from "lodash";

import {
  CloseAction,
  createConnection,
  ErrorAction,
  MonacoLanguageClient,
  MonacoServices,
} from "monaco-languageclient";

import { listen } from "vscode-ws-jsonrpc";
import normalizeUrl from "normalize-url";
import ReconnectingWebSocket from "reconnecting-websocket";
import WebSocketConnection from "../../utils/ws";
import { Button, Card, Typography, Popconfirm } from "antd";
import {DeleteOutlined, ApiOutlined} from  '@ant-design/icons';
import request from "../../utils/request";

function createLanguageClient(connection) {
  return new MonacoLanguageClient({
    name: "Sample Language Client",
    clientOptions: {
      // use a language id as a document selector
      documentSelector: ["python"],
      // disable the default error handler
      errorHandler: {
        error: () => ErrorAction.Continue,
        closed: () => CloseAction.DoNotRestart,
      },
    },
    // create a language client connection from the JSON RPC connection on demand
    connectionProvider: {
      get: (errorHandler, closeHandler) => {
        return Promise.resolve(
          createConnection(connection, errorHandler, closeHandler)
        );
      },
    },
  });
}

function createUrl(path) {
  // const protocol = 'ws';

  return normalizeUrl("ws://localhost:3001/python");

  // return normalizeUrl(`${protocol}://${location.host}${location.pathname}${path}`);
}

function createWebSocket(url) {
  const socketOptions = {
    maxReconnectionDelay: 10000,
    minReconnectionDelay: 1000,
    reconnectionDelayGrowFactor: 1.3,
    connectionTimeout: 10000,
    maxRetries: 5,
    debug: false,
  };
  return new ReconnectingWebSocket(url, undefined, socketOptions);
}

function createDependencyProposals(range, data) {
  // returning a static list of proposals, not even looking at the prefix (filtering is done by the Monaco editor),
  // here you could do a server side lookup
  return data.map((p) => {
    return { label: `import ${p.name}`, insertText: `import ${p.name}`, range };
  });
}

let INIT = true

export default ({ Module, set_project, ...props }) => {
  const [Result, SetResult] = React.useState(null);

  const monaco = useMonaco();
  const ws = new WebSocketConnection();

  const handleEditorMounted = (editor, m) => {
    loader.init().then((monacoInstance) => {
      //NEW API FOR Proposal
      if (!INIT){
          return
      }
      request({ url: "api/dashboard/package", method: "get" }, (res) => {
        monacoInstance.languages.registerCompletionItemProvider("python", {
          provideCompletionItems: function (model, position) {
            var word = model.getWordUntilPosition(position);
            var range = {
              startLineNumber: position.lineNumber,
              endLineNumber: position.lineNumber,
              startColumn: word.startColumn,
              endColumn: word.endColumn,
            };
            INIT = false
            return {
              suggestions: createDependencyProposals(range, res.data),
            };
          },
        });
      });
    });
  };

  useEffect(() => {
    if (monaco) {
      MonacoServices.install(monaco.editor);
      const url = createUrl("/sampleSer ver");
      const webSocket = createWebSocket(url);
      ws.connect(`ws/dashboard/module/${Module.id}/`);
      listen({
        webSocket,
        onConnection: (connection) => {
          // create and start the language client
          const languageClient = createLanguageClient(connection);
          const disposable = languageClient.start();
          connection.onClose(() => {
            disposable.dispose();
            console.log("CLOSE!!");
          });
        },
      });
      return () => {
        webSocket.close();
        ws.close();
      };
    }
  }, [monaco]);


  function SendToServer(value, event) {
    ws.send(JSON.stringify({ code: value }));
  }

  function RunModule() {
    request(
      { url: `api/dashboard/module/${Module.id}/run/`, method: "post" },
      (res) => {
        console.log(res.data);
        SetResult(res.data);
      },
      (err) => {}
    );
  }

  function DeleteModule(){
    request({'method': 'delete', url:  `api/dashboard/module/${Module.id}`},
    (res)=>{
      set_project(null)
    },
    (err)=>{

    })
  }

  return (
    <div>
      <div style={{ display: "flex", background: "white"}}>
        <Button icon={<ApiOutlined />} type="primary" danger onClick={RunModule}>
          Run
        </Button>

        <Popconfirm
    title="Are you sure to delete this module?"
    onConfirm={DeleteModule}
    okText="Yes"
    cancelText="No"
  >
            <Button icon={<DeleteOutlined />} type="primary" style={{marginLeft: '1%'}} ghost>
          Delete
        </Button>
    </Popconfirm>
        <Typography.Paragraph
          copyable
          style={{ marginLeft: "5%", marginTop: "1%" }}
        >
          {Module.url}
        </Typography.Paragraph>
      </div>
      <div style={{ display: "flex"}}>
        <Editor
          height="35vmax"
          width="50vmax"
          value={Module.code}
          language="python"
          onMount={handleEditorMounted}
          onChange={SendToServer}
        />
        {Result != null ? (
          <Card title="Output" bordered={true} style={{ width: 300 }}>
            <p>Output:{Result.stdout}</p>
            <p style={{ color: "red" }}>Errors:{Result.stderr}</p>
            <p>Exit code: {Result.exit_code}</p>
          </Card>
        ) : (
          ""
        )}
      </div>
    </div>
  );
};

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
    maxRetries: Infinity,
    debug: false,
  };
  return new ReconnectingWebSocket(url, undefined, socketOptions);
}

export default ({ initialText, ...props }) => {
  let localRef = useRef(null);
  const [value, setValue] = useState(initialText);

  const monaco = useMonaco();

  function createDependencyProposals(range) {
    // returning a static list of proposals, not even looking at the prefix (filtering is done by the Monaco editor),
    // here you could do a server side lookup
    console.log("tuta");
    return [
      {
        label: "import django",
        insertText: "enum ",
        range,
      },
      {
        label: "import restfraemwork",
        insertText: "LALA",
        range,
      },
      {
        label: "import aiohttp",
        insertText: "String",
        range,
      },
      {
        label: "import asyncio",
        insertText: "Da",
        range,
      },
    ];
  }

  const handleEditorMounted = (editor, m) => {
    loader.init().then((monacoInstance) => {
      monacoInstance.languages.registerCompletionItemProvider("python", {
        provideCompletionItems: function (model, position) {
          var word = model.getWordUntilPosition(position);
          var range = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: word.startColumn,
            endColumn: word.endColumn,
          };
          return {
            suggestions: createDependencyProposals(range),
          };
        },
      });
    });
  };

  useEffect(() => {
    if (monaco) {
      console.log("here is the monaco instance:", monaco);
      MonacoServices.install(monaco.editor);
      const url = createUrl("/sampleSer ver");
      const webSocket = createWebSocket(url);
      listen({
        webSocket,
        onConnection: (connection) => {
          // create and start the language client
          const languageClient = createLanguageClient(connection);
          const disposable = languageClient.start();
          connection.onClose(() => disposable.dispose());
        },
      });
      // return () => monaco.editor.dispose();
    }
  }, [monaco]);

  return (
    <Editor
      height="800px"
      width="800px"
      value={initialText}
      language="python"
      onMount={handleEditorMounted}
    />
  );
};

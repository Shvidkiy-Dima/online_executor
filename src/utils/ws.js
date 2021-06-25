
class WebSocketConnection {
  constructor() {
    this.ws = null;
    this.connected = false;
    this.dispatch = {};
  }

  connect(path) {
    if (!this.connected) {
      let token = localStorage.getItem("token");
      //let url = ((window.location.protocol === "https:") ? "wss://" : "ws://") + window.location.host + path + "/?token=" + token;
      let url = ((window.location.protocol === "https:") ? "wss://" : "ws://") + 'localhost:9000/' + path + "?token=" + token;
      console.log(url)
      this.url = url
      this.ws = new WebSocket(url);
      this.ws.onopen = () => {
        this.connected = true;
        console.log("OPEN");
      };
      this.ws.onmessage = (response) => {
        console.log(response, '-----------')
        response = JSON.parse(response.data); 
        let method = this.dispatch[response.method];
        if (method){
          method(response);
        }
      };
      this.ws.onclose = () => {
        console.log("Close!", this.url);
        this.connected = false;
      };
    }
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }

  send(data){
    let count = 0
        function waitForSocketConnection(socket){
            count++
            if (count < 100000) {
                setTimeout(
                    function () {
                        if (socket.readyState === 1) {
                            console.log("Connection is made")
                            socket.send(data)
                        }
                        else {
                            console.log("wait for connection..." + count)
                            waitForSocketConnection(socket);
                        }

                }, 10);
        }
      }
  waitForSocketConnection(this.ws)
}


}

export default WebSocketConnection;

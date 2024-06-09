let DATA;
export const rasp_getData = () => {
  return
	fetch('/print', {
    method: 'POST',
    body: JSON.stringify(DATA), 
    headers: {
      'Content-Type': 'application/json'
    }
  })//.then(response=>response.json().then(out=>console.log(out)));
	return DATA;
};

function receiveData(websocket) {
  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data);
     // (json.dumps({"co2":DATA[0],"temp1":DATA[1],"humidity":DATA[2],"temp2":DATA[3],"altitude":DATA[4]}))
     window.DATA = event
		//console.log(event);
		//terminal_log(event);
  });
}

function connect() {
  window.websocket = new WebSocket("ws://10.8.0.2:8001/"); // <------ CHANGE THIS IP
  receiveData(websocket);
}

window.addEventListener("DOMContentLoaded", () => {
  setInterval(()=>{
    if (window.websocket.readyState != 1) {
      window.websocket.close(); // retry until the connection restablishes
      connect();
    }
  
  },2000);
	
  connect();
	//window.DATA = {"U":[1],"C":[1],"T":[1,2,3,4],"H":[1],"A":[1,2],"P":[1],"R":[1,2,3],"G":[41.58,1.61],"S":[1,2],"D":[1]};
  window.DATA = {"U":["-"],"C":["-"],"T":["-","-","-","-"],"H":["-"],"A":["-","-"],"P":["-"],"R":["-","-","-"],"G":["-","-"],"S":["-","-"],"D":["-"]};
});
import { json_read, json_download, json_instance } from "./json.js";
import { csv_download } from "./csv.js";

let map = L.map('map').setView([41.580344220761255, 1.610345784058587], 15);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let state = {
    t: [],
    x: [41.580344220761255,41.580344220761255,41.580344220761255],
    y: [1.610345784058587,1.610345784058587,1.610345784058587],
    h: [],
    v: []
};
let chords = [];

let CLEAR = document.querySelector("#CLEAR");
CLEAR.addEventListener("click", () => {
    map.eachLayer(function (layer) {
        if (layer instanceof L.Marker || layer instanceof L.Polyline) {
            map.removeLayer(layer);
        }
    });
});


class DataSet{
    label = "";
    borderColor = "#fff";
    data = [];

    getInfo(){
      return 1+Math.random()*1;
    }

    constructor(l,c){
        this.label = l;
        this.borderColor = c;
        this.data = [];
    }
}

let lastMarker;

setInterval(function () {
    for (let i = 0; i < state.x.length; i++) {
        chords[i] = [state.x[i], state.y[i]];
    }

    let lastIdx = state.x.length - 1;
    let lastChord = [state.x[lastIdx], state.y[lastIdx]];

    if (lastMarker) {
        map.removeLayer(lastMarker);
    }

    state.t.push(state.t.length);
    state.x.push(window.global.DATA.G[0])//state.x.push(state.x[lastIdx] + Math.random() * 1);
    state.y.push(window.global.DATA.G[1])//state.y.push(state.y[lastIdx] + Math.random() * 1);
    

    for (let i = chords.length > 5 ? chords.length - 1 : 1; i < chords.length; i++) {
        if (i > 1) {
            let ang = ((chords.length / (2 * Math.PI)) % 1) * 2 * Math.PI;
            let line = L.polyline([chords[i - 1], chords[i]], {
                color: `rgb(${Math.cos(ang - Math.PI) * 255},${Math.cos(ang) * 155},${Math.sin(ang) * 255})`
            }).addTo(map);
        }
    }

    lastMarker = L.marker(lastChord).addTo(map);
    lastMarker.bindPopup('¡Última ubicación!');
}, 1000);

document.getElementById('downloadButtonJSON').addEventListener('click', function () {
    json_download(state);
});

document.getElementById('downloadButtonCSV').addEventListener('click', ()=>{
	let data = {
	    time: state.t,
	    datasets: Object.keys(state).map(key => {
		    if (key === "t") return null;
		    let ds = new DataSet(key, "#fff");
		    ds.data = state[key];
		    return ds;
		}).filter(ds => ds !== null)
	};
	csv_download(data);
});

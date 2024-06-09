import { json_read, json_download, json_instance } from "./json.js";
import { csv_download } from "./csv.js";
import { rasp_getData } from "./ws.js";

const OPTIONS = await json_read("../src/gParams.json");

const canvasElements = Array.from(document.querySelectorAll(".graph"));
const contexts = canvasElements.map(canvas => canvas.getContext("2d"));
let graphs = [];
const colorInputs = document.querySelectorAll("input[type='color']");

class GraphParams {
    constructor(ctx, data, options, type) {
        this.ctx = ctx;
        this.data = data;
        this.options = options;
        this.type = type;
    }
}

const MakeNewGraph = async (cvs, data) => {
    let myChart = echarts.init(cvs);

    let option = await json_read("../src/cParams.json");

    option.yAxis = {
        type: "value",
        min: value => value.min -1
    };

    myChart.setOption(option);

    return myChart;
};

class DataSet {
    constructor(label, borderColor) {
        this.label = label;
        this.borderColor = borderColor;
        this.data = [];
        this.memory = [];
    }

    getInfo(id) {
        try {
            let info = window.DATA[this.label];
            // esto es temporal, no todos los valores los queremos mostrar en un mismo gráfico ya que son muy distintos
            if (this.label == "R") {
                info = [info[0],info[1]]
            }
            if (this.label == "T") {
                info = [info[0],info[1]]
            }
            if (this.label == "A") {
                info = [info[0]]
            }
            if (this.label == "C") {
                info = [info[0]]
            }
            if (this.label == "H") {
                info = [info[0]]
            }
            if (this.label == "P") {
                info = [info[0]]
            }

            window.parent.connScreen.style.visibility = "hidden";

            return info == "-" ? null : info; //Conect makes the error
        } catch (error) {
            window.parent.connScreen.style.visibility = "visible";

            console.error(error);
            return 0;
        }
    }
}

class DataManager {
    static time = [];
    static datasets = [];
    static memory = [];
    static checkboxes = [];

    static async main() {
        DataManager.clearGraphs();

        DataManager.datasets = contexts.map((ctx, index) => new DataSet(canvasElements[index].id, "#f00"));

        DataManager.checkboxes = document.querySelectorAll(".selection");

        for (let i = 0; i < contexts.length; i++) {
            graphs[i] = await MakeNewGraph(canvasElements[i]);
        }
    }

    static update(t) {
        DataManager.time.push(DataManager.time.length);

        for (let i = 0; i < contexts.length; i++) {
            const info = DataManager.datasets[i].getInfo(DataManager.datasets[i].label);
            DataManager.datasets[i].data.push(info);
            DataManager.memory[i].push(info);

            if (DataManager.datasets[i].data.length >= OPTIONS.scales.x.ticks.max) {
                DataManager.datasets[i].data = DataManager.datasets[i].data.filter((value, index) => index % 2 === 0);
            }

            DataManager.datasets[i].borderColor = colorInputs[DataManager.datasets.indexOf(DataManager.datasets[i])].value;

            let col = DataManager.datasets[i].borderColor;
            let gradient = [];

            let xAxisData = graphs[i].getOption().xAxis[0].data;
            let seriesData = graphs[i].getOption().series[0].data;

            let now = new Date();
            xAxisData.push(now.toLocaleTimeString());
            seriesData = DataManager.datasets[i].data;

            let option = document.querySelectorAll('.gOptions');

            let sers = [];
            for(let j = 0; j < seriesData[0].length; j++){
                if(t==1){
                    DataManager.checkboxes[i].innerHTML+=`<input type="checkbox" id="${"id_"+i+"_"+j}" checked="true">${j}</input>`;
                }

                if(t>=1){
                    let check = document.querySelector(`#${"id_"+i+"_"+j}`);
                    if(!check.checked)
                        continue;
                    gradient[j] = col;
                    sers.push({
                        data: seriesData.map(s=>s[j]), //+raondom() para offlinemode
                        name:j,
                        type: 'line',
                        smooth: false,
                        areaStyle: {
                            color: gradient[j]+`${99-(j+5)*10<0?"22":(j+5)*10}`
                        }
                    });
                }
            }

            graphs[i].setOption({
                xAxis: {
                    data: xAxisData
                },
                series: sers,
                color: gradient
            });
        }
    }

    static clearGraphs() {
        graphs = [];
    }
}

await DataManager.main();
for (let i = 0; i < contexts.length; i++) {
    DataManager.memory[i] = [];
}

let TIME = 0; //cutre start()
setInterval(() => {
    TIME++;
    DataManager.update(TIME);
}, 500);

document.getElementById('CLEAR').addEventListener("click", () => DataManager.main());

document.getElementById('downloadButtonJSON').addEventListener('click', () => {
    const exportData = {
    time: DataManager.time,
    datasets: DataManager.memory.map(mem => ({
        label: DataManager.datasets[DataManager.memory.indexOf(mem)].label,
        data: mem
    }))
};

    json_download(exportData);
});

document.getElementById('downloadButtonCSV').addEventListener('click', () => csv_download(DataManager)); //las columnas y sus titulos estan desfasados porque hay columnas mas anchas que otrasy este cambio de momento se tiene que hacer manual...
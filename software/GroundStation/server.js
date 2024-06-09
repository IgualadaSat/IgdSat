import express from 'express';
import path from 'path';
import open from 'open';
import fs from 'fs';
//import { Terminal } from "./server/terminal.js";
//import { Rasp } from "./server/rasp.js";

const app = express();
const port = 3000;

const __filename = new URL(import.meta.url).pathname;
const __dirname = path.dirname(__filename);

app.use(express.static(path.join(__dirname, 'dist/public/')));
app.use(express.json());

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist/public/', 'index.html'));
});

app.post("/terminal", (req, res) => {
  res.json(Terminal.msgs);
});

app.post("/print", (req, res) => {
  const data = req.body;
  Terminal.msgs.push(JSON.stringify(data));
  res.json(data);
});
app.post('/connex', (req, res) => {
  let input = req.body.text;
  let output = Rasp.connect(input);
  Terminal.msgs[Terminal.msgs.length] = output.text;
  if(input == "clear")
    Terminal.msgs = [];
  console.log("rasp: ",output.text);
  res.json(output); 
});

app.listen(port, () => {
  console.log(`Servidor escuchando en http://localhost:${port}`);
  open("http://localhost:"+port,"","width=1280,height=720")
});

app.get('/modify', (req, res) => {
  const datos = req.query;
  console.log('Datos recibidos:', datos);
  const filePath = path.join(__dirname, './dist/public/storage/prueva.json');
  console.log('Ruta del archivo:', filePath);
  fs.writeFile(filePath, JSON.stringify(data, null, 2), (err) => {
    if (err) {
      console.error('Error al escribir en el archivo:', err);
      res.status(500).send('Error interno del servidor');
    } else {
      console.log('Datos escritos en el archivo correctamente.');
      res.status(200).send('Datos escritos en el archivo correctamente');
    }
  });

  console.log(JSON.stringify(datos));
});

import { Connex } from "./connex.js";

class Terminal{
  static content = document.querySelector("#command-line").value;
  static terminal = document.querySelector("#terminal");
  static lines = [];

  static update(){
    Terminal.content = document.querySelector("#command-line").value;
    Connex.msg = {text:Terminal.content};
    Connex.conect();
  }
  static recive(){
    Terminal.terminal.innerHTML = "";

    fetch('/terminal', {
      method: 'POST'
    }).then(response => {
      response.json().then(out => {
        Terminal.lines = out;
      })
    }).catch(error => console.error('Error al enviar el texto:', error));

    for(let i = Terminal.lines.length-1;i > 0;i--){
      Terminal.terminal.innerHTML += "~$ "+Terminal.lines[i]+"\n";
    }
  }
}

let button = document.querySelector("#submit");
button.addEventListener("click",()=>{
  Terminal.update();
});
document.addEventListener("keydown",(key)=>{
  key.key=="Enter"?Terminal.update():0;
});

//setInterval(()=>{Terminal.recive()},16);
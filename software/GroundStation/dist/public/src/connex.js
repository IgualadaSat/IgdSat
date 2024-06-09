export class Connex{
  static msg = {text:""};
  static conect(){
    fetch('/connex', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(Connex.msg)
    }).then(response => {
      response.json().then(out => {
        console.log("rasp: ",out.text);
      })
    }).catch(error => console.error('Error al enviar el texto:', error));
  }
} 
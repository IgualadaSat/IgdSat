import { Client } from 'ssh2';

export class Rasp {
	static host = "192.168.222.105";
	static port = 22;
	static username = "igdsat";
	static password = ".";

	static r = "conectando...";

	static connect(msg) {
		Rasp.network(msg);
		return {text:Rasp.r};
	}
	static network(msg){
		const conn = new Client();
		conn.on('ready', () => {
		  console.log("conectado!");
		  Rasp.r = "conectado, sin output";
		  conn.exec(msg, (err, stream) => {
		    if (err) {
		      conn.end();
		      Rasp.r = err.toString();
			  stream.end();
		    }
		    let result = 'no hay respuesta';
		    stream.on('data', (data) => {
		      result = data.data.toString();
		    });
		    stream.on('end', () => {
		      conn.end();
		      Rasp.r = result;
		    });
		  });
		});
		conn.on('error', (err) => {
		  conn.end();
		  Rasp.r = err.toString();
		});
		conn.connect(Rasp);
	}
}
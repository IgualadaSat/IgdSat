export async function json_read(pack) {
    const json = pack;
    try {
        const respuesta = await fetch(json);
        if (!respuesta.ok) {
            console.error('Error al cargar el archivo JSON');
            return "";
        }
        const datosJSON = await respuesta.text();
        const datos = JSON.parse(datosJSON);
        return datos;
    } catch (error) {
        console.error('Error al leer el archivo JSON:', error);
        return "";
    }
}

export function json_download(datos){
    const jsonString = JSON.stringify(datos, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'datos.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

export async function json_instance(datos){
    const params = new URLSearchParams();
    for (const key in datos) {
        params.append(key, datos[key]);
    }
    const queryString = params.toString();

    await fetch(`/modify?${queryString}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });
}
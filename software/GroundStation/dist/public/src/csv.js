function dataToCSV(obj) {
    let headers = obj.datasets.map(d=>d.label);
    headers.unshift("time");
    const rows = [headers.join(',')];

    for (let i = 0; i < obj.time.length; i++) {
        const row = [obj.time[i]].concat(obj.memory.map(mem => mem[i]));
        rows.push(row.join(','));
    }

    return rows.join('\n');
}

export function csv_download(obj){
	const csvContent = "data:text/csv;charset=utf-8," + dataToCSV(obj);

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "datos.csv");
    document.body.appendChild(link);

    link.click();
    document.body.removeChild(link);
}
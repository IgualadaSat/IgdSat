let body = document.querySelector("body");
body.addEventListener("click",()=>{	
	let iframe = document.querySelector("iframe");
	iframe.src = `${Header.windows[Header.windowid].innerHTML}.html`;
});
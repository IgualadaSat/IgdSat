//---------------------------------------------------------------THEME
document.lm = false;

const LIGHTMODE = () => {
	applyModeToFrames(document, "lightmode");
	document.lm = true;
};

const DARKMODE = () => {
	applyModeToFrames(document, "darkmode");
	document.lm = false;
};

function applyModeToFrames(doc, modeClass) {
    let all = doc.querySelectorAll("*");
    all.forEach(element => {
    	applyMode(element, modeClass);
    });
   
    const iframes = doc.querySelectorAll("iframe");

    iframes.forEach(iframe => {
        try {
            const iframeDocument = iframe.contentDocument || iframe.contentWindow.document;
            if(modeClass == "lightmode")
            	iframeDocument.lm = true;
           	else
           		iframeDocument.lm = false;
            applyModeToFrames(iframeDocument, modeClass);
        } catch (error) {
            console.error("Error al acceder al contenido del iframe:", error);
        }
    });
}

function applyMode(element, modeClass) {
    element.classList.remove("darkmode", "lightmode");
    element.classList.add(modeClass);
}

document.lm?LIGHTMODE():DARKMODE();

//----------------------------------------------------------------SOUNDS

function playSound(src) {
    const sound = new Audio(src);
    sound.volume = 0.3;
    sound.play();
}

function addSoundEventListenersToButtonsAndLinks(doc) {
    const buttonsAndLinks = doc.querySelectorAll("button, a, .windows, input");

    buttonsAndLinks.forEach(element => {
        element.addEventListener("mouseenter", ()=>{playSound('../storage/hover.mp3')});
        element.addEventListener("click", ()=>{playSound('../storage/click.mp3')});
    });

    const iframes = doc.querySelectorAll("iframe");

    iframes.forEach(iframe => {
        try {
            const iframeDocument = iframe.contentDocument || iframe.contentWindow.document;
            addSoundEventListenersToButtonsAndLinks(iframeDocument);
        } catch (error) {
            console.error("Error al acceder al contenido del iframe:", error);
        }
    });
}

addSoundEventListenersToButtonsAndLinks(document);

//----------------------------------------------------------------HEATHERS

class Header {
	static windows = document.querySelectorAll('.window');
	static windowid = 0;

	static main(){
		if(Header.windows.length > 0){
			let header = document.querySelectorAll('header');
			let numWindows = document.querySelectorAll('header .window').length;
			header[0].style.gridTemplateColumns = `repeat(${numWindows}, 1fr)`;

			for(let i = 0;i < Header.windows.length;i++){
				Header.windows[i].addEventListener("click",()=>{
					Header.windowid = i;
				});
			}
		}
	}

	static update(){
		if(Header.windows.length > 0){
			for(let i = 0;i < Header.windows.length;i++){
				Header.windows[i].style.display = "block";
				Header.windows[i].style.paddingLeft = "10px";
				Header.windows[i].style.height = "calc(100% - 4px)";
				Header.windows[i].style.borderTop = "4px solid #0000";
				Header.windows[i].style.background = "#fff0";
			}
			Header.windows[Header.windowid].style.borderTop = "4px solid #0ffa";
			Header.windows[Header.windowid].style.background = document.lm?"#0005":"#fff2";
		}
	}
}

Header.main();
setInterval(()=>{
	Header.update();
},10);

if(document.querySelectorAll("textarea") != null){
	document.querySelectorAll("textarea").forEach(ta => {
		ta.spellcheck = false;
	});
}

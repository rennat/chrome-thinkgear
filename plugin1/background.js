'use strict';

var ports = [],
	ws = null;


console.debug('background starting');


function connect() {
	console.debug('connecting...');
	ws = new WebSocket("ws://localhost:8080");
	ws.addEventListener('open', function (e) {
		console.debug('connection opened');
		sendEvent({type: "open.thinkgear"});
	});
	ws.addEventListener('close', function (e) {
		if (ports.length > 0) {
			console.debug('connection lost... retrying in 1s');
			sendEvent({type: "close.thinkgear"});
			setTimeout(connect, 1);
		} else {
			ws = null;
		}
	});
	ws.addEventListener('message', function (e) {
		e.data.type = "message.thinkgear";
		sendEvent({type: "message.thinkgear", data: e.data});
	});
}


function sendEvent(eventObject) {
	var i;
	for (i=0;i<ports.length;++i) {
		ports[i].postMessage(eventObject);
	}
}


chrome.runtime.onConnect.addListener(function (port) {
	console.debug('new port opened');
	ports.push(port);
	port.onDisconnect.addListener(handleDisconnect);
	if (ports.length > 0 && ws === null) {
		connect();
	}
});


function handleDisconnect(port) {
	console.debug('port closed');
	ports = ports.filter(function (x) {
		return x !== port;
	});
	if (ports.length === 0 && ws !== null) {
		ws.close();
	}
}

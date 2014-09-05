'use strict';


var port;


function initConnection() {
	console.debug('content connecting');
	port = chrome.runtime.connect();
	port.onMessage.addListener(function (request, sender, sendResponse) {
		console.debug('content message');
		window.postMessage({
			type: 'thinkgear',
			data: request
		}, "*");
	});
}



if (typeof(document.querySelector('html').dataset.thinkgear) !== 'undefined') {
	initConnection();
}

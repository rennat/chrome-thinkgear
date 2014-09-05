#!/usr/bin/env python

import os
import sys
import time
import json
import threading
import re
import subprocess

import mindwave
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer


# TODO: This is the ID of my MindWave (model MW001), get IDs or pattern 
#       for all MindWave devices.
SERIAL_PORT = os.path.realpath('/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0')


class ConnectionMonitor(threading.Thread):
	
	def __init__(self, headset, *args, **kwargs):
		self.headset = headset
		super(ConnectionMonitor, self).__init__(*args, **kwargs)
	
	def run(self):
		print('connection monitor started')
		while True:
			time.sleep(1)
			if self.headset.status == 'connected':
				continue
			print('connecting to headset...')
			self.headset.connect()


class ThinkGearWebSocket(WebSocket):
	
	def handleConnected(self):
		print("client connected")
		headset.waves_handlers.append(self.handle_waves)
		headset.attention_handlers.append(self.handle_attention)
		headset.meditation_handlers.append(self.handle_meditation)
		headset.poor_signal_handlers.append(self.handle_poor_signal)
		headset.good_signal_handlers.append(self.handle_good_signal)
	
	def handleClose(self):
		print("client disconnected")
		headset.waves_handlers.remove(self.handle_waves)
		headset.attention_handlers.remove(self.handle_attention)
		headset.meditation_handlers.remove(self.handle_meditation)
		headset.poor_signal_handlers.remove(self.handle_poor_signal)
		headset.good_signal_handlers.remove(self.handle_good_signal)
	
	def handle_waves(self, headset, waves):
		self.sendMessage(json.dumps(waves))
	
	def handle_attention(self, headset, attention):
		self.sendMessage(json.dumps({'attention': attention}))
	
	def handle_meditation(self, headset, meditation):
		self.sendMessage(json.dumps({'meditation': meditation}))

	def handle_poor_signal(self, headset, poor_signal):
		self.sendMessage(json.dumps({'poor_signal': poor_signal}))

	def handle_good_signal(self, headset, good_signal):
		self.sendMessage(json.dumps({'good_signal': good_signal}))


def msg_handler(message):
	def _f(*args):
		print(message, args)
	return _f


def waves_handler(headset, waves):
	print(waves)


if not os.path.exists(SERIAL_PORT):
	print('No USB dongle found')
	sys.exit(1)
headset = mindwave.Headset(SERIAL_PORT)


headset.headset_connected_handlers.append(msg_handler('headset connected'))
headset.headset_disconnected_handlers.append(msg_handler('headset disconnected'))
headset.headset_notfound_handlers.append(msg_handler('headset notfound'))
headset.scanning_handlers.append(msg_handler('headset scanning'))
headset.standby_handlers.append(msg_handler('headset standby'))
headset.request_denied_handlers.append(msg_handler('headset request_denied'))


monitor = ConnectionMonitor(headset)
monitor.daemon = True
monitor.start()


try:
	server = SimpleWebSocketServer('', 8080, ThinkGearWebSocket)
	server.serveforever()
except KeyboardInterrupt:
	pass
except Exception, e:
	headset.disconnect()
	headset.serial_close()
	raise e
finally:
	print('bye!')
	headset.disconnect()
	headset.serial_close()

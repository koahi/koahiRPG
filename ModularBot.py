import plugins
import threading

import logging

import sleekxmpp
from sleekxmpp.exceptions import *

import inspect
import sys
import os
import time
import ssl
import random

from plugins.runtime import runtime
from plugins.expruntime import expruntime

elapsed = 0
start = 0

class ModularBot(sleekxmpp.ClientXMPP):
	def __init__(self,jid,password,nick,channel,excluded,server,admins,bot_id,plugin_status={}):
		print "jid is "+str(jid)
		print "password is "+str(password)
		print "channel is "+str(channel)
		sleekxmpp.ClientXMPP.__init__(self, jid, password)
		self.jid_note = jid
		self.password = password
		self.nick = nick
		self.channel = channel
		
		
		self.bot_id=bot_id
		
		self.admins=admins
		
		self.lock=threading.Lock()
		self.messagables={}
		
		self.trackables={}
		
		self.ignored_names=excluded
		
		self.jidList={}
		
		self.plugin_status=plugin_status
		
		self.load_modules()
		
		self.add_event_handler("groupchat_presence", self.updateJIDs)
		self.add_event_handler("session_start", self.start)
		self.add_event_handler("message", self.msg_handler)
		self.add_event_handler("presence_unavailable", self.removeJID)
		
		self.scheduler.add("Tracking",0.1,self.track_handler,repeat=True)
		
		runtime(self).start()
		expruntime(self).start()
		
		
	def updateJIDs(self,msg):
		nick=str(msg["from"]).split("/")[1]
		if msg["type"]!="unavailable":
			if not msg["mucnick"] in self.jidList.keys() and not msg["muc"]["jid"].bare in self.jidList.values() and msg["mucnick"] != "rpgbot":
				self.jidList[nick]=str(msg["muc"]["jid"].bare)
				print(nick + " " + msg["type"])

	def removeJID(self,msg):
		nick=str(msg["from"]).split("/")[1]
		if nick in self.jidList.keys():
			self.jidList.pop(nick)
			print(nick + " " + msg["type"])
		
	def load_modules(self):
		
		for i in plugins.classDictionary:
			real_thing=plugins.classDictionary[i](self)
			
			if "All" in self.plugin_status.keys():
				real_thing.active=self.plugin_status["All"]
			
			if i in self.plugin_status.keys():
				real_thing.active=self.plugin_status[i]
			
			if real_thing.messagable:
				self.messagables[i.lower()]=real_thing
			if real_thing.trackable:
				self.trackables[i.lower()]=real_thing
		
	def start(self,arg):
		self.send_presence()
		r=self.get_roster()
		self.plugin['xep_0045'].joinMUC(self.channel, self.nick, wait=False)

		
	def list_plugins(self):
		s="\n"
		for i in plugins.classDictionary:
			s+=i+"\n"
		return s
		
	def msg_handler(self,msg):
		
		admin=False
		if str(msg["from"].bare).lower() in self.admins:
			admin=True
			if msg["body"].lower().startswith("!enable"):
				self.toggle(msg["mucnick"],msg["body"][8:].lower(),True)
				self.channel_message(msg["body"][8:]+" enabled!")
			if msg["body"].lower().startswith("!disable"):
				self.toggle(msg["mucnick"],msg["body"][9:].lower(),False)
				self.channel_message(msg["body"][9:]+" disabled!")
				
			if msg["body"].lower().startswith("!help"):
				self.private_message(msg["from"],self.help(admin))
			
			if msg["body"].lower().startswith("!plugins"):
				self.private_message(msg["from"],self.list_plugins())
				
			if msg["body"].lower().startswith("!ignore"):
				self.ignore_toggle(msg["body"],True)
			
			if msg["body"].lower().startswith("!unignore"):
				self.ignore_toggle(msg["body"],False)
					
		if msg["body"].lower().startswith("!help"):
			self.private_message(msg["from"],self.help(False))
		
		if msg["type"]=="groupchat":
			ignored=msg["mucnick"].lower() in self.ignored_names
		else:
			ignored=False
		
		for i in self.messagables:
			messagable=self.messagables[i]
			if messagable.active:
				messagable.message(msg,admin,ignored)
				
	def ignore_toggle(self,s,status):
		s=s.split(" ")
		name=s[1].lower()
		if status:
			self.channel_message(name+" is now being ignored!")
			self.ignored_names.append(name)
		else:
			self.channel_message(name+" is no longer being ignored!") 
			self.ignored_names.remove(name)
		
	def help(self,admin):
		s="\n"
		if admin:
			s+="ADMIN ONLY COMMANDS\n"
			s+="!enable [plugin name] - enables a plugin\n"
			s+="!disable [plugin name] - disables a plugin\n"
			s+="!plugins - list all loaded plugins\n"
			s+="!ignore - ignore a specific user by nickname\n"
			s+="!unignore - unignore a specific user by nickname\n"
		for i in self.messagables.keys():
			s+=self.messagables[i].help(admin)
		return s
			
	def track_handler(self):
		for i in self.trackables:
			trackable=self.trackables[i]
			try:
				if trackable.active:
					trackable.track()
			except:
				pass
		
	def toggle(self,admin,name,toggle):
		b_1=b_2=toggle
		
		if name in self.messagables:
			b_1=self.messagables[name].active
			self.messagables[name].active=toggle
				
		if name in self.trackables:
			b_2=self.trackables[name].active
			self.trackables[name].active=toggle
		
		if not b_1 and not b_2 and toggle:
			self.channel_message(admin+" enabled "+name+"!")
		elif b_1 and b_2 and not toggle:
			self.channel_message(admin+" disabled "+name+"!")
				
	def channel_message(self,content):
		self.send_message(mto=self.channel,mbody=content, mtype="groupchat")
		
	def private_message(self,user,content):
		self.send_message(mto=user,mbody=content,mtype="chat")

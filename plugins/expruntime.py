import random
import time
import sleekxmpp
import threading
				
class expruntime(threading.Thread):

	def help(self,admin):
		return ""	
		
	def message(self,msg,admin,ignored):
		if self.active and str(msg["mucnick"]) != u"": # This should really say "if self.active and msg['mucnick'])"
			self.commands(msg,admin,ignored)
	
	def commands(self, msg, admin, ignored):
		return ""
		
	def __init__(self, parent):	
		self.parent=parent
		self.messagable=True
		self.trackable=True
		
		self.active=False
		threading.Thread.__init__(self)
		
	def run (self):
		while True:
			interval = random.randint(60, 60)
			self.parent.trackables["main"].timed_exp_gain()
			time.sleep(60)
			self.parent.trackables["main"].effects_decay()
			time.sleep(60)
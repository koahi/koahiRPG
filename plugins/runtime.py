import random
from random import choice
import os
import sys
import time
import sleekxmpp
import threading

class runtime(threading.Thread):

	def help(self,admin):
		return ""	
		
	def message(self,msg,admin,ignored):
		if self.active and str(msg["mucnick"])!=u"":
			self.commands(msg,admin,ignored)
	
	def commands(self,msg,admin,ignored):
		return ""
		
	def __init__(self, parent):	
		self.parent=parent
		self.messagable=True
		self.trackable=True
		
		self.active=False
		threading.Thread.__init__(self)
		
	def run (self):
		count = 0
		while (count >= 0):
			interval = random.randint(10, 30)
			time.sleep(int(interval))
			roll = random.randint(1,10)
			print("Counter: "+str(count)+" Roll: " +str(roll))
			count = count + 1
			if roll <= 5 and len(self.parent.jidList) >= 2:
				print "Combat Count"
				self.parent.trackables["main"].combatset()
			elif roll == 9:
				print "Effects Count"
				self.parent.trackables["main"].timed_effects_gain()
			elif roll == 10:
				print "Weapon Count"
				self.parent.trackables["main"].timed_weapon_gain()
			else:
				print "NOTHING HAPPENS!"
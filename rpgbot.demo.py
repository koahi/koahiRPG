# TEST GENERAL

from ModularBot import ModularBot
import logging
import ssl


jid="JID here"
password="password"

nick="bot's nickname in MUC"

channel="testing channel"

excluded=["people you want bot to ignore although I'm 95 percent sure this doesn't work"]

server="jabber server"

admins="your jid probably"

port=5222

plugin_status={"main":True,
			   "runtime":True,
			   "expruntime":True,
			   "All":False}

		
if __name__=="__main__":
	logging.basicConfig(format='%(levelname)-8s %(message)s')		
			
	mb=ModularBot(jid,password,nick,channel,excluded,server,admins,"AutoKoahi",plugin_status)
	mb.register_plugin('xep_0030')	 # Service discovery.
	mb.register_plugin('xep_0045')	 # MUC support.
	mb.register_plugin('xep_0199')	 # XMPP Ping
	mb.ssl_version = ssl.PROTOCOL_SSLv3

	if mb.connect((server,port)):
		print "Attempting to connect"
		mb.process(block=True)
	else:
		print "Failed to connect."
		exit()
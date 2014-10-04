from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
	routing_table = {}
	def __init__(self):
		# Add your code here!
		create(DVRouter, "dv")
		routing_table[self] = {self, 0}

	def handle_rx (self, packet, port):
		# Add your code here!
		if isinstance(packet, RoutingUpdate):
			pass
		elif isinstance(packet, DiscoveryPacket):
			pass
		elif isinstance(packet, Packet):
			pass
		else
			pass


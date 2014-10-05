from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
	def __init__(self):
		# Add your code here!
		self.routing_table[self] = {self:(0, 0)}

	def handle_rx (self, packet, port):
		# Add your code here!
		if isinstance(packet, RoutingUpdate):
      update_routing_table(packet)
			send_update()
		elif isinstance(packet, DiscoveryPacket):
			self.routing_table[self][packet.src] = (1, port)
		elif isinstance(packet, Packet):
			next_dest = next_hop(packet.dst)
			self.send(packet, next_dest)
		else:
			pass

  def update_routing_table (self, update):
		pass

	def next_hop (self, dest):
		return self

	def send_update(self):
		pass

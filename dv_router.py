from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
	def __init__(self):
		# Add your code here!
		self.routing_table= {}
		self.ip_to_port={}
		self.routing_table[self] = {self:(0, 0)} #dst->(distance, switch)
		self.ip_to_port[self] = (None, 0)  #switch->(port number, distance)

	def handle_rx (self, packet, port):
		# Add your code here!
		if isinstance(packet, RoutingUpdate):
			update_routing_table(packet,port)
			send_update()
		elif isinstance(packet, DiscoveryPacket):
			self.routing_table[self][packet.src] = (1, packet.src)
			if(packet.is_link_up):
				self.ip_to_port[packet.src]=(port,packet.latency)
			else:
				self.ip_to_port[packet.src]=(port,None) #didn't use a really high number. 
				
			update_routing_table(packet,port)
		elif isinstance(packet, Packet):
			next_dest = next_hop(packet)
			self.send(packet, next_dest)
		else:
			pass

  def update_routing_table (self, packet, port):
		keys = packet.all_dests()
		for key in keys:
			new_dist = get_distance(key) + self.routing_table[packet.src][key][0]
			current_ip = self.routing_table[packet.src][key]
			if (packet.src is current_ip[1] and new_dist < current_ip[0]) or (packet.src is not current_ip[1]):
				current_ip = (new_dist, packet.src)

	def next_hop (self, packet):
		result=self.routing_table[self][packet.dst]
		if result:
			return result[1] # this is the port
		return nil 

	def send_update(self):
		pass

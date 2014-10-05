from sim.api import *
from sim.basics import *
import pdb

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
			self.update_routing_table(packet,port)
			send_update()

		elif isinstance(packet, DiscoveryPacket):
			self.routing_table[self][packet.src] = (1, packet.src)
			state=""
			if(packet.is_link_up):
				state="Added "
				self.ip_to_port[packet.src]=(port,packet.latency)
			else:
				state="Removed "
				self.ip_to_port[packet.src]=(port,None) #didn't use a really high number. 
				self.clean(packet.src)

			print state, packet.src, " to ", self , " table"

		elif isinstance(packet, Packet):
			port = port_for_packet(packet)
			self.send(packet, port)
		else:
			pdb.set_trace() #TODO:REMOVE. enter debugging if its not any packet
			pass


  	def update_routing_table (self, packet, port):

		pass

	def port_for_packet(self, packet):
		route=self.routing_table[self][packet.dst]
		port=self.ip_to_port(route[1])[0]
		return port


	def send_update(self):

		pass

	def clean(self, switch):
		for k,v in self.routing_table[self]:
			if v[1]==switch:
				self.routing_table[self][k]=(None,None)
				self.calculate(self,k)
		

	def calculate(self,src,dest):
		pass



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
			#send_update()

		elif isinstance(packet, DiscoveryPacket):
			self.routing_table[self][packet.src] = (1, packet.src)
			state=""
			if(packet.is_link_up):
				state="Added "
				self.ip_to_port[packet.src]=(port,packet.latency)
				self.send_update(packet.src,packet.latency,port)
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
		keys = packet.all_dests()
		for key in keys:
			new_dist = packet.get_distance(key) + self.routing_table[packet.src][key][0]
			current_ip = self.routing_table[packet.src][key]
			if packet.src is current_ip[1]: # if the sources are the same, then something along the path changed
				current_ip = (new_dist, packet.src)
			elif packet.src is not current_ip[1] and new_dist < current_ip[0]: # if the sources are different, then this becomes a choice between new path or current path
				current_ip = (new_dist, packet.src)
				self.ip_to_port[key] = port #also update the ip_to_port table to reflect the new port that should be used.

	def port_for_packet(self, packet):
		route=self.routing_table[self][packet.dst]
		port=self.ip_to_port(route[1])[0]
		return port


	def send_update(self,dst,distance,port):
		p=RoutingUpdate()
		p.add_destination(dst, distance)
		self.send(p,port, True)

	def clean(self, switch):
		del self.routing_table[switch]
		for k,v in self.routing_table[self]:
			if v[1]==switch:
				self.routing_table[self][k]=(None,None)
				self.calculate(self,k)
		
	def calculate(self,src,dst):
		print "calculate ", src," ", dst
		return
		newEntry=(10000000000000,None)
		for k,v in self.routing_table:   #check each connected component
			if dst in v.keys():
				new_distance=v[dst][0]+self.ip_to_port[k][1]
				if new_distance<newEntry[0]:
					newEntry=(new_distance,k)
		if newEntry[1]==None:
			return None		
		return newEntry

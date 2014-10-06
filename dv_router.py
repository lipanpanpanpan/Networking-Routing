from sim.api import *
from sim.basics import *
import pdb
import pprint
pp = pprint.PrettyPrinter(indent=4)


'''
Create your distance vector router in this file.
'''


infinity=1000

class DVRouter (Entity):
	def __init__(self):
		# Add your code here!
		self.routing_table= {}
		self.ip_to_port={}
		self.routing_table[self] = {self:(0, 0)} #dst->(distance, switch)
		self.ip_to_port[self] = (None, 0)  #switch->(port number, distance)
		self.delay = 4

	def handle_rx (self, packet, port):
		# Add your code here!
		if isinstance(packet, RoutingUpdate):
			if self.update_routing_table(packet,port):
				self.send_table(port)

		elif isinstance(packet, DiscoveryPacket):
			self.routing_table[self][packet.src] = (packet.latency, packet.src)
			state=""
			if(packet.is_link_up):
				state="Added "
				self.ip_to_port[packet.src]=(port,packet.latency)
				self.send_update(packet.src,packet.latency,port)
			else:
				state="Removed "
				self.ip_to_port[packet.src]=(port,infinity)
				self.clean(packet.src)

			print state, packet.src, " to ", self , " table"

		elif isinstance(packet, Packet):
			port = self.port_for_packet(packet)
			self.send(packet, port)
		else:
			pdb.set_trace() #TODO:REMOVE. enter debugging if its not any packet
			pass


	def update_routing_table (self, packet, port):
		keys = packet.all_dests()
		if packet.src not in self.routing_table.keys():
			self.routing_table[packet.src]={}
		for key in keys:
			self.routing_table[packet.src][key]=(packet.get_distance(key),None)

		changed = False
		for key in keys:
			new_dist = packet.get_distance(key) + self.ip_to_port[packet.src][1]
			if key not in self.routing_table[self]:
				self.routing_table[self][key] = (new_dist,packet.src)
				print "NEW", self, "->", key, "=", new_dist
				changed = True
			else:
				r=self.routing_table[self][key]
				if packet.src is r[1] and r[0]!=new_dist: # if the sources are the same & changed then update 
					self.routing_table[self][key]= (new_dist, packet.src)
					self.routing_table[self][key]=self.calculate(self,key)
					print "UPDATE", self, "->", key, "=", self.routing_table[self][key][0] 
					changed = True
				elif packet.src is not r[1] and new_dist < r[0]: # if the sources are different, then this becomes a choice between new path or current path
					self.routing_table[self][key] = (new_dist, packet.src)
					print "UPDATE", self, "->", key, "=", new_dist
					changed = True
		return changed

	def print_table(self):
		pp.pprint(self.routing_table)

	def port_for_packet(self, packet):
		#pdb.set_trace()
		route=self.routing_table[self][packet.dst]
		port=self.ip_to_port[route[1]][0]
		return port

	def send_table(self,port):
		print "Sending table"
		pp.pprint(self.routing_table[self])
		print "\n\n"

		for i in xrange(self.get_port_count()):
			p=RoutingUpdate()
			for k,v in self.routing_table[self].iteritems():
				if v[1]==i:
					p.add_destination(k,infinity)	
				else:
					p.add_destination(k,v[0])
			self.send(p,port)

	def send_update(self,dst,distance,port):
		p=RoutingUpdate()
		p.add_destination(dst, distance)
		self.send(p,port, flood=True)

	def clean(self, switch):
		p=RoutingUpdate()
		del self.routing_table[switch]
		for k,v in self.routing_table[self].iteritems():
			if v[1]==switch:
				self.routing_table[self][k]=(infinity,None)
				p.add_destination(k,self.routing_table[self][k][0])
		self.send(p,self.ip_to_port[switch][0], flood=True)

	def calculate(self,src,dst):
		newEntry=(infinity,None)
		for k,v in self.routing_table.iteritems():   #check each connected component
			if dst in v.keys():
				new_distance=v[dst][0]+self.ip_to_port[k][1]
				if new_distance<newEntry[0]:
					newEntry=(new_distance,k)

		print "calculate ", src," ", dst, " : ", newEntry
		return newEntry

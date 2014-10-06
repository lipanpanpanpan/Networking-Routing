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
		self.changed_table = {} #dst->(distance, switch) 

	def handle_rx (self, packet, port):
		# Add your code here!
		if isinstance(packet, RoutingUpdate):
			if self.update_routing_table(packet,port):
				self.send_table()

		elif isinstance(packet, DiscoveryPacket):
			self.routing_table[self][packet.src] = (packet.latency, packet.src)
			self.changed_table[packet.src]=(packet.latency,packet.src)
			state=""
			if(packet.is_link_up):
				state="Added "
				self.ip_to_port[packet.src]=(port,packet.latency)
				self.send_update(packet.src,packet.latency,port)
				self.send_entire_table(packet.src)
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

		#pdb.set_trace()


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
				self.changed_table[key] = (new_dist, packet.src)
				print "NEW", self, "->", key, "=", new_dist
				changed = True
			else:
				r=self.routing_table[self][key]
				if packet.src is r[1] and r[0]!=new_dist: # if the sources are the same & changed then update 
					self.routing_table[self][key]= (new_dist, packet.src)
					self.routing_table[self][key]=self.calculate(self,key)
					self.changed_table[key] = self.routing_table[self][key]
					print "UPDATE", self, "->", key, "=", self.routing_table[self][key][0] 
					changed = True
				elif packet.src is not r[1] and new_dist == r[0]:
					if self.ip_to_port[packet.src][0]<self.ip_to_port[self.routing_table[self][key][1]][0]:
						self.routing_table[self][key]=(new_dist, packet.src)
						self.changed_table[key] = (new_dist, packet.src) 
						print "UPDATE LOWER KEY", self, "->", key, "=", self.routing_table[self][key][0] 
						changed=True	
				elif packet.src is not r[1] and new_dist < r[0]: # if the sources are different, then this becomes a choice between new path or current path
					self.routing_table[self][key] = (new_dist, packet.src)
					self.changed_table[key] = (new_dist,packet.src)
					print "UPDATE", self, "->", key, "=", new_dist
					changed = True
		return changed

	def print_table(self):
		pp.pprint(self.routing_table)

	def port_for_packet(self, packet):
		#pdb.set_trace()
		t=self.routing_table[self]
		if packet.dst in t.keys():
			route=t[packet.dst]
			if route[1] in self.ip_to_port.keys():
				return self.ip_to_port[route[1]][0]
		return None 

	def send_increments(self, port):
		p = RoutingUpdate()
		for k,v in self.changed_table.iteritems():
			p.add_destination(k, v)
		self.changed_table.clear()
		self.send(p, port, flood=True)

	def send_table(self):
		print "\n\n"
		for ip,port in self.ip_to_port.iteritems():
			d={}
			p=RoutingUpdate()
			for k,v in self.changed_table.iteritems(): #added
				if v[1]==ip and k!=self:
					d[k]=infinity
					p.add_destination(k,infinity)	
				else:
					d[k]=v[0]
					p.add_destination(k,v[0])
			print "Sending table from ", self, " to: ",ip
			pp.pprint(d)
			self.send(p,port[0])
		self.changed_table.clear() #added

	def send_entire_table(self,src):
		print "\n\n"
		d={}
		p=RoutingUpdate()
		for k,v in self.routing_table[self].iteritems(): #added
			if v[1]==src and k!=self:
				d[k]=infinity
				p.add_destination(k,infinity)	
			else:
				d[k]=v[0]
				p.add_destination(k,v[0])
		print "Sending table from ", self, " to: ", src
		pp.pprint(d)
		self.send(p,self.ip_to_port[src])



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
				self.routing_table[self][k]=self.calculate(self,k)
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

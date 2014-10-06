from sim.api import *
from sim.basics import *
import pdb
import pprint
pp = pprint.PrettyPrinter(indent=4)


'''
Create your distance vector router in this file.
'''


infinity=5

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
			self.update_routing_table(packet,port)    #table updated
			self.send_table()						  #send table

		elif isinstance(packet, DiscoveryPacket):
			state=""
			if(packet.is_link_up):
				self.ip_to_port[packet.src]=(port,packet.latency)  #if link is up ALWAYS set ip_to_port
				state="Added "

				if packet.src in self.routing_table[self].keys() and packet.latency>self.routing_table[self][packet.src] and (packet.src is not self.routing_table[self][packet.src][1]):
					print "Do nothing"   #there is some prexisting way thats better using a different route
				else:
					self.routing_table[self][packet.src] = (packet.latency, packet.src)
					self.changed_table[packet.src]=(packet.latency,packet.src)

				self.send_table()  #tell people of your new link. 
				self.send_entire_table(packet.src) #inform person accross new link of your services.
			else:
				state="Removed "
				self.ip_to_port[packet.src]=(port,infinity)  # set link distance to infinity
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
		pdb.set_trace()
		if packet.src not in self.routing_table.keys():
			self.routing_table[packet.src]={}             #create a dictionary if the src isn't there
		for key in keys:
			self.routing_table[packet.src][key]=(packet.get_distance(key),None)  # copy down locations for what we think this guy has 

		for key in keys: #for each of the sent distances
			new_dist = packet.get_distance(key) + self.ip_to_port[packet.src][1] #add link distance to packet's advertised distance

			if new_dist>infinity:  #set max distance to infinity
				new_dist=infinity

			if key not in self.routing_table[self] or self.routing_table[self][key][0]==infinity:   #if I didn't know how to get there then this is the best
				self.routing_table[self][key] = (new_dist,packet.src)
				self.changed_table[key] = (new_dist, packet.src)
				print "NEW", self, "->", key, "=", new_dist
			else:
				r=self.routing_table[self][key]
				if packet.src is r[1] and r[0]!=new_dist: # if prev. route was through packet.src and distance is different, then need to update
					self.routing_table[self][key]= (new_dist, packet.src)
					self.routing_table[self][key]=self.calculate(self,key)
					self.changed_table[key] = self.routing_table[self][key]
					print "UPDATE", self, "->", key, "=", self.routing_table[self][key][0] 
				elif (packet.src is not r[1]) and new_dist == r[0]:  #if distances are same, then check if port number is lower. 
					if self.ip_to_port[packet.src][0]<self.ip_to_port[self.routing_table[self][key][1]][0]:
						self.routing_table[self][key]=(new_dist, packet.src)
						self.changed_table[key] = (new_dist, packet.src) 
						print "UPDATE LOWER KEY", self, "->", key, "=", self.routing_table[self][key][0] 
				elif packet.src is not r[1] and new_dist < r[0]: # if the sources are different, then this becomes a choice between new path or current path
					self.routing_table[self][key] = (new_dist, packet.src)
					self.changed_table[key] = (new_dist,packet.src)
					print "UPDATE", self, "->", key, "=", new_dist

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
		if len(self.changed_table)==0:
			return

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
		print "Sending entire table from ", self, " to: ", src
		pp.pprint(d)
		self.send(p,self.ip_to_port[src][0])

	def send_update(self,dst,distance,port):
		p=RoutingUpdate()
		p.add_destination(dst, distance)
		self.send(p,port, flood=True)

	def clean(self, switch):
		p=RoutingUpdate()
		if switch in self.routing_table.keys():   #delete the switch from table since its no longer connected
			del self.routing_table[switch]
		for k,v in self.routing_table[self].iteritems():  #for all routes if used deleted switch. set to infinity.
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

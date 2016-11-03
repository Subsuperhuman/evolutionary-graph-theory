import sys
import os
import pygame
import time
import random
import math
import json
from pprint import pprint

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,0)

def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

def normal(a):
	if a[0] == a[1] == 0:
		return [0,0]
	b = [0.,0.]
	b[0] = -a[1]
	b[1] = a[0]
	return b

def mag(a):
	return math.sqrt(a[0]*a[0] + a[1]*a[1])

def unit(a):
	if a[0] == a[1] == 0:
		return [0,0]
	b = [0.,0.]
	m = mag(a)
	b[0] = a[0]/m
	b[1] = a[1]/m
	return b
 
class Simulation:
    
    def __init__(self,file=None, width=960,height=540):
        """Initialize"""
        """Initialize PyGame"""
        pygame.init()
        self.file = file
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width
                                               , self.height))

        self.graph = Graph(self.file,self.width,self.height)

    def Tick(self):
    	tNode = self.graph.nodes[random.choice(self.graph.nodes.keys())]
    	
    	spin = random.randint(0,100)*0.01
    	runTot = 0.0
    	for conn in tNode.connectionsOut:
    		runTot += conn.weight
    		if runTot > spin:
    			conn.n2.populate(conn.n1.genotype)
    			return;


    def MainLoop(self):
        pygame.key.set_repeat(500, 30)
        
        """background"""
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((255,255,255))
        self.screen.blit(self.background, (0, 0))
        mc = False
        mutant = Genotype(1)

        lastTick = 0
        
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()

            mp = pygame.mouse.get_pos()
            if(pygame.mouse.get_pressed()[0] and not mc):
            	mutant = Genotype(1)

            mc = pygame.mouse.get_pressed()[0]


            """logic"""

            for name,node in self.graph.nodes.iteritems():
            	dist = [mp[0] - node.x,mp[1] - node.y]
            	if mag(dist) < node.radius:
            		node.hover = True
            	else:
            		node.hover = False
            	if node.hover and mc:
            		node.populate(mutant)

            if pygame.time.get_ticks()-lastTick >= 1 and not mc:
            	lastTick = pygame.time.get_ticks()
            	self.Tick()

            """drawing"""

            for conn in self.graph.connections:
            	if conn.n1.hover:
            		ccolor = conn.hoverColor
            	else:
            		ccolor = conn.color
            	pygame.draw.line(self.screen, ccolor, (conn.x1,conn.y1), (conn.x2,conn.y2), 1)

            for name, node in self.graph.nodes.iteritems():
            	if node.hover:
            		ncolor = node.genotype.hoverColor
            	else:
            		ncolor = node.genotype.color
            	pygame.draw.circle(self.screen, ncolor, (node.x, node.y), node.radius, 0)

            for conn in self.graph.connections:
            	if conn.n1.hover:
	            	font = pygame.font.Font(None,16)
	                text = font.render(truncate(conn.weight,3), 1, (0, 0, 0))
	                textpos = text.get_rect(centerx=self.background.get_width()/2)
	                self.screen.blit(text, (conn.x1+0.5*(conn.x2-conn.x1),conn.y1+0.5*(conn.y2-conn.y1)))


            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))


class Genotype(object):
	"""A mutation instance"""
	def __init__(self, fitness):
		super(Genotype, self).__init__()
		self.fitness = fitness
		r = random.randint(30,255)
		g = random.randint(30,255)
		b = random.randint(30,255)
		self.color = (r,g,b)
		self.hoverColor = (r-30,g-30,b-30)
		

class Connection(object):
	"""A connectin between two nodes"""
	def __init__(self, n1, n2):
		super(Connection, self).__init__()
		self.n1 = n1
		self.n2 = n2
		self.weight = 0
		self.tweight = 1
		"""rendering properties"""
		self.x1 = 0
		self.x2 = 0
		self.y1 = 0
		self.y2 = 0
		self.color = (236,208,120)
		self.hoverColor = (84,36,55)
		

class Node(object):
	"""A graph node"""
	def __init__(self,name, x, y, genotype=Genotype(1)):
		super(Node, self).__init__()
		self.connectionsOut = []
		self.connectionsIn = []
		self.name = name

		self.hover = False
		self.selected = False

		self.x = x
		self.y = y
		self.genotype = genotype
		self.radius = 15

	def populate(self,genotype):
		self.genotype = genotype



class Graph(object):
	"""class for an entire graph instance"""
	def __init__(self, file=None, xsize=960, ysize=540):
		super(Graph, self).__init__()
		self.nodes = {}
		self.connections = []
		self.separation = 7.0

		if file!=None:
			with open(file) as data_file:
				data = json.load(data_file)
				for n in data["nodes"]:
					if "name" in n:
						self.nodes[n["name"]] = Node (n["name"],
							n["position"]["x"] if "position" in n and "x" in n["position"] else random.randint(20,xsize-20),
							n["position"]["y"] if "position" in n and "y" in n["position"] else random.randint(20,ysize-20))
					else:
						print("node is missing a name")

				for n in data["nodes"]:
					if "name" in n:
						n1 = self.nodes[n["name"]]
						if "connections" in n:
							for c in n["connections"]:
								if "to" in c:
									n2 = self.nodes[c["to"]]
									self.addConnection(n1,n2,c["weight"] if "weight" in c else 1)
								else:
									print("connection is missing a target")
			self.nNodes = len(self.nodes)

		else:
			self.nNodes = random.randint(4,30)
			for i in range(self.nNodes):
				tX = random.randint(20,xsize-20)
				tY = random.randint(20,ysize-20)
				self.nodes[str(i)] = (Node(str(i),tX,tY))

			for iName,iNode in self.nodes.iteritems():
				for jName,jNode in self.nodes.iteritems():
					if random.randint(0,100) >= 0:
						self.addConnection(iNode,jNode,random.randint(0,100))
				if len(iNode.connectionsOut) < 1:
					self.addConnection(iNode,jNode,random.randint(0,100))
		
		for iName,iNode in self.nodes.iteritems():
			totalWeight = 0.0
			for iConn in iNode.connectionsOut:
				totalWeight += iConn.tweight
			invTotalWeight = 1.0/totalWeight if totalWeight > 0 else 0
			for iConn in iNode.connectionsOut:
				iConn.weight = invTotalWeight*iConn.tweight

		for conn in self.connections:
				v = (conn.n2.x-conn.n1.x,conn.n2.y-conn.n1.y)
				unv = unit(normal(v))
				conn.x1 = conn.n1.x
				conn.x2 = conn.n2.x
				conn.y1 = conn.n1.y
				conn.y2 = conn.n2.y
				if conn.n1.x != conn.n2.x and conn.n1.y != conn.n2.y:
					conn.x1 += self.separation*unv[0]
					conn.x2 += self.separation*unv[0]
					conn.y1 += self.separation*unv[1]
					conn.y2 += self.separation*unv[1]

	def addConnection(self,n1,n2,weight=1):
		self.connections.append(Connection(n1,n2))
		n1.connectionsOut.append(self.connections[-1])
		n2.connectionsIn.append(self.connections[-1])
		self.connections[-1].tweight = weight

if __name__ == "__main__":
	Instance = Simulation(sys.argv[1] if len(sys.argv) > 1 else None)
	Instance.MainLoop()
       
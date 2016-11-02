import sys
import os
import pygame
import time
import random
import math
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
    
    def __init__(self,nNodes=10, width=960,height=540):
        """Initialize"""
        """Initialize PyGame"""
        pygame.init()
        self.nNodes = nNodes
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width
                                               , self.height))

        self.graph = Graph(self.nNodes,self.width,self.height)

    def Tick(self):
    	tNode = self.graph.nodes[random.randint(0,len(self.graph.nodes)-1)]
    	
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

            for node in self.graph.nodes:
            	dist = [mp[0] - node.x,mp[1] - node.y]
            	if mag(dist) < node.radius:
            		node.hover = True
            	else:
            		node.hover = False
            	if node.hover and mc:
            		node.populate(mutant)

            if pygame.time.get_ticks()-lastTick >= 1:
            	lastTick = pygame.time.get_ticks()
            	self.Tick()

            """drawing"""

            for conn in self.graph.connections:
            	if conn.n1.hover:
            		ccolor = conn.hoverColor
            	else:
            		ccolor = conn.color
            	pygame.draw.line(self.screen, ccolor, (conn.x1,conn.y1), (conn.x2,conn.y2), 1)

            for node in self.graph.nodes:
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
		self.tweight = 0
		"""rendering properties"""
		self.x1 = 0
		self.x2 = 0
		self.y1 = 0
		self.y2 = 0
		self.color = (236,208,120)
		self.hoverColor = (84,36,55)
		

class Node(object):
	"""A graph node"""
	def __init__(self, x, y, genotype=Genotype(1)):
		super(Node, self).__init__()
		self.connectionsOut = []
		self.connectionsIn = []

		self.mutated = False

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
	def __init__(self, nNodes, xsize, ysize):
		super(Graph, self).__init__()
		self.nNodes = nNodes
		self.nodes = []
		self.connections = []
		for i in range(nNodes):
			tX = random.randint(20,xsize-20)
			tY = random.randint(20,ysize-20)
			self.nodes.append(Node(tX,tY))

		for iNode in self.nodes:
			for jNode in self.nodes:
				if random.randint(0,100) > 50:
					self.connections.append(Connection(iNode,jNode))
					iNode.connectionsOut.append(self.connections[-1])
					jNode.connectionsIn.append(self.connections[-1])
			if len(iNode.connectionsOut) < 1:
				jNode = self.nodes[random.randint(0,len(self.nodes)-1)]
				self.connections.append(Connection(iNode,jNode))
				iNode.connectionsOut.append(self.connections[-1])
				jNode.connectionsIn.append(self.connections[-1])
		
		for iNode in self.nodes:
			totalWeight = 0.0
			for iConn in iNode.connectionsOut:
				iConn.tweight = random.randint(0,100)
				totalWeight += iConn.tweight
			invTotalWeight = 1.0/totalWeight if totalWeight > 0 else 0
			for iConn in iNode.connectionsOut:
				iConn.weight = invTotalWeight*iConn.tweight

		for conn in self.connections:
				v = (conn.n2.x-conn.n1.x,conn.n2.y-conn.n1.y)
				unv = unit(normal(v))
				d = 7
				conn.x1 = conn.n1.x
				conn.x2 = conn.n2.x
				conn.y1 = conn.n1.y
				conn.y2 = conn.n2.y
				if conn.n1.x != conn.n2.x and conn.n1.y != conn.n2.y:
					conn.x1 += d*unv[0]
					conn.x2 += d*unv[0]
					conn.y1 += d*unv[1]
					conn.y2 += d*unv[1]

if __name__ == "__main__":
    Instance = Simulation(20)
    Instance.MainLoop()
       
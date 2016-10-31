x = 100
y = 0
import sys
import os
import pygame
import time
import random
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
 

class PyManMain:
    """The Main PyMan Class - This class handles the main 
    initialization and creating of the Game."""
    
    def __init__(self, width=960,height=540):
        """Initialize"""
        """Initialize PyGame"""
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width
                                               , self.height))

        self.graph = Graph(10)
                                                          
    def MainLoop(self):
        """This is the Main Loop of the Game"""
        
        """tell pygame to keep sending up keystrokes when they are
        held down"""
        pygame.key.set_repeat(500, 30)
        
        """background"""
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((255,255,255))
        self.screen.blit(self.background, (0, 0))
        
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()

            """logic"""

            """drawing"""

            for conn in self.graph.connections:
            	pygame.draw.line(self.screen, (0,0,0), (conn.n1.x,conn.n1.y), (conn.n2.x, conn.n2.y), 1)

            for node in self.graph.nodes:
            	pygame.draw.circle(self.screen, (0,0,255), (node.x, node.y), 20, 0)

            for conn in self.graph.connections:
            	font = pygame.font.Font(None,16)
                text = font.render(str(conn.weight), 1, (0, 0, 0))
                textpos = text.get_rect(centerx=self.background.get_width()/2)
                self.screen.blit(text, (conn.n1.x+0.5*(conn.n2.x-conn.n1.x),conn.n1.y+0.5*(conn.n2.y-conn.n1.y)))


            pygame.display.flip()

class Connection(object):
	"""docstring for Connection"""
	def __init__(self, n1, n2):
		super(Connection, self).__init__()
		self.n1 = n1
		self.n2 = n2
		self.weight = 0
		

class Node(object):
	"""docstring for Node"""
	def __init__(self, x, y):
		super(Node, self).__init__()
		self.x = x
		self.y = y
		self.connectionsOut = []
		self.connectionsIn = []

class Graph(object):
	"""docstring for Graph"""
	def __init__(self, nNodes):
		super(Graph, self).__init__()
		self.nNodes = nNodes
		self.nodes = []
		self.connections = []
		for i in range(nNodes):
			tX = random.randint(30,930)
			tY = random.randint(20,520)
			self.nodes.append(Node(tX,tY))

		for iNode in self.nodes:
			for jNode in self.nodes:
				self.connections.append(Connection(iNode,jNode))
				iNode.connectionsOut.append(self.connections[-1])
				jNode.connectionsIn.append(self.connections[-1])

		for iNode in self.nodes:
			for iConn in iNode.connectionsOut:
				iConn.weight = 1.0/len(iNode.connectionsOut)



if __name__ == "__main__":
    MainWindow = PyManMain()
    MainWindow.MainLoop()
       
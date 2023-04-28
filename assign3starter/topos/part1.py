#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

class part1_topo(Topo):
    
    #Generates the topology. 
    def build(self):
        #create a new switch s1 according to the topology.
        switch1 = self.addSwitch('s1')
        #generate 4 hosts with names according to the topology. 
        for i in range(4):
            h = self.addHost('h'+ str(i+1))
            #link every host created to the switch s1. 
            self.addLink(h, switch1)

topos = {'part1' : part1_topo}

if __name__ == '__main__':
    t = part1_topo()
    net = Mininet (topo=t)
    net.start()
    CLI(net)
    net.stop()

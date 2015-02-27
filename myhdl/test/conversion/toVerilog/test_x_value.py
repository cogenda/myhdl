import os.path
import unittest
from unittest import TestCase
import random

from myhdl import *

from util import setupCosimulation

ACTIVE_LOW, INACTIVE_HIGH = 0, 1

def fifo(Ck, Rst, D, Q):
    '''FIFO. Initial values are partially initialized.
    in the first few clock cycles, will output True, X, 1, X, ...
    '''

    N = 4
    mem = [Signal(bool()) for _ in xrange(N)]

    @always(Ck.posedge, Rst.negedge)
    def logic():
        if Rst==False:
            mem[2].next = 1
            mem[0].next = True
        else:
            mem[N-1].next = D
            for i in downrange(N-1):
                mem[i].next = mem[i+1]
            Q.next = mem[0]
    return logic

class TestValueX(TestCase):

    def testValueX(self):
        Ck, Rst, D, Q, Qn = [Signal(False) for _ in xrange(5)]

        #toVerilog.trace = True
        toVerilog(fifo, Ck, Rst, D, Q)
        fifo_v = setupCosimulation(name=fifo.func_name, **toVerilog.portmap)
        #fifo_ref = fifo(Ck, Rst, D, Q)

        @instance
        def clockGen():
            while True:
                yield delay(5)
                Ck.next = not Ck

        @instance
        def stimulus():
            Rst.next = False
            yield Ck.negedge
            Rst.next = True

            for i in xrange(5):
                #print now(), Ck, D, Q
                yield Ck.posedge
            raise StopSimulation
      
        sim = Simulation(instances())
        sim.run()

if __name__ == '__main__':
    unittest.main()



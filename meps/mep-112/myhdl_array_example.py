'''
Created on 1 August 2015


@author: Josy
'''

from __future__ import print_function

import random

import myhdl

import hdlutils



def nDcube( Clk, Reset, A0, A1, A2, D , Wr , Q):
    ''' a small example to test the nD experimental implementation '''

    cube = myhdl.Array( (3, 3, 3), myhdl.intbv(0)[len(D):])
    
    @myhdl.always_seq( Clk.posedge, reset = Reset)
    def fill():
        for l in range(3):
            for k in range(3):
                for j in range(3):
                    if A2 ==l and A1 == k and A0 == j and Wr:
                        cube[l][k][j].next = D
        
    @myhdl.always_comb
    def calc():
        cubesum = myhdl.intbv(0)[len(Q):]
        for l in range(3):
            for k in range(3):
                for j in range(3):
                    cubesum += cube[l][k][j]
        Q.next = cubesum
        
    return fill, calc



def tb_nDcube():
    WIDTH_D = 8
    Clk = myhdl.Signal( bool( 0 ) )
    Reset = myhdl.ResetSignal( 0, active = 1, async = True )
    A0, A1, A2 = [myhdl.Signal( myhdl.intbv( 0 )[4:] ) for _ in range(3)]
    D = myhdl.Signal( myhdl.intbv( 0 )[WIDTH_D:] )
    Wr = myhdl.Signal( bool( 0 ) )
    Q = myhdl.Signal( myhdl.intbv( 0 )[WIDTH_D + 5:] )
    
    dut = nDcube(Clk, Reset, A0, A1, A2, D, Wr, Q)
    
    random.seed("We want repeatable randomness")
    td = [ random.randint(1, 2**WIDTH_D) for _ in range(3**3)]
    
    ClkCount = myhdl.Signal(myhdl.intbv(0)[32:])
    tCK = 20

    @myhdl.instance
    def clkgen():
        yield hdlutils.genClk(Clk, tCK, ClkCount)

    @myhdl.instance
    def resetgen():
        yield hdlutils.genReset(Clk, tCK, Reset)

    @myhdl.instance
    def stimulus():
        yield hdlutils.delayclks(Clk, tCK, 5)
        idx = 0
        for l in range(3):
            A2.next = l
            for k in range(3):
                A1.next = k
                for j in range(3):
                    A0.next = j
                    D.next = td[idx]
                    yield hdlutils.pulsesig(Clk, tCK, Wr, 1, 1)
                    idx += 1
        
        yield hdlutils.delayclks(Clk, tCK, 5)
        raise myhdl.StopSimulation
    
    return dut, clkgen, resetgen, stimulus


def convert():      
    WIDTH_D = 8
    Clk = myhdl.Signal( bool( 0 ) )
    Reset = myhdl.ResetSignal( 0, active = 1, async = True )
    A0, A1, A2 = [myhdl.Signal( myhdl.intbv( 0 )[2:] ) for _ in range(3)]
    D = myhdl.Signal( myhdl.intbv( 0 )[WIDTH_D:] )
    B = myhdl.Signal( bool( 0 ) )
    Wr = myhdl.Signal( bool( 0 ) )
    Qcube = myhdl.Signal( myhdl.intbv( 0 )[WIDTH_D + 5:] )
    Qbool = myhdl.Signal( myhdl.intbv( 0 )[5:] )
    Qcol  = myhdl.Signal( myhdl.intbv( 0 )[WIDTH_D + 2:] )
    
    myhdl.toVHDL( nDcube, Clk, Reset, A0, A1, A2, D, Wr, Qcube)
#     myhdl.toVerilog( nDcube, Clk, Reset, A0, A1, A2, D, Wr, Qcube)


if __name__ == '__main__':
    hdlutils.simulate(1000, tb_nDcube)
    convert()

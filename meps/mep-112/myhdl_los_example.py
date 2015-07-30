'''
Created on 29 July 2015


@author: Josy
'''

from __future__ import print_function

import random

import myhdl

import hdlutils
    
def m1Dcube( Clk, Reset, A0, A1, A2, D , Wr , Q):
    ''' a small example to test the m1D experimental implementation '''

    cube = [[[ myhdl.Signal(myhdl.intbv(l*9+k*3+j+1)[len(D):]) for j in range(3)] for k in range(3)] for l in range(3)]
    
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
      
                      
def m1Dbcube( Clk, Reset, A0, A1, A2, D , Wr , Q): 
    ''' testing for bool() '''
    
    bcube =  [[[ myhdl.Signal(bool(0)) for _ in range(3)] for __ in range(3)] for ___ in range(3)]
    
    @myhdl.always_seq( Clk.posedge, reset = Reset)
    def fill():
        if Wr:
            bcube[A2][A1][A0].next = D
    
    @myhdl.always_seq( Clk.posedge, reset = Reset)
    def calc():
        cubesum = 0
        for l in range(3):
            for k in range(3):
                for j in range(3):
                    cubesum += bcube[l][k][j]
        Q.next = cubesum
    return fill, calc


def m1Dlist( Clk, Reset, A0, D, Wr, Q):
    ''' a module to verify that the simple LoS still works OK'''
    
    col = [ myhdl.Signal(D.val) for _ in range(3)] 
 
    @myhdl.always_seq( Clk.posedge, reset = Reset)
    def fill():
        for j in range(3):
            if A0 == j and Wr:
                col[j].next = D
    
    @myhdl.always_seq( Clk.posedge, reset = Reset)
    def calc():
        colsum = myhdl.intbv(0)[len(Q):]
        for j in range(3):
            colsum += col[j]
        Q.next = colsum
        
    return fill, calc


def tb_m1Dcube():
    WIDTH_D = 8
    Clk = myhdl.Signal( bool( 0 ) )
    Reset = myhdl.ResetSignal( 0, active = 1, async = True )
    A0, A1, A2 = [myhdl.Signal( myhdl.intbv( 0 )[4:] ) for _ in range(3)]
    D = myhdl.Signal( myhdl.intbv( 0 )[WIDTH_D:] )
    Wr = myhdl.Signal( bool( 0 ) )
    Q = myhdl.Signal( myhdl.intbv( 0 )[WIDTH_D + 5:] )
    
    dut = m1Dcube(Clk, Reset, A0, A1, A2, D, Wr, Q)
    
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


def tb_m1Dbcube():
    Clk = myhdl.Signal( bool( 0 ) )
    Reset = myhdl.ResetSignal( 0, active = 1, async = True )
    A0, A1, A2 = [myhdl.Signal( myhdl.intbv( 0 )[4:] ) for _ in range(3)]
    D = myhdl.Signal( bool(0) )
    Wr = myhdl.Signal( bool( 0 ) )
    Q = myhdl.Signal( myhdl.intbv( 0 )[5:] )
    
    dut = m1Dbcube(Clk, Reset, A0, A1, A2, D, Wr, Q)
    
    random.seed("We want repeatable randomness")
    td = [ random.randint(0, 1) for _ in range(3**3)]
    
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

       
# no tb for m1Dlist

            
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
    
    myhdl.toVHDL( m1Dcube, Clk, Reset, A0, A1, A2, D, Wr, Qcube)
    myhdl.toVHDL( m3Dbool, Clk, Reset, A0, A1, A2, B, Wr, Qbool)
    myhdl.toVHDL( m1Dlist, Clk, Reset, A0, D, Wr, Qcol)
if __name__ == '__main__':
#     hdlutils.simulate(1000, tb_m1Dcube)
#     hdlutils.simulate(1000, tb_m3Dbool)
    convert()
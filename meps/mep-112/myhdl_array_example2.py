'''
Created on 2 August 2015


@author: Josy
'''

from __future__ import print_function

import random

import myhdl

import hdlutils


# def shift( Clk, matrix, D,  Enable):
#     ''' testing down on level '''
#     
#     @myhdl.always_seq( Clk.posedge, reset = None)
#     def shift():    
#         for k in range(3):
#             matrix[k][:2].next = matrix[k][1:]
#             matrix[k][2].next = D[k]
#             
#     return shift
#     

def nDmatrix( Clk, Reset, A0, A1, D , Wr1, Wr2 , Q , ShiftLeft, ShiftUp):
    ''' a small example to test the nD experimental implementation '''

    matrix = myhdl.Array( (3, 3), myhdl.Signal(myhdl.intbv(0)[len(D):]))
    vector = myhdl.Array( (3,), myhdl.Signal(myhdl.intbv(0)[len(D):]))
    
    @myhdl.always_seq( Clk.posedge, reset = Reset)
    def fill():
            for k in range(3):
                for j in range(3):
                    if A1 == k and A0 == j and Wr1:
                        matrix[k][j].next = D
            for j in range(3):
                if A0 == j and Wr2:
                    vector[j].next = D
            if ShiftLeft:
                for k in range(3):
                    for j in range(2):
                        matrix[k][j].next = matrix[k][j+1]
                    matrix[k][2].next = vector[k]
            elif ShiftUp:
                for k in range(2):
                    matrix[k+1].next = matrix[k]
                matrix[0] =  vector

    @myhdl.always_comb
    def calc():
        matrixsum = myhdl.intbv(0)[len(Q):]
        for l in range(3):
            for k in range(3):
                for j in range(3):
                    matrixsum += matrix[l][k][j]
        Q.next = matrixsum
                
    return fill, calc



def tb_nDmatrix():
    WIDTH_D = 8
    Clk = myhdl.Signal( bool( 0 ) )
    Reset = myhdl.ResetSignal( 0, active = 1, async = True )
    A0, A1 = [myhdl.Signal( myhdl.intbv( 0 )[2:] ) for _ in range(2)]
    D = myhdl.Signal( myhdl.intbv( 0 )[WIDTH_D:] )
    Wr1 = myhdl.Signal( bool( 0 ) )
    Wr2 = myhdl.Signal( bool( 0 ) )
    ShiftLeft = myhdl.Signal( bool( 0 ) )
    ShiftUp = myhdl.Signal( bool( 0 ) )
    Q = myhdl.Signal( myhdl.intbv( 0 )[WIDTH_D + 4:] )
    
    dut = nDmatrix(Clk, Reset, A0, A1, D , Wr1, Wr2 , Q , ShiftLeft, ShiftUp)
    
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

        for k in range(3):
            A1.next = k
            for j in range(3):
                A0.next = j
                D.next = td[idx]
                yield hdlutils.pulsesig(Clk, tCK, Wr1, 1, 1)
                idx += 1
        
        yield hdlutils.delayclks(Clk, tCK, 5)
        raise myhdl.StopSimulation
    
    return dut, clkgen, resetgen, stimulus


def convert():      
    WIDTH_D = 8
    Clk = myhdl.Signal( bool( 0 ) )
    Reset = myhdl.ResetSignal( 0, active = 1, async = True )
    A0, A1 = [myhdl.Signal( myhdl.intbv( 0 )[2:] ) for _ in range(2)]
    D = myhdl.Signal( myhdl.intbv( 0 )[WIDTH_D:] )
    B = myhdl.Signal( bool( 0 ) )
    Wr1 = myhdl.Signal( bool( 0 ) )
    Wr2 = myhdl.Signal( bool( 0 ) )
    ShiftLeft = myhdl.Signal( bool( 0 ) )
    ShiftUp = myhdl.Signal( bool( 0 ) )
    Q = myhdl.Signal( myhdl.intbv( 0 )[WIDTH_D + 4:] )
    
    myhdl.toVHDL( nDmatrix, Clk, Reset, A0, A1, D , Wr1, Wr2 , Q, ShiftLeft, ShiftUp)
    myhdl.toVerilog( nDmatrix, Clk, Reset, A0, A1, D , Wr1, Wr2 , Q, ShiftLeft, ShiftUp)


if __name__ == '__main__':
    hdlutils.simulate(1000, tb_nDmatrix)
    convert()

'''
Created on 15 Aug 2015

@author: Josy
'''

import myhdl


def convolve2D(Clk, DataA, DataB, Result ):
    """ computes the convoultion over 2 equally sized matrices
        DataA : Array( (N,N) , myhdl.Signal(intbv()[WIDTH_DATAA:]) )
        DataB : Array( (N,N) , myhdl.Signal(intbv()[WIDTH_DATAB:]) ) or Array( (N,N) , intbv()[WIDTH_DATAB:] )
        Result : Signal( intbv()[WIDTH_RESULT:])        
    """
    NY, NX = DataA._sizes   # need a 'nicer' way for this
    WIDTH_DA = len(DataA[0][0])
    WIDTH_DB = len(DataB[0][0])
    
    def multiply(Clk, DataA, DataB, Result ):
        ''' multiply the two matrices element-wise'''
        
        @myhdl.always_seq(Clk.posedge, reset = None)
        def rtl():
            for k in range(NY):
                for j in range(NX):
                    Result[k][j].next = DataA[k][j] * DataB[k][j]
                                                                  
        return rtl
    
    def summation(Clk, Data, Result):
        ''' simple 'stair-case' summation of all the elements in the matrix'''
        
        @myhdl.always_seq(Clk.posedge, reset = None)
        def rtl():
            # must clone the intbv of the Result ...
            sum2D = myhdl.intbv(0, min = Result.min, max = Result.max)
            for k in range(NY):
                for j in range(NX):
                    sum2D += Data[k][j]
            Result.next = sum2D
            
        return rtl
    

    # there must be a shortcut for the next 14 lines ...       
    if  DataA.element.min < 0 :
        if  DataB.element.min < 0 :
            mrmin = -(DataA.element.min * DataB.element.min)
            mrmax = DataA.element.max * DataB.element.max
        else:
            mrmin = DataA.element.min * 2**DataB.element._nrbits
            mrmax = DataA.element.max * 2**DataB.element._nrbits
    else:
        if  DataB.element.min < 0 :
            mrmin = DataB.element.min * 2**DataA.element._nrbits
            mrmax = DataB.element.max * 2**DataA.element._nrbits
        else:
            mrmin = 0
            mrmax = 2**(DataA.element._nrbits + DataA.element._nrbits)
        
    m_Result = myhdl.Array( (NY, NX), myhdl.Signal(myhdl.intbv(0, min = mrmin, max = mrmax)))
    
    m = multiply(Clk, DataA, DataB, m_Result )
    s = summation(Clk, m_Result, Result )

      
    return m, s
    

if __name__ == '__main__':
    
    def tb_convolve2D():
        clock = myhdl.Signal(bool(0))
        dataa = myhdl.Array( (3,3), myhdl.Signal( myhdl.intbv(0)[8:]))
        datab = myhdl.Array( [[1, 2, 3], [4, 5, 6,], [7, 8, 9]], myhdl.Signal( myhdl.intbv(0)[8:]))
        result = myhdl.Signal( myhdl.intbv(0)[16+4:])
        
        hw_inst = convolve2D(clock, dataa, datab, result)
        
        @myhdl.always(myhdl.delay(10))
        def clkgen():
            clock.next = not clock
        
        @myhdl.instance
        def stimulusin():
            reset.next = 1
            for _ in range( 3 ):
                yield clock.posedge
                
            yield clock.negedge
            reset.next = 0
            yield clock.negedge
            dataa.next = [[1, 2, 3], [4, 5, 6,], [7, 8, 9]]
            
    
            yield clock.negedge
    
            for k in range(3):
                for j in range(3):
                    dataa[k][j].next = k * 3 + j + 1
                    datab[k][j].next = (2-k) * 3 + (2-j) + 1            
            
            yield clock.negedge
            dataa[0].next = [3, 2, 1]    
                        
            yield clock.negedge
            dataa[1][2].next = 100
            
            for _ in range(10):
                yield clock.negedge        
            raise myhdl.StopSimulation
        
        
        return myhdl.instances()
    
    
    def convert():
        ''' this is a bit more work as we can't convert lists in the top module (yet) '''
        
        def matrixwriter(Clk, Reset, D, AY, AX, Wr, M):
            ''' to fill each matrix '''
            @myhdl.always_seq(Clk.posedge, reset = Reset)
            def rtl():
                for k in range(3):
                    for j in range(3):
                        if k == AY and j == AX and Wr:
                            M[k][j].next = D
                    
            return rtl
        
        
        # two Signal matrices
        def top_convolve2D( Clk, Reset, D, AY, AX, WrA, WrB, Q):
            ''' the ultimate test? '''
            dataa = myhdl.Array( (3,3), myhdl.Signal( myhdl.intbv(0)[8:]))
            datab = myhdl.Array( (3,3), myhdl.Signal( myhdl.intbv(0)[8:]))
            
            # filling the two matrices                    
            wa = matrixwriter(Clk, Reset, D, AY, AX, WrA, dataa)            
            wb = matrixwriter(Clk, Reset, D, AY, AX, WrB, datab) 
            
            # convolving the two matrices
            conv = convolve2D(Clk, dataa, datab, Q )
            
            return wa, wb, conv            

        # one Signal and one Constant matrix
        def SC_convolve2D( Clk, Reset, D, AY, AX, Wr, Q):
            ''' one SIgnal Matrix and a COnstant Matrix '''
            dataa  = myhdl.Array( (3,3), myhdl.Signal( myhdl.intbv(0)[8:]))
            SobelH = myhdl.Array( [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],  myhdl.intbv(0, min= -3, max = 3))
            
            w = matrixwriter(Clk, Reset, D, AY, AX, Wr, dataa)            
            conv = convolve2D(Clk, dataa, SobelH, Q )

            return w, conv   
    
        clock = myhdl.Signal(bool(0))
        reset = myhdl.ResetSignal(0, active=1, async=True)
        data =  myhdl.Signal( myhdl.intbv(0)[8:])
        addry, addrx =  [myhdl.Signal( myhdl.intbv(0)[2:]) for _ in range(2)]
        wra = myhdl.Signal(bool(0))
        wrb = myhdl.Signal(bool(0))
        result = myhdl.Signal(myhdl.intbv(0)[20:])
        scresult = myhdl.Signal(myhdl.intbv(0, min = -2**(8+2+4), max = 2**(8+2+4) ))
            
        # finally convert
        myhdl.toVHDL(top_convolve2D, clock, reset, data, addry, addrx, wra, wrb, result)
        myhdl.toVHDL(SC_convolve2D,  clock, reset, data, addry, addrx, wra, scresult)





#     myhdl.Simulation(myhdl.traceSignals(tb_convolve2D )).run(3000)
    convert()


'''
Created on 15 Aug 2015

@author: Josy
'''

import myhdl


def convolve2D(Clk, Reset, DataA, DataB, Result ):
    """ computes the convoultion over 2 equally sized matrices
        DataA : Array( (N,N) , myhdl.Signal(intbv()[WIDTH_DATAA:]) )
        DataB : Array( (N,N) , myhdl.Signal(intbv()[WIDTH_DATAB:]) ) or Array( (N,N) , intbv()[WIDTH_DATAB:] )
        Result : Signal( intbv()[WIDTH_RESULT:])        
    """
    NY, NX = DataA._sizes   # need a 'nicer' way for this
    WIDTH_DA = len(DataA[0][0])
    WIDTH_DB = len(DataB[0][0])
    
    def multiply(Clk, Reset, DataA, DataB, Result ):
        ''' multiply the two matrices element-wise'''
        
        @myhdl.always_seq(Clk.posedge, reset = Reset)
        def rtl():
            for k in range(NY):
                for j in range(NX):
                    Result[k][j].next = DataA[k][j] * DataB[k][j]
                                                                  
        return rtl
    
    def summation(Clk, Reset, Data, Result):
        ''' simple 'stair-case' summation of all the elements in the matrix'''
        
        @myhdl.always_seq(Clk.posedge, reset = Reset)
        def rtl():
            sum2D = myhdl.intbv(0)[len(Result):]
            for k in range(NY):
                for j in range(NX):
                    sum2D += Data[k][j]
            Result.next = sum2D
            
        return rtl
    
       
    m_Result = myhdl.Array( (NY, NX), myhdl.Signal(myhdl.intbv(0)[WIDTH_DB + WIDTH_DA:] ))
    m = multiply(Clk, Reset, DataA, DataB, m_Result )
    s = summation(Clk, Reset, m_Result, Result )

      
    return m, s
    

if __name__ == '__main__':
    
    def tb_convolve2D():
        clock = myhdl.Signal(bool(0))
        reset = myhdl.ResetSignal(0, active=1, async=True)
        dataa = myhdl.Array( (3,3), myhdl.Signal( myhdl.intbv(0)[8:]))
        datab = myhdl.Array( [[1, 2, 3], [4, 5, 6,], [7, 8, 9]], myhdl.Signal( myhdl.intbv(0)[8:]))
        result = myhdl.Signal( myhdl.intbv(0)[16+4:])
        
        hw_inst = convolve2D(clock, reset, dataa, datab, result)
        
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
        
        def top_convolve2D( Clk, Reset, D, AY, AX, WrA, WrB, Q):
            ''' the ultimate test? '''
            dataa = myhdl.Array( (3,3), myhdl.Signal( myhdl.intbv(0)[8:]))
            datab = myhdl.Array( (3,3), myhdl.Signal( myhdl.intbv(0)[8:]))
            
            def top_writer(Clk, Reset, D, AY, AX, Wr, M):
                ''' to fill each matrix '''
                @myhdl.always_seq(Clk.posedge, reset = Reset)
                def rtl():
                    for k in range(3):
                        for j in range(3):
                            if k == AY and j == AX and Wr:
                                M[k][j].next = D
                        
                return rtl

            # filling the two matrices                    
            wa = top_writer(Clk, Reset, D, AY, AX, WrA, dataa)            
            wb = top_writer(Clk, Reset, D, AY, AX, WrB, datab) 
            
            # convolving the two matrices
            conv = convolve2D(Clk, Reset, dataa, datab, Q )
            
            return wa, wb, conv            

        
        clock = myhdl.Signal(bool(0))
        reset = myhdl.ResetSignal(0, active=1, async=True)
        data =  myhdl.Signal( myhdl.intbv(0)[8:])
        addry, addrx =  [myhdl.Signal( myhdl.intbv(0)[2:]) for _ in range(2)]
        wra = myhdl.Signal(bool(0))
        wrb = myhdl.Signal(bool(0))
        result = myhdl.Signal(myhdl.intbv(0)[20:])
            
        # finally convert
        myhdl.toVHDL(top_convolve2D, clock, reset, data, addry, addrx, wra, wrb, result)





    myhdl.Simulation(myhdl.traceSignals(tb_convolve2D )).run(3000)
    convert()


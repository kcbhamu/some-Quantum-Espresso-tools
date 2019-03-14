# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 15:14:33 2019

@author: 15902

GUI for scientific program
"""
import sys
from Tkinter import *
import tkFileDialog
from tkFileDialog import askopenfilename
from matplotlib import pyplot

class bandplot:
    def __init__(self):
        print "now preparing to plot the bands"
        self.bandsheet=[]
        self.allbands=None
        self.symboList=None
        self.Ef=None
        self.Emin=None
        self.Emax=None
        self.e_zero=None
    def Add_Kpoints(self,symmlist):
        """
        define variables
            self.sympoints==the k-point each line
            self.sympointNum==the number of k-point in the corresponding line
            self.kpointNum==total number used
            self.kpoints==all the k-points used with total number of self.tatal_sympointNum
        For example:
        0.000 0.000 0.500 20
        0.000 0.000 0.000 20
        0.000 0.500 0.500 1
        sympoints=[[0,0,0.5],[0,0,0],[0,0.5,0.5]]
        there are 20 points including 0,0,0.5, the [0,0,0] points starts at 21
        sympointNum=20,20,1
        self.kpointNum=41
        len(kpoints)=41
        """
        self.sympoints=[]
        self.sympointNum=[]
        tmp_list=symmlist.split("\n")
        for aline in tmp_list:
            aline=aline.split(" ")
            print aline
            self.sympointNum.append(int(aline.pop()))
            tmp_point=[]
            for xyz in aline:
                tmp_point.append(float(xyz))
            self.sympoints.append(tmp_point)
        self.kpointNum=sum(self.sympointNum)
        self.kpoints=[]
        for i in range(1,len(self.sympoints)):
            start=self.sympoints[i-1]
            end=self.sympoints[i]
            num=self.sympointNum[i-1]
            dx=(end[0]-start[0])*1.0/num
            dy=(end[1]-start[1])*1.0/num
            dz=(end[2]-start[2])*1.0/num
            for j in range(num):
                self.kpoints.append([start[0]+dx*j,start[1]+dy*j,start[2]+dz*j])
        self.kpoints.append(self.sympoints[-1])
        print "total number of k points:"+str(len(self.kpoints))
        return
    
    def setFermi(self,value):
        self.Ef=value
    
    def setY_min(self,value):
        self.Emin=value
    def setY_max(self,value):
        self.Emax=value
    def set_symbol(self,symbols):
        #symbols are seperated by "-"
        self.symboList=symbols.split("-")    
        
    def readGNU(self,filename):
        """
        self.allbands==a list of all the bands with total number of bands defined by num in the calculation
        """
        gnu=open(filename,"r")
        self.bandsGNU=[]
        all_line=gnu.readlines()
        gnu.close()
        
        self.allbands=[]
        self.bandNum=0
        group=[]
        for line in all_line:
            try:
                line=line.rstrip().split()
                group.append(float(line[1]))
            except:
                if group!=[]:
                    self.allbands.append(group)
                    self.bandNum+=1
                group=[]
                
    def bandmax(self,fermilevel):
        bandMaximum=[]
        bandMinimum=[]
        for bands in self.allbands:
            bandMaximum.append(max(bands))
            bandMinimum.append(min(bands))
        tmp=float("-inf")
        for i in bandMaximum:
            if i<fermilevel and i>tmp:
                tmp=i
        VBMax=tmp
        tmp=float("inf")
        for i in bandMinimum:
            if i>=fermilevel and i<tmp:
                tmp=i
        CBMin=tmp
        return VBMax,CBMin
            
    def graph(self):
        if self.allbands==None:
            print "no data input"
            return
        if self.Ef==None:
            print "fermi-level not specified"
            return
                
        if self.symboList==None:
            symbol=[]
        else:
            symbol=self.symboList
            
        if self.Emin==None:
            Min=-1
        else:
            Min=self.Emin
        if self.Emax==None:
            Max=1
        else:
            Max=self.Emax
        bandgap_range=self.bandmax(self.Ef)
        Max=Max+bandgap_range[1]-bandgap_range[0]
        """0 is set at the VBMax, here Max=inputed max+bandgap"""
        
        xs=[]
        xmarks=[]
        x=0
        for i in range(len(self.sympointNum)):
            if xmarks==[] or x!=xmarks[-1]:
                xmarks.append(x)
                pyplot.plot([x,x],[Min,Max],c='k')
            if self.sympointNum[i]==1 and i!=len(self.sympointNum)-1:
                xs.append(x)
            else:
                for j in range(self.sympointNum[i]):
                    xs.append(x)
                    x+=1 
        zero=bandgap_range[0]
        for ys in self.allbands:
            tmp=[]
            for j in ys:
                tmp.append(j-zero)
            pyplot.plot(xs,tmp)
        print xmarks    
        pyplot.ylim(Min,Max)
        pyplot.xlim(0,xs[-1])
        pyplot.ylabel("Energy(eV)")
        pyplot.xticks(xmarks,symbol)
        pyplot.show()
        
    def readDAT(self,filename):
        return    
    def graph_along_symmetryline(self,region):
        #region from 1 to len()
        '''
        suppose there is 2 symmetry line, there are 3 symmtryPoints. 
        '''
        total_region=len(self.sympointNum)-1
        K=[]
        E=[]
        start=0
        for i in range(region-1):
            start+=self.sympointNum[i]
        end=start+self.sympointNum[region-1]
        for i in range(start,end+1):
                K.append(self.kpoints[i])
        if self.e_zero==None:
            for i in range(self.bandNum):
                E_tmp=[]
                for j in range(start,end+1):
                    E_tmp.append(self.allbands[i][j])
                E.append(E_tmp)
        elif self.e_zero!=None:
            for i in range(self.bandNum):
                E_tmp=[]
                for j in range(start,end+1):
                    E_tmp.append(self.allbands[i][j]-self.e_zero)
                E.append(E_tmp)
        return K,E
        
    def graph_all(self):
        K=self.kpoints
        if self.e_zero==None:
            E=self.allbands
        else:
            E=[]
            for i in len(self.bandNum):
                E_tmp=[]
                for j in self.allbands[i]:
                    E_tmp.append(j-self.e_zero)
                E.append(E_tmp)
        return K,E

def test():
    band=bandplot()
    band.setFermi(6)
    band.Add_Kpoints("0.000 0.000 0.000 10\n-0.268 0.268 0.003 5\n-0.270 0.270 0.459 3\n-0.266 0.266 0.547 10\n0.000 0.000 0.500 5\n0.500 0.500 0.500 10\n0.270 0.730 0.541 1\n0.265 0.734 0.453 5\n0.268 0.732 -0.003 10\n0.500 0.500 0.000 5\n0.000 0.000 0.000 12\n0.000 0.500 0.000 1\n0.000 0.500 0.500 12\n0.000 0.000 0.000 1")
    band.readGNU("InTe.plotbands.dat.gnu")
    band.graph()

"""GUI part"""

class window:
    def __init__(self):
        win=Tk()
        win.resizable(0,0)
        win.title("Plot band structure")
        """define widges"""
        f_D=Frame(win)
        discrip1=Label(f_D,text="this is a program that plot band structure from QE output.  --WH",anchor=W)
        discrip2=Label(f_D,text="1.open the data file such as 'plotbands.gnu'",anchor=W)
        discrip3=Label(f_D,text="2.enter symmetry symbol",anchor=W)
        discrip4=Label(f_D,text="3.paste the symmetry lines used in non-scf calculation",anchor=W)
        discrip1.grid(row=0,sticky=W)
        discrip2.grid(row=1,sticky=W)
        discrip3.grid(row=2,sticky=W)
        discrip4.grid(row=3,sticky=W)
        
        f_B=Frame(win)
        Butt1=Button(f_B,text="load.gnu",width=15,command=self.openFILE)
        Butt2=Button(f_B,text="generate",width=15,command=self.plot)
        Butt1.grid(row=0,column=0)
        Butt2.grid(row=0,column=1)
        
        f_E=Frame(win)
        EminL=Label(f_E,text="E(min):",width=6,anchor=E)
        self.EminE=Entry(f_E,width=10)
        EmaxL=Label(f_E,text="E(max):",width=6,anchor=E)
        self.EmaxE=Entry(f_E,width=10)
        EfL=Label(f_E,text="E(fermi):",width=7,anchor=E)
        self.EfE=Entry(f_E,width=10)
        EminL.grid(row=0,column=0)
        self.EminE.grid(row=0,column=1)
        EmaxL.grid(row=0,column=2)
        self.EmaxE.grid(row=0,column=3)
        EfL.grid(row=0,column=4)
        self.EfE.grid(row=0,column=5)
        
        f_T=Frame(win)
        label1=Label(f_T,text="Data file:",width=10)
        self.DAT=Entry(f_T,width=50)
        self.DAT.insert(END,"No file specified")
        label2=Label(f_T,text="symmetry line points:",width=10)
        self.sym_symbol=Entry(f_T)
        
        self.Input=Text(f_T,height=25,width=52)
        SI=Scrollbar(f_T)
        SI.config(command=self.Input.yview)
        self.Input.config(yscrollcommand=SI.set)
        
        label1.grid(row=0,column=0,sticky=W+E)
        self.DAT.grid(row=0,column=1,columnspan=3,sticky=W+E)
        label2.grid(row=1,column=0,sticky=W+E)
        self.sym_symbol.grid(row=1,column=1,columnspan=2,sticky=W+E)
        self.Input.grid(row=2,column=0,columnspan=2,sticky=W+E)
        SI.grid(row=2,column=2,sticky=N+S)
        """layout"""
        f_D.grid(row=0,sticky=W)
        f_B.grid(row=1,sticky=W)
        f_E.grid(row=2)
        f_T.grid(row=3,sticky=W+E)
        
        win.mainloop()
    def openFILE(self):
        filename=askopenfilename()
        self.DAT.delete(0,END)
        self.DAT.insert(END,filename)
        return
    
    def plot(self):
        plot=bandplot()
        try:
            filename=self.DAT.get()
            plot.readGNU(filename)
        except:
            print "no data specified"
            return
        try:
            symbols=self.sym_symbol.get()
            plot.set_symbol(symbols)
        except:
            print "no symbols specified"
            
        try:
            Ef=float(self.EfE.get())
            plot.setFermi(Ef)
        except:
            print "EF not specified"
            return
        
        try:
            Emin=float(self.EminE.get())
            plot.setY_min(Emin)
        except:
            print "using default Ymin range"
        try:
            Emax=float(self.EmaxE.get())
            plot.setY_max(Emax)
        except:
            print "using default Ymax range"
        
        if True:
            lines=self.Input.get("@0,0",END)
            lines=lines.rstrip()
            plot.Add_Kpoints(lines)


        plot.graph()
        
w=window()

from PyQt4 import QtGui,QtCore
import sys
import pyqtgraph as pg
import numpy as np
from PIL import Image
import pdb
import pickle
import simulator
import time
import math
from PyTango import *

class ViewData(QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(ViewData, self).__init__(parent)
		self.widget=QtGui.QWidget()
		self.widget.setLayout(QtGui.QGridLayout())

		#ni=Image.open('SYN_49a_piston_OK.tif')
		ni=Image.open('DAC4-00002MODD.png')#default_image
		arr=np.array(ni)
		self.imv=pg.ImageView()

		#imv2=pg.ViewBox()
		#self.widget.addItem(imv2)

		buttonNewTarget=QtGui.QPushButton("new target")
		buttonNewTarget.clicked.connect(self.change)
		#buttonNewTarget.move(600,50)

		buttonOpenFile=QtGui.QPushButton("open image")
		buttonOpenFile.clicked.connect(self.openFile)
		#buttonOpenFile.move(600,100)

		buttonWriteToFile=QtGui.QPushButton("write to file")
		buttonWriteToFile.clicked.connect(self.writeData)

		buttonResetROI=QtGui.QPushButton("reset ROI")
		buttonResetROI.clicked.connect(self.resetROI)

		buttonReadFile=QtGui.QPushButton("read file")
		buttonReadFile.clicked.connect(self.readData)

		buttonMovePellets=QtGui.QPushButton("move pellets")
		#buttonMovePellets.clicked.connect(self.moveAll)
		buttonMovePellets.clicked.connect(self.moveAllNew)

		buttonCalibrate=QtGui.QPushButton("calibrate")
		buttonCalibrate.clicked.connect(self.calibrate)

		buttonReArrange=QtGui.QPushButton("rearrange")
		buttonReArrange.clicked.connect(self.rearrange)

		buttonAdd_bs=QtGui.QPushButton("add_bs")
		buttonAdd_bs.clicked.connect(self.add_bs)

		mx='p02/motor/elab.01'#x_motor
		my='p02/motor/elab.02'#y_motor
		gr='p02/register/elab.out08'#io_register
		self.gripper=DeviceProxy(gr)
                self.motox=DeviceProxy(mx)
		self.motoy=DeviceProxy(my)
		self.yBacklash=3.0#backlash
		self.amount=5#amount_of_beamstops
		self.imv.setImage(arr)
		self.roiAll=[]#create_list(roi means region of interest)
		self.roiPos=[]#create_list only for position data
		self.roiSize=[]#create_list which contains updated sizes of rois
		self.roiPosOld=[]#create roi pos list which is later used as buffer
		self.filenames=QtCore.QStringList()
		self.filenames.append('DAC4-00002MODD.png')

		self.roiPos.append([80,50,0])#first_roi_default_position
		self.roiSize.append([20,20])#first_roi_default_size
		self.roiAll.append(pg.CircleROI([80,50,0],[20,20], pen=(15,15)))
		self.roiAll[0].sigRegionChanged.connect(self.update)
		it1=self.imv.addItem(self.roiAll[0])

		self.widget.layout().addWidget(self.imv,0,0,3,3)
		self.widget.layout().addWidget(buttonNewTarget,4,0)
		self.widget.layout().addWidget(buttonOpenFile,4,1)
		self.widget.layout().addWidget(buttonWriteToFile,4,2)
		self.widget.layout().addWidget(buttonResetROI,5,0)
		self.widget.layout().addWidget(buttonMovePellets,5,1)
		self.widget.layout().addWidget(buttonReadFile,5,2)
		self.widget.layout().addWidget(buttonCalibrate,6,0)
		self.widget.layout().addWidget(buttonReArrange,6,1)
		self.widget.layout().addWidget(buttonAdd_bs,6,2)
		#self.widget.layout().addWIdget(imv2,5,5,3,3)
		self.setCentralWidget(self.widget)
		self.show()

	def update(self):
		for x in range(0,len(self.roiAll)):
			#print "circle %i :" %x, self.roiAll[x].pos(), self.roiAll[x].size()
			print self.roiAll[x]
			#pdb.set_trace()
			#self.roiPos[x]=[self.roiAll[x].pos(),0]
			self.roiPos[x]=[self.roiAll[x].pos()[0],self.roiAll[x].pos()[1],0]
			print self.roiPos[x]
			self.roiSize[x]=self.roiAll[x].size()

	def change(self):
		self.roiAll.append(pg.CircleROI([5,5,0], [20,20], pen=(9,15)))
		self.roiAll[len(self.roiAll)-1].sigRegionChanged.connect(self.update)
		self.imv.addItem(self.roiAll[len(self.roiAll)-1])
		self.roiPos.append([5,5,0])
		self.roiSize.append([20,20])
		print self.roiPos

	def showPositions(self):
		print self.roiPos

	def openFile(self):
		#pdb.set_trace()
		fileHandling=QtGui.QFileDialog()
		fileHandling.setFileMode(QtGui.QFileDialog.AnyFile)
		if fileHandling.exec_():
			self.filenames=fileHandling.selectedFiles()
			print self.filenames[0]
			print str(self.filenames[0])
			name=self.filenames[0]
			ni=Image.open(str(name))
			arr=np.array(ni)
			self.imv=pg.ImageView()
			self.imv.setImage(arr)
			self.widget.layout().addWidget(self.imv,0,0,3,3)
			self.roiAll=[]
			self.roiPos=[]
			self.roiSize=[]

	def writeData(self):
		with open('%s.data' %str(self.filenames[0]), 'wb') as f:
			dataContainer=[]
			dataContainer.append(self.filenames[0])
			dataContainer.append(self.roiPos)
			dataContainer.append(self.roiSize)
    			pickle.dump(dataContainer, f)

	def readData(self):
		fileHandling=QtGui.QFileDialog()
		fileHandling.setFileMode(QtGui.QFileDialog.AnyFile)
		if fileHandling.exec_():
			self.filenames=fileHandling.selectedFiles()
			print self.filenames[0]
			print str(self.filenames[0])
			name=self.filenames[0]
		with open(str(name), 'r') as f:
     			data = pickle.load(f)
		self.resetROI()
		fName=data[0]
		self.roiPos=data[1]
		self.roiSize=data[2]
		print fName
		print self.roiPos
		#ni=Image.open(str(fName))
                #arr=np.array(ni)
                #self.imv=pg.ImageView()
                #self.imv.setImage(arr)
                #self.widget.layout().addWidget(self.imv,0,0,3,3)
		for x in range(0,len(self.roiPos)):
			self.roiAll.append(pg.CircleROI([self.roiPos[x][0],self.roiPos[x][1]], [self.roiSize[x][0],self.roiSize[x][1]], pen=(9,15)))
                	self.roiAll[len(self.roiAll)-1].sigRegionChanged.connect(self.update)	
			self.imv.addItem(self.roiAll[len(self.roiAll)-1])

	def movePellets(self):
		print 'movePellets'
		#pdb.set_trace()
		print self.roiPos[0][0]
		print self.roiPos[0][1]
		#print "circle %i :" %x, self.roiAll[0].pos(), self.roiAll[0].size()
		#str1='p02/motor/eh1a.16'
		self.gripper.value=0
		self.motox.position=0
		while(self.motox.state() == DevState.MOVING):
			time.sleep(0.01)
		self.motoy.position=0
                while(self.motoy.state() == DevState.MOVING):
			time.sleep(0.01)
		time.sleep(2)
		self.gripper.value=1
		self.motox.position=self.roiPos[0][0]
		while(self.motoy.state() == DevState.MOVING):
			time.sleep(0.01)
		self.motoy.position=400-self.roiPos[0][1]-self.yBacklash
                while(self.motoy.state() == DevState.MOVING):
			time.sleep(0.01)
		time.sleep(2)

	def moveAll(self):
		#pdb.set_trace()
		self.roiPosOld=self.roiPos
		self.gripper.value=0
		self.motox.position=0
		while(self.motox.state() == DevState.MOVING):
			time.sleep(0.01)
		self.motoy.position=0
                while(self.motoy.state() == DevState.MOVING):
			time.sleep(0.01)
		for i in range (0, len(self.roiPos)):
			self.gripper.value=1
			time.sleep(2)
			self.motox.position=self.roiPos[i][0]
			while(self.motoy.state() == DevState.MOVING):
				time.sleep(0.01)
			self.motoy.position=400-self.roiPos[i][1]-self.yBacklash
			while(self.motoy.state() == DevState.MOVING):
				time.sleep(0.01)
			self.gripper.value = 0
			time.sleep(2)
			self.motox.position=0
			while(self.motox.state() == DevState.MOVING):
				time.sleep(0.01)
			self.motoy.position=0
                	while(self.motoy.state() == DevState.MOVING):
				time.sleep(0.01)

	def move_bs(self, axis, position):
		self.(axis).position=position
			while(self.(axis).state() == DevState.MOVING):
				time.sleep(0.01)
	

        def test(self):
		print self.roiPos

	def make_bs_list(self,amount):
    		bs_list=[]
    		for i in range(0,amount):
        		bs_list.append([0,0+i*10])
    		return bs_list

	def calc_ind(self,x):
    		for i in range(0,len(x)):
        		x[i][2]=math.sqrt(pow(x[i][0],2)+pow(x[i][1],2))
    		return x

	def sort_ind(self,x,item_ind):
    		x=sorted(x, key=lambda item: item[item_ind])
    		return x
	
	def list_cmp(self,o_list,n_list):
		ind=[]
		j=0
		for i in range(0,len(o_list)):
			if (o_list[i]==n_list[i]) == False:
				ind.append(i)
				j=+1
		return ind

	def calc_alpha(self,xn,x0,yn,y0):
        	alpha=180/math.pi*math.atan(float(yn-y0)/float(xn-x0))
        	#alpha=math.atan(3/2)
        	return alpha

	def calc_vec_len(self,xn,x0,yn,y0):
        	length=math.sqrt(pow((xn-x0),2)+pow((yn-y0),2))
        	return length

	def calc_alpha_mod(self,alpha_i,alpha_j):
        	alpha_mod=(alpha_j-alpha_i)/2+alpha_i
        	return alpha_mod


	def add_bs(self):
        	newList=[]
		bufList=[]
		bufList=self.roiPos
        	bs=[10,10]
		target=[]
        	#self.roiPos=self.calc_ind(self.roiPos)
		for i in range(0, len(bufList)):
			bufList[i][2]=self.calc_vec_len(bufList[i][0],bs[0],bufList[i][1],bs[1])
        	target.append(bufList[len(bufList)-1])
        	target[0].append(0)
		print bufList
		print target
        	for i in range(0,len(bufList)):
                	if bufList[i][2]<target[0][2]:
                        	newList.append(bufList[i])
        	target[0][3]=self.calc_alpha(target[0][0],bs[0],target[0][1],bs[1])
        	for i in range(0,len(newList)):
                	newList[i].append(0)
                	newList[i][3]=newList[0][2]*math.tan(math.pi/180*self.calc_alpha(newList[i][0],bs[0],newList[i][1],bs[1])-target[0][3])
        	print newList
		
	def rearrange(self):
		ch_list=[]
		ch_ind=self.list_cmp(self.roiPos,self.roiPosOld)
		for i in range(0,len(ch_ind)):
			ch_list.append(self.roiPosOld[ch_ind[i]])
		for i in range(0,len(ch_list)):
			self.gripper.value = 0
                	self.motox.position = ch_list[i][0]
			print ch_list[i][0]
			while (self.motox.state() == DevState.MOVING):
				time.sleep(0.01)
			self.motoy.position = ch_list[i][1]
			print ch_list[i][1]
			while (self.motoy.state() == DevState.MOVING):
				time.sleep(0.01)
			self.gripper.value = 1
			time.sleep(2)
			self.motox.position = self.roiPos[i][0]
			print self.roiPos[i][0]
			while (self.motoy.state() == DevState.MOVING):
				time.sleep(0.01)
			self.motoy.position = 400 - self.roiPos[i][1]
			print self.roiPos[i][1]
			while (self.motoy.state() == DevState.MOVING):
				time.sleep(0.01)
			#self.motoy.position = 400 - self.roiPos[i][1] - self.yBacklash
			#while (self.motoy.state() == DevState.MOVING):
			#	time.sleep(0.01)
			self.gripper.value = 0
			time.sleep(2)
			print "x0"
			self.motox.position = 0
                	while (self.motox.state() == DevState.MOVING):
                    		time.sleep(0.01)
                	self.motoy.position = 0
			print "y0"
                	while (self.motoy.state() == DevState.MOVING):
                    		time.sleep(0.01)
		self.roiPosOld=self.roiPos

		

        def moveAllNew(self):
		#pdb.set_trace()
                self.gripper.value = 0
		time.sleep(2)
		self.roiPosOld=self.roiPos
		bs_list=[]
		bs_list=self.make_bs_list(self.amount)
		print self.roiPos
		self.roiPos=self.calc_ind(self.roiPos)
		self.roiPos=self.sort_ind(self.roiPos,2)
		# pdb.set_trace()

		for i in range(0, len(self.roiPos)):
			print "beamstop",bs_list[i][0]
                	self.motox.position = bs_list[i][0]
			while (self.motox.state() == DevState.MOVING):
				time.sleep(0.01)
			self.motoy.position = bs_list[i][1]
			print bs_list[i][1]
			while (self.motoy.state() == DevState.MOVING):
				time.sleep(0.01)
			self.gripper.value = 1
			time.sleep(2)
			self.motox.position = self.roiPos[i][0]
			print self.roiPos[i][0]
			while (self.motox.state() == DevState.MOVING):
				time.sleep(0.01)
			self.motoy.position = 400 - self.roiPos[i][1]
			print self.roiPos[i][1]
			while (self.motoy.state() == DevState.MOVING):
				time.sleep(0.01)
			#self.motoy.position = self.roiPos[i][1] - self.yBacklash
			#print "backlash"
			#while (self.motoy.state() == DevState.MOVING):
			#	time.sleep(0.01)
			self.gripper.value = 0
			time.sleep(2)
			print "ready"
		self.motox.position = 0
		self.motoy.position = 0
		self.roiPosold=self.roiPos
		
	def calibrate(self):
		slew_buf_x=self.motox.slewrate
		slew_buf_y=self.motox.slewrate
		self.motox.slewrate=400
		self.motoy.slewrate=400
		print 'calibrate motors ....'
		self.motox.moveToCwLimit()
		while(self.motox.state() == DevState.MOVING):
			time.sleep(0.01)
		self.motox.calibrate(0)
		self.motoy.moveToCwLimit()
		while(self.motox.state() == DevState.MOVING):
			time.sleep(0.01)
		self.motoy.calibrate(0)
		print "write back slew rate"
		self.motox.slewrate=slew_buf_x
		self.motoy.slewrate=slew_buf_y

	def resetROI(self):
		for x in range(0,len(self.roiAll)):	
			self.imv.removeItem(self.roiAll[x])
		self.roiAll=[]
		self.roiPos=[]
		print "deleted all setted ROI"

	

def main():
	app=QtGui.QApplication(sys.argv)
	vd=ViewData()
	vd.show()
	app.exec_()

if __name__ == '__main__':
	main()


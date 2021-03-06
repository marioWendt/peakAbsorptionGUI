from PyQt4 import QtGui, QtCore
import sys
import pyqtgraph as pg
import numpy as np
from PIL import Image
import pickle
import time
import math
import pdb
#import tango

#mx = 'p02/motor/elab.01'  # x_motor
#my = 'p02/motor/elab.02'  # y_motor
#gr = 'p02/register/elab.out08'  # io_register
#self.yBacklash = 3.0  # backlash
#self.amount = 5  # amount_of_beamstops
#self.bs_diam = 5
#self.dist = 15 #minimum distance between bs


class ViewData(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ViewData, self).__init__(parent)
        self.widget = QtGui.QWidget()
        self.widget.setLayout(QtGui.QGridLayout())

        ni = Image.open('DAC4-00002MODD.png')  # default_image
        arr = np.array(ni)
        self.imv = pg.ImageView()

        button_new_target = QtGui.QPushButton("new target")
        button_new_target.clicked.connect(self.change)

        button_open_file = QtGui.QPushButton("open image")
        button_open_file.clicked.connect(self.open_file)

        button_write_to_file = QtGui.QPushButton("write to file")
        button_write_to_file.clicked.connect(self.write_data)

        button_reset_roi = QtGui.QPushButton("reset ROI")
        button_reset_roi.clicked.connect(self.reset_roi)

        button_read_file = QtGui.QPushButton("read file")
        button_read_file.clicked.connect(self.read_data)

        button_move_pellets = QtGui.QPushButton("move pellets")
        # button_move_pellets.clicked.connect(self.moveAll)
        button_move_pellets.clicked.connect(self.move_all_new)

        button_calibrate = QtGui.QPushButton("calibrate")
        button_calibrate.clicked.connect(self.calibrate)

        button_re_arrange = QtGui.QPushButton("rearrange")
        button_re_arrange.clicked.connect(self.rearrange)

        button_add_bs = QtGui.QPushButton("add_bs")
        button_add_bs.clicked.connect(self.test_find_path)

        mx = 'p02/motor/elab.01'  # x_motor
        my = 'p02/motor/elab.02'  # y_motor
        gr = 'p02/register/elab.out08'  # io_register
        self.col = 1
        #self.gripper = tango.DeviceProxy(gr)
        #self.motox = tango.DeviceProxy(mx)
        #self.motoy = tango.DeviceProxy(my)
        self.yBacklash = 3.0  # backlash
        self.amount = 5  # amount_of_beamstops
        self.imv.setImage(arr)
        self.roiAll = []  # create_list(roi means region of interest)
        self.roiPos = []  # create_list only for position data
        self.roiSize = []  # create_list which contains updated sizes of rois
        self.roiPosOld = []  # create roi pos list which is later used as buffer
        self.filenames = QtCore.QStringList()
        self.filenames.append('DAC4-00002MODD.png')

        self.roiPos.append([80, 50, 0])  # first_roi_default_position
        self.roiSize.append([20, 20])  # first_roi_default_size
        self.roiAll.append(pg.CircleROI([80, 50, 0], [20, 20], pen=(self.col, 15)))
        self.roiAll[0].sigRegionChanged.connect(self.update)
        it1 = self.imv.addItem(self.roiAll[0])

        self.widget.layout().addWidget(self.imv, 0, 0, 3, 3)
        self.widget.layout().addWidget(button_new_target, 4, 0)
        self.widget.layout().addWidget(button_open_file, 4, 1)
        self.widget.layout().addWidget(button_write_to_file, 4, 2)
        self.widget.layout().addWidget(button_reset_roi, 5, 0)
        self.widget.layout().addWidget(button_move_pellets, 5, 1)
        self.widget.layout().addWidget(button_read_file, 5, 2)
        self.widget.layout().addWidget(button_calibrate, 6, 0)
        self.widget.layout().addWidget(button_re_arrange, 6, 1)
        self.widget.layout().addWidget(button_add_bs, 6, 2)
        self.setCentralWidget(self.widget)
        self.show()

    def update(self):
        for x in range(0, len(self.roiAll)):
            # print "circle %i :" %x, self.roiAll[x].pos(), self.roiAll[x].size()
            #print self.roiAll[x]
            # self.roiPos[x]=[self.roiAll[x].pos(),0]
            self.roiPos[x] = [self.roiAll[x].pos()[0], self.roiAll[x].pos()[1], 0]
            print self.roiPos[x]
            self.roiSize[x] = self.roiAll[x].size()

    def change(self):
        self.col+=1
        print self.col
        self.roiAll.append(pg.CircleROI([5, 5, 0], [20, 20], pen=(self.col, 15)))
        self.roiAll[len(self.roiAll) - 1].sigRegionChanged.connect(self.update)
        self.imv.addItem(self.roiAll[len(self.roiAll) - 1])
        self.roiPos.append([5, 5, 0])
        self.roiSize.append([20, 20])
        print self.roiPos

    def show_positions(self):
        print self.roiPos

    def open_file(self):
        file_handling = QtGui.QFileDialog()
        file_handling.setFileMode(QtGui.QFileDialog.AnyFile)
        if file_handling.exec_():
            self.filenames = file_handling.selectedFiles()
            print self.filenames[0]
            print str(self.filenames[0])
            name = self.filenames[0]
            ni = Image.open(str(name))
            arr = np.array(ni)
            self.imv = pg.ImageView()
            self.imv.setImage(arr)
            self.widget.layout().addWidget(self.imv, 0, 0, 3, 3)
            self.roiAll = []
            self.roiPos = []
            self.roiSize = []

    def write_data(self):
        with open('%s.data' % str(self.filenames[0]), 'wb') as f:
            data_container = [self.filenames[0], self.roiPos, self.roiSize]
            pickle.dump(data_container, f)

    def read_data(self):
        file_handling = QtGui.QFileDialog()
        file_handling.setFileMode(QtGui.QFileDialog.AnyFile)
        if file_handling.exec_():
            self.filenames = file_handling.selectedFiles()
            print self.filenames[0]
            print str(self.filenames[0])
            name = self.filenames[0]
        with open(str(name), 'r') as f:
            data = pickle.load(f)
        self.reset_roi()
        f_name = data[0]
        self.roiPos = data[1]
        self.roiSize = data[2]
        print f_name
        print self.roiPos
        for x in range(0, len(self.roiPos)):
            self.roiAll.append(
                pg.CircleROI([self.roiPos[x][0], self.roiPos[x][1]], [self.roiSize[x][0], self.roiSize[x][1]],
                             pen=(9, 15)))
            self.roiAll[len(self.roiAll) - 1].sigRegionChanged.connect(self.update)
            self.imv.addItem(self.roiAll[len(self.roiAll) - 1])

    def move_pellets(self):
        print 'movePellets'
        print self.roiPos[0][0]
        print self.roiPos[0][1]
        # print "circle %i :" %x, self.roiAll[0].pos(), self.roiAll[0].size()
        self.gripper.value = 0
        self.motox.position = 0
        self.wait_move(self.motox)
        self.motoy.position = 0
        self.wait_move(self.motoy)
        time.sleep(2)
        self.gripper.value = 1
        self.motox.position = self.roiPos[0][0]
        self.wait_move(self.motoy)
        self.motoy.position = 400 - self.roiPos[0][1] - self.yBacklash
        self.wait_move(self.motoy)
        time.sleep(2)

    def move_all(self):
        # pdb.set_trace()
        self.roiPosOld = self.roiPos
        self.gripper.value = 0
        self.motox.position = 0
        self.wait_move(self.motox)
        self.motoy.position = 0
        self.wait_move(self.motoy)
        for i in range(0, len(self.roiPos)):
            self.gripper.value = 1
            time.sleep(2)
            self.motox.position = self.roiPos[i][0]
            self.wait_move(self.motoy)
            self.motoy.position = 400 - self.roiPos[i][1] - self.yBacklash
            self.wait_move(self.motoy)
            self.gripper.value = 0
            time.sleep(2)
            self.motox.position = 0
            self.wait_move(self.motox)
            self.motoy.position = 0
            self.wait_move(self.motoy)

    def wait_move(self, motor):
        while motor.state() == tango.DevState.MOVING:
            time.sleep(0.01)

    def move_bs(self, axis, position):
        self.axis.position = position
        while self.axis.state() == tango.DevState.MOVING:
            time.sleep(0.01)


    def test(self):
        print self.roiPos


    def make_bs_list(self, amount):
        bs_list = []
        for i in range(0, amount):
            bs_list.append([0, 0 + i * 10])
        return bs_list


    def calc_ind(self, x):
        for i in range(0, len(x)):
            x[i][2] = math.sqrt(pow(x[i][0], 2) + pow(x[i][1], 2))
        return x


    def sort_ind(self, x, item_ind):
        x = sorted(x, key=lambda item: item[item_ind])
        return x


    def list_cmp(self, o_list, n_list):
        ind = []
        j = 0
        for i in range(0, len(o_list)):
            if not(o_list[i] == n_list[i]):
                ind.append(i) #TODO: sure you want to append i? j is not used
                j = +1 #TODO: this just assigns 1 to j
        return ind


    def calc_alpha(self, xn, x0, yn, y0):
        alpha = 180 / math.pi * math.atan(float(yn - y0) / float(xn - x0))
        # alpha=math.atan(3/2)
        print xn,x0
        return alpha


    def calc_vec_len(self, xn, x0, yn, y0):
        length = math.sqrt(pow((xn - x0), 2) + pow((yn - y0), 2))
        return length


    def calc_alpha_mod(self, alpha_i, alpha_j):
        alpha_mod = (alpha_j - alpha_i) / 2 + alpha_i
        return alpha_mod


    def add_bs(self):
        #QtCore.pyqtRemoveInputHook()
        #pdb.set_trace()
        new_list = []
        buf_list = self.roiPos
        bs = [10, 10]
        target = []
        # self.roiPos=self.calc_ind(self.roiPos)
        for i in range(0, len(buf_list)):
            buf_list[i][2] = self.calc_vec_len(buf_list[i][0], bs[0], buf_list[i][1], bs[1])
        target.append(buf_list[len(buf_list) - 1])
        target[0].append(0)
        print "buf_list",buf_list
        print "target",target
        for i in range(0, len(buf_list)):
            if buf_list[i][2] < target[0][2]:
                new_list.append(buf_list[i])
        target[0][3] = self.calc_alpha(target[0][0], bs[0], target[0][1], bs[1])
        for i in range(0, len(new_list)):
            new_list[i].append(0)
            new_list[i][3] = new_list[0][2] * math.tan(
                math.pi / 180 * self.calc_alpha(new_list[i][0], bs[0], new_list[i][1], bs[1]) - target[0][3])
        print "new_list",new_list

    def col_check(self,next_bs,used_bs,target): #next_bs is the startposition of the next unset bs, bs_used contains all bs on the field, target is the next desired position
        #QtCore.pyqtRemoveInputHook() #for debugging
        #pdb.set_trace() #for debugging
        col_issues = [] #captures colliding beamstops in a list
        vec_target=self.calc_vec_len(next_bs[0],target[0],next_bs[1],target[1]) #determine the distance between next_bs and target
        for i in range(0, len(used_bs)): #
            next_vec=self.calc_vec_len(used_bs[i][0],next_bs[0],used_bs[i][1],next_bs[1]) #determine the distance between next_bs and all set bs
            if next_vec < (vec_target+25): #filter: if shorter then vec_target it is not relevant
                alpha_target=self.calc_alpha(target[0],next_bs[0],target[1],next_bs[1]) #calculates angle of horizontal base line of next_bs regarding target position
                alpha_next=self.calc_alpha(used_bs[i][0],next_bs[0],used_bs[i][1],next_bs[1]) #calculates angle of horizontal base line of next_bs regarding used_bs
                alpha_check=alpha_next-alpha_target #calculate relativ angle betwenn alpha_target and alpha_next
                pass_distance=next_vec*math.tan(math.pi/180*alpha_check) #now we can calculate the distance
                print "pass distance ", pass_distance
                if abs(pass_distance) < 15: #now we can check for issues
                    used_bs[i][2]=next_vec #put the issues in a list
                    col_issues.append(used_bs[i])
                    print "col_issues", col_issues

        if len(col_issues) > 1:
            col_issues=self.sort_ind(col_issues, 2) #sort the list 
        #pdb.set_trace()
        #if len(col_issues)>0: #this if block was just for testing the bypass function
        #    bypass=self.calc_bypass(next_bs,col_issues,20)
        return col_issues

    def calc_bypass(self,next_bs,col_issues,used_bs,dist):
        test=[]
        alpha_next=self.calc_alpha(col_issues[0][0],next_bs[0],col_issues[0][1],next_bs[1])
        new_x=dist*math.cos(90-(math.pi/180*alpha_next))+col_issues[0][0]
        new_y=dist*math.sin(90-(math.pi/180*alpha_next))+col_issues[0][1]
        test=self.col_check(next_bs,used_bs,[new_x,new_y])
        print len(test)
        if len(test)>0:
            new_x=2*dist*math.cos(90-(math.pi/180*alpha_next))+col_issues[0][0]
            new_y=2*dist*math.sin(90-(math.pi/180*alpha_next))+col_issues[0][1]

        newer_y=dist/math.sin(90-(math.pi/180*alpha_next))+col_issues[0][1]
        #return [0.001+col_issues[0][0],newer_y]# will be changed to [col_issues[0][0],newer_y] and newer_y will be renamed
        return [new_x,new_y]

    def calc_bypass_new(self,next_bs,col_issues,used_bs,target,dist):
        i=0
        j=0
        alpha_target=self.calc_alpha(target[0],next_bs[0],target[1],next_bs[1])
        print "alpha Target ",alpha_target
        new_x=(-1)*(dist*math.cos(math.pi/180*alpha_target))+col_issues[0][0]
        new_y=(dist*math.sin(math.pi/180*alpha_target))+col_issues[0][1]
        test=self.col_check(next_bs,used_bs,[new_x,new_y])
        if len(test)>0:
            while len(test)>0:
                i+=1
                if i <5:
                    print i
                    new_x=(-1)*(i*dist*math.cos((math.pi/180*alpha_target)+i))+col_issues[0][0]
                    new_y=(i*dist*math.sin((math.pi/180*alpha_target)+i))+col_issues[0][1]
                    test=self.col_check(next_bs,used_bs,[new_x,new_y])
                if i>=5:
                    j+=1
                    new_x=(j*dist*math.cos((math.pi/180*alpha_target)+j))+col_issues[0][0]
                    new_y=(-1)*(j*dist*math.sin((math.pi/180*alpha_target)+j))+col_issues[0][1]
                    test=self.col_check(next_bs,used_bs,[new_x,new_y])
                print new_x," ",new_y
        return [new_x,new_y]

    def find_path(self,target,next_bs,used_bs,dist):#first try
        QtCore.pyqtRemoveInputHook() #for debugging
        pdb.set_trace() #for debugging
        kascade=[]
        kascade.append(target)
        col_issues=[]
        col_issues=self.col_check(next_bs,used_bs,target)
        if len(col_issues) > 0:
            while len(col_issues) > 0:
                bypass=self.calc_bypass_new(next_bs,col_issues,used_bs,target,dist)

                kascade.append(bypass)
                next_bs=bypass
                col_issues=self.col_check(next_bs,used_bs,target)
        print kascade,"kascade done"
        return kascade

    def test_find_path(self):
        kaskade=self.find_path([264,208],[10,10],self.roiPos,25)


    def rearrange(self):
        ch_list = []
        ch_ind = self.list_cmp(self.roiPos, self.roiPosOld)
        for i in range(0, len(ch_ind)):
            ch_list.append(self.roiPosOld[ch_ind[i]])
        for i in range(0, len(ch_list)):
            self.gripper.value = 0
            self.motox.position = ch_list[i][0]
            print ch_list[i][0]
            self.wait_move(self.motox)
            self.motoy.position = ch_list[i][1]
            print ch_list[i][1]
            self.wait_move(self.motoy)
            self.gripper.value = 1
            time.sleep(2)
            self.motox.position = self.roiPos[i][0]
            print self.roiPos[i][0]
            self.wait_move(self.motoy)
            self.motoy.position = 400 - self.roiPos[i][1]
            print self.roiPos[i][1]
            self.wait_move(self.motoy)
            # self.motoy.position = 400 - self.roiPos[i][1] - self.yBacklash
            # while (self.motoy.state() == tango.DevState.MOVING):
            #	time.sleep(0.01)
            self.gripper.value = 0
            time.sleep(2)
            print "x0"
            self.motox.position = 0
            self.wait_move(self.motox)
            self.motoy.position = 0
            print "y0"
            self.wait_move(self.motoy)
        self.roiPosOld = self.roiPos


    def move_all_new(self):
        # pdb.set_trace()
        self.gripper.value = 0
        time.sleep(2)
        self.roiPosOld = self.roiPos
        bs_list = self.make_bs_list(self.amount)
        print self.roiPos
        self.roiPos = self.calc_ind(self.roiPos)
        self.roiPos = self.sort_ind(self.roiPos, 2)
        # pdb.set_trace()

        for i in range(0, len(self.roiPos)):
            print "beamstop", bs_list[i][0]
            self.motox.position = bs_list[i][0]
            self.wait_move(self.motox)
            self.motoy.position = bs_list[i][1]
            print bs_list[i][1]
            self.wait_move(self.motoy)
            self.gripper.value = 1
            time.sleep(2)
            self.motox.position = self.roiPos[i][0]
            print self.roiPos[i][0]
            self.wait_move(self.motox)
            self.motoy.position = 400 - self.roiPos[i][1]
            print self.roiPos[i][1]
            self.wait_move(self.motoy)
            # self.motoy.position = self.roiPos[i][1] - self.yBacklash
            # print "backlash"
            # while (self.motoy.state() == tango.DevState.MOVING):
            #	time.sleep(0.01)
            self.gripper.value = 0
            time.sleep(2)
            print "ready"
        self.motox.position = 0
        self.motoy.position = 0
        self.roi_pos_old = self.roiPos


    def calibrate(self):
        slew_buf_x = self.motox.slewrate
        slew_buf_y = self.motox.slewrate
        self.motox.slewrate = 400
        self.motoy.slewrate = 400
        print 'calibrate motors ....'
        self.motox.moveToCwLimit()
        self.wait_move(self.motox)
        self.motox.calibrate(0)
        self.motoy.moveToCwLimit()
        self.wait_move(self.motox) #TODO: sure you waiut for x again?
        self.motoy.calibrate(0) #TODO: don't use calibrate
        print "write back slew rate"
        self.motox.slewrate = slew_buf_x
        self.motoy.slewrate = slew_buf_y


    def reset_roi(self):
        for x in range(0, len(self.roiAll)):
            self.imv.removeItem(self.roiAll[x])
        self.roiAll = []
        self.roiPos = []
        print "deleted all set ROI"


def main():
    app = QtGui.QApplication(sys.argv)
    vd = ViewData()
    vd.show()
    app.exec_()


if __name__ == '__main__':
    main()

# pip2 install wxPython scipy
#https://github.com/amanraj/Handwritten-Numeral-Recognition-Using-Fuzzy-Logic/blob/master/README.md
import math
import wx
from scipy import stats

class Segment():

    def __init__(self, parent, coord):
        self.coord = list(coord)
        self.parent = parent
        self.calc_boundary()
        self.calc_straightness()
        self.calc_len()
        self.calc_line_props()
        self.calc_pos()
        self.calc_UL()
        self.calc_AL()
        self.calc_CL()
        self.calc_DL()
        self.debug()

    def debug(self):

        print 'x_max is -----', self.x_max
        print 'y_max is -----', self.y_max
        print 'x_min is -----', self.x_min
        print 'y_min is -----', self.y_min
        print 'x_center is', self.x_center
        print 'y_center is', self. y_center
        print 'mew horizontal position is ', self.mew_HP
        print 'mew vertical position is ', self.mew_VP
        print 'distance end to end is ', self.dist_fi
        print 'total distance is ', self.tot_dist
        print 'mew straightness is ', self.mew_STRAIGHTNESS
        print 'mew arcness is ', self.mew_ARCNESS
        print 'avg slope is ', self.AVG_SLOPE
        print 'mew verticalness is ', self.mew_VERTICAL
        print 'mew horizontalness is ', self.mew_HORIZONTAL
        print 'mew posive slope is ', self.mew_PS
        print 'mew negative slope is ', self.mew_NS
        print 'mew horizontal length is ', self.mew_HLEN
        print 'mew slant length is ', self.mew_SLEN
        print 'mew vertical length', self.mew_VLEN
        print 'mew clike is ', self.mew_CL
        print 'mew d like is ', self.mew_DL
        print 'mew a like is ', self.mew_AL
        print 'mew u like is ', self.mew_UL
        #print 'mew o like is ', self.mew_OL
        #print 'mew hsl', self.mew_HSL
        #print 'mew wsl', self.mew_WSL


    def calc_boundary (self):
        x_list = []
        y_list = []
        for (x,y) in self.coord:
            x_list.append(x)
            y_list.append(y)
        self.x_max = max(x_list)
        self.y_max = max(y_list)
        self.x_min = min(x_list)
        self.y_min = min(y_list)
        self.x_center = (self.x_max+self.x_min)/2
        self.y_center = (self.y_max+self.y_min)/2
        slope_avg, intercept, r_value, p_value, slope_std_error = stats.linregress(x_list, y_list)
        self.AVG_SLOPE = slope_avg

        return

    def calc_straightness(self):
        self.tot_dist = 0
        for i in range(0,len(self.coord)-1,1):
            x1 = self.coord[i][0]
            y1 = self.coord[i][1]
            x2 = self.coord[i+1][0]
            y2 = self.coord[i+1][1]
            self.tot_dist = self.tot_dist + math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )
        self.dist_fi = math.sqrt( (self.coord[-1][0] - self.coord[0][0])**2 + (self.coord[-1][1] - self.coord[0][1])**2 )
        self.mew_STRAIGHTNESS = float(self.dist_fi/self.tot_dist)
        self.mew_ARCNESS = 1-self.mew_STRAIGHTNESS
        return

    def lamda_fn(self,x,b,c):

        if ((c-float(b)/2) <= (x*(c+float(b)/2)) ):
            return 1 - 2*math.fabs((x-c)/float(b))
        else:
            return 0

    def calc_line_props(self):
        psi1 = float(math.degrees(math.atan(math.fabs(self.AVG_SLOPE))))
        x_i_minus_step = self.coord[0][0]
        y_i_minus_step = self.coord[0][1]
        x_i = self.coord[-1][0]
        y_i = self.coord[-1][1]

        if((x_i_minus_step <= x_i) and (y_i_minus_step <= y_i)):
                theta1 = psi1
        elif ((x_i_minus_step >= x_i) and (y_i_minus_step <= y_i)):
                theta1 = 180 - psi1
        elif ((x_i_minus_step >= x_i) and (y_i_minus_step >= y_i)):
                theta1 = 180 + psi1
        elif ((x_i_minus_step <= x_i) and (y_i_minus_step >= y_i)):
                theta1 = 360 - psi1
        else:
                theta1 = psi1


        self.mew_VERTICAL = max(self.lamda_fn(theta1, 90, 90), self.lamda_fn(theta1, 90, 270))
        self.mew_HORIZONTAL = max(self.lamda_fn(theta1, 90, 0), self.lamda_fn(theta1, 90, 180), self.lamda_fn(theta1, 90, 360))
        self.mew_PS = max(self.lamda_fn(theta1, 90, 45), self.lamda_fn(theta1, 90, 225))
        self.mew_NS = max(self.lamda_fn(theta1, 90, 135), self.lamda_fn(theta1, 90, 315))

    def calc_len(self):
        self.mew_HLEN = float(self.dist_fi)/(self.parent.x_max - self.parent.x_min)
        self.mew_VLEN = float(self.dist_fi)/(self.parent.y_max - self.parent.y_min)
        self.mew_SLEN = float(self.dist_fi)/(math.sqrt( (self.parent.x_max - self.parent.x_min)**2 + (self.parent.y_max - self.parent.y_min)**2 ))
        if (self.mew_HLEN > 1):
            self.mew_HLEN = 1
        if (self.mew_VLEN > 1):
            self.mew_VLEN = 1
        if (self.mew_SLEN > 1):
            self.mew_SLEN = 1

    def calc_pos(self):
        self.mew_HP = float((self.x_center - self.parent.x_min))/(self.parent.x_max - self.parent.x_min)
        self.mew_VP = float((self.y_center - self.parent.y_min))/(self.parent.y_max - self.parent.y_min)

    def calc_AL(self):
        ys=self.coord[0][1]
        ye=self.coord[-1][1]
        condition=(ys+ye)/2
        sum=0.0
        for coord in self.coord:
            if(coord[1]>condition):
                sum=sum+1
        sum=sum/len(self.coord)
        self.mew_AL=min(1,sum)

    def calc_CL(self) :
        xs=self.coord[0][0]
        xe=self.coord[-1][0]
        condition=(xs+xe)/2
        sum=0.0
        for coord in self.coord:
            if(coord[0]<condition):
                sum=sum+1
        sum=sum/len(self.coord)
        self.mew_CL=min(1,sum)

    def calc_DL(self):
        xs=self.coord[0][0]
        xe=self.coord[-1][0]
        condition=(xs+xe)/2
        sum=0.0
        for coord in self.coord:
            if(coord[0]>condition):
                sum=sum+1
        sum=sum/len(self.coord)
        self.mew_DL=min(1,sum)

    def calc_UL(self):
        ys=self.coord[0][1]
        ye=self.coord[-1][1]
        condition=(ys+ye)/2
        sum=0.0
        for coord in self.coord:
            if(coord[1]<condition):
                sum=sum+1
        sum=sum/len(self.coord)
        self.mew_UL=min(1,sum)

    def mem_HP(self,hp, prop):
        if (prop == 'RIGHT'):
            if (hp>=0.7 and hp<=1):
                return math.fabs((hp-0.7)*(10/3))
            elif (hp>1):
                return 1
            else:
                return 0
        elif (prop == 'RIGHT_CENTER'):
            if ((hp >= 0.6 and hp <= 0.75)):
                return math.fabs((hp-0.6)*(20/3))
            elif ((hp>=0.75) and (hp<= 0.9)):
                return math.fabs((hp-0.9)*(-20/3))
            else:
                return 0
        elif (prop == 'CENTER'):
            if ((hp >= 0.3) and (hp <= 0.5)):
                return math.fabs((hp - 0.3)*(5))
            elif ((hp >= 0.5) and (hp <= 0.7)):
                return math.fabs((hp - 0.7)*(-5))
            else:
                return 0

        elif (prop == 'LEFT_CENTER'):
            if ((hp >= 0.1 and hp <= 0.25)):
                return math.fabs((hp-0.1)*(20/3))
            elif ((hp>=0.25) and (hp<= 0.4)):
                return math.fabs((hp-0.4)*(-20/3))
            else:
                return 0

        elif (prop == 'LEFT'):
            if (hp<=0.3 and hp>=0):
                return math.fabs((hp-0.3)*(-10/3))
            elif (hp<0):
                return 1
            else:
                return 0

    def mem_VP(self,hp, prop):
        if (prop == 'TOP'):
            if (hp>=0.7 and hp<=1):
                return math.fabs((hp-0.7)*(10/3))
            elif(hp>1):
                return 1
            else:
                return 0
        elif (prop == 'SLIGHT_TOP'):
            if((hp >= 0.75) and (hp <= 0.85)):
                return math.fabs((hp-0.75)*(10))
            elif ((hp >= 0.85) and (hp <= 0.95)):
                return math.fabs((hp-0.95)*(-10))
            else:
                return 0

        elif (prop == 'TOP_CENTER'):
            if ((hp >= 0.6 and hp <= 0.75)):
                return math.fabs((hp-0.6)*(20/3))
            elif ((hp>=0.75) and (hp<= 0.9)):
                return math.fabs((hp-0.9)*(-20/3))
            else:
                return 0
        elif (prop == 'CENTER'):
            if ((hp >= 0.3) and (hp <= 0.5)):
                return math.fabs((hp - 0.3)*(5))
            elif ((hp >= 0.5) and (hp <= 0.7)):
                return math.fabs((hp - 0.7)*(-5))
            else:
                return 0

        elif (prop == 'BOTTOM_CENTER'):
            if ((hp >= 0.1 and hp <= 0.25)):
                return math.fabs((hp-0.1)*(20/3))
            elif ((hp>=0.25) and (hp<= 0.4)):
                return math.fabs((hp-0.4)*(-20/3))
            else:
                return 0

        elif (prop == 'BOTTOM'):
            if (hp<=0.3 and hp>=0):
                return math.fabs((hp-0.3)*(-10/3))
            elif(hp<0):
                return 1
            else:
                return 0

    def mem_UL(self,ul , prop):
        if (prop == 'HIGH'):
            if (ul >= 0.8):
                return 1
            elif (ul <= 0.8 and ul>= 0.6):
                return math.fabs((ul - 0.6)*(5))
            else:
                return 0
        elif (prop == 'MEDIUM'):
            if ((ul >= 0.3) and (ul <= 0.5)):
                return math.fabs((ul - 0.3)*(5))
            elif (ul >= 0.5 and ul<= 0.7):
                return math.fabs((ul - 0.7)*(-5))
            else:
                return 0
        elif (prop == 'LOW'):
            if (ul <=0.4 and ul>=0):
                return math.fabs((ul - 0.4)*(2.5))
            else:
                return 0

    def mem_CL(self,ul , prop):
        if (prop == 'HIGH'):
            if (ul >= 0.8):
                return 1
            elif (ul <= 0.8 and ul>= 0.6):
                return math.fabs((ul - 0.6)*(5))
            else:
                return 0
        elif (prop == 'MEDIUM'):
            if ((ul >= 0.3) and (ul <= 0.5)):
                return math.fabs((ul - 0.3)*(5))
            elif (ul >= 0.5 and ul<= 0.7):
                return math.fabs((ul - 0.7)*(-5))
            else:
                return 0
        elif (prop == 'LOW'):
            if (ul <=0.4 and ul>=0):
                return math.fabs((ul - 0.4)*(-2.5))
            else:
                return 0

    def mem_DL(self,ul , prop):
        if (prop == 'HIGH'):
            if (ul >= 0.8):
                return 1
            elif (ul <= 0.8 and ul>= 0.6):
                return math.fabs((ul - 0.6)*(5))
            else:
                return 0
        elif (prop == 'MEDIUM'):
            if ((ul >= 0.3) and (ul <= 0.5)):
                return math.fabs((ul - 0.3)*(5))
            elif (ul >= 0.5 and ul<= 0.7):
                return math.fabs((ul - 0.7)*(-5))
            else:
                return 0
        elif (prop == 'LOW'):
            if (ul <=0.4 and ul>=0):
                return math.fabs((ul - 0.4)*(-2.5))
            else:
                return 0

    def mem_AL(self,ul , prop):
        if (prop == 'HIGH'):
            if (ul >= 0.8):
                return 1
            elif (ul <= 0.8 and ul>= 0.6):
                return math.fabs((ul - 0.6)*(5))
            else:
                return 0
        elif (prop == 'MEDIUM'):
            if ((ul >= 0.3) and (ul <= 0.5)):
                return math.fabs((ul - 0.3)*(5))
            elif (ul >= 0.5 and ul<= 0.7):
                return math.fabs((ul - 0.7)*(-5))
            else:
                return 0
        elif (prop == 'LOW'):
            if (ul <=0.4 and ul>=0):
                return math.fabs((ul - 0.4)*(-2.5))
            else:
                return 0

    def mem_ST(self,st,prop):
        if(prop=='ZERO'):
            if((st>=0) and (st<=0.35)):
                return math.fabs(1.0-(st/0.35))
            elif (st<0):
                return 1
            else:
                return 0
        if(prop=="VERY_LOW"):
            if((st>=0.2) and (st<=0.4)):
                return math.fabs(5*(st-0.2))
            if((st>=0.4) and (st<=0.6)):
                return math.fabs(-5*(st-0.6))
            else:
                return 0
        if(prop=="LOW"):
            if((st>=0.4) and (st<=0.6)):
                return math.fabs(5*(st-0.4))
            if((st>=0.6) and (st<=0.8)):
                return math.fabs(-5*(st-0.8))
            else:
                return 0
        if(prop=="MEDIUM"):
            if((st>=0.7) and (st<=0.8)):
                return math.fabs(10*(st-0.7))
            if((st>=0.8) and (st<=0.9)):
                return math.fabs(-10*(st-0.9))
            else:
                return 0
        if(prop=="HIGH"):
            if((st>=0.8) and (st<=0.9)):
                return math.fabs(10*(st-0.8))
            if((st>=0.9) and (st<=1)):
                return 1
            else:
                return 0

    def mem_ARC(self,st,prop):
        if(prop=='ZERO'):
            if((st>=0) and (st<=0.35)):
                return math.fabs(1.0-(st/0.35))
            elif(st<0):
                return 1
            else:
                return 0

        if(prop=="VERY_LOW"):
            if((st>=0.2) and (st<=0.4)):
                return math.fabs(5*(st-0.2))
            elif((st>=0.4) and (st<=0.6)):
                return math.fabs(-5*(st-0.6))
            else:
                return 0
        if(prop=="SLIGHT_LOW"):
            if((st>=0.3) and (st<=0.5)):
                return math.fabs(5*(st-0.3))
            elif((st>=0.5) and  (st<=0.7)):
                return math.fabs(-5*(st-0.7))
        if(prop=="LOW"):
            if((st>=0.4) and (st<=0.6)):
                return math.fabs(5*(st-0.4))
            elif((st>=0.6) and (st<=0.8)):
                return math.fabs(-5*(st-0.8))
            else:
                return 0
        if(prop=="MEDIUM"):
            if((st>=0.7) and (st<=0.8)):
                return math.fabs(10*(st-0.7))
            elif((st>=0.8) and (st<=0.9)):
                return math.fabs(-10*(st-0.9))
            else:
                return 0
        if(prop=="HIGH"):
            if((st>=0.8) and (st<=0.9)):
                return 10*(st-0.8)
            elif((st>=0.9) and (st<=1)):
                return 1
            else:
                return 0

    def mem_VER(self,st,prop):
        if(prop=='ZERO'):
            if((st>=0) and (st<=0.35)):
                return math.fabs((st-0.35)*(-1/0.35))
            elif(st<0):
                return 1
            else:
                return 0
        if (prop == 'VVL'):
            if((st>=0.15) and (st<=0.3)):
                return math.fabs((st-0.15)*(1/0.15))
            elif ((st>=0.3) and (st<=0.45)):
                return math.fabs((st-0.45)*(-1/0.15))
            else:
                return 0

        if(prop=="VERY_LOW"):
            if((st>=0.2) and (st<=0.4)):
                return math.fabs(5*(st-0.2))
            if((st>=0.4) and (st<=0.6)):
                return math.fabs(-5*(st-0.6))
            else:
                return 0
        if(prop=="LOW"):
            if((st>=0.4) and (st<=0.6)):
                return math.fabs(5*(st-0.4))
            if((st>=0.6) and (st<=0.8)):
                return math.fabs(-5*(st-0.8))
            else:
                return 0
        if(prop=="MEDIUM"):
            if((st>=0.7) and (st<=0.8)):
                return math.fabs(10*(st-0.7))
            if((st>=0.8) and (st<=0.9)):
                return math.fabs(-10*(st-0.9))
            else:
                return 0
        if(prop=="HIGH"):
            if((st>=0.8) and (st<=0.9)):
                return 10*(st-0.8)
            if((st>=0.9) and (st<=1)):
                return 1
            else:
                return 0

    def mem_HOR(self,st,prop):
        if(prop=='ZERO'):
            if((st>=0) and (st<=0.35)):
                return math.fabs(1.0-(st/0.35))
            elif (st<0):
                return 1
            else:
                return 0

        if(prop=="VERY_LOW"):
            if((st>=0.2) and (st<=0.4)):
                return math.fabs(5*(st-0.2))
            if((st>=0.4) and (st<=0.6)):
                return math.fabs(-5*(st-0.6))
            else:
                return 0
        if(prop=="LOW"):
            if((st>=0.4) and (st<=0.6)):
                return math.fabs(5*(st-0.4))
            if((st>=0.6) and (st<=0.8)):
                return math.fabs(-5*(st-0.8))
            else:
                return 0
        if(prop=="MEDIUM"):
            if((st>=0.7) and (st<=0.8)):
                return math.fabs(10*(st-0.7))
            if((st>=0.8) and (st<=0.9)):
                return math.fabs(-10*(st-0.9))
            else:
                return 0
        if(prop=="HIGH"):
            if((st>=0.8) and (st<=0.9)):
                return 10*(st-0.8)
            if((st>=0.9) and (st<=1)):
                return 1
            else:
                return 0

    def mem_PS(self,st,prop):
        if(prop=="LOW"):
            if(st<=0.4 and st>=0):
                return math.fabs((-5/2)*(st-0.4))
            elif(st<0):
                return 1
            else:
                return 0
        if(prop=="HIGH"):
            if((st>=0.4) and (st<=0.5)):
                return (10*(st-0.4))
            if((st>=0.5) and (st<=1)):
                return 1
            else:
                return 0
























    #self.x_max = 0
    #self.y_max = 0
    #self.x_center = 0
    #self. y_center = 0
    #self.mew_HP = 0
    #self.mew_VP = 0
    #self.dist_fi = 0
    #self.tot_dist = 0
    #self.mew_STRAIGHTNESS = 0
    #self.mew_ARCNESS = 0
    #self.AVG_SLOPE = 0
    #self.mew_VERTICAL = 0
    #self.mew_HORIZONTAL = 0
    #self.mew_PS = 0
    #self.mew_NS = 0
    #self.mew_HLEN = 0
    #self.mew_SLEN = 0
    #self.mew_VLEN = 0
    #self.CL = 0
    #self.DL = 0
    #self.AL = 0
    #self.UL = 0
    #self.OL = 0
    #self.HSL = 0
    #self.WSL = 0
    #self.CL = 0
    #self.CL = 0





class Numeral():

    def __init__(self,coord):
        self.coord = []
        self.coord = list(coord)
        self.seg_coord = []
        self.segments_list = []
        self.calc_boundary()
        self.segment()
        self.prettify_segment()
        self.initialize_segments()
        self.calc_prob_numerals()
        self.print_prob()
        self.calc_max()

    def calc_max(self):
        max_val = max(self.prob_1, self.prob_2, self.prob_3, self.prob_4, self.prob_5, self.prob_6, self.prob_7, self.prob_8, self.prob_9, self.prob_0)
        self.max = max_val
        if (math.fabs(max_val-0)<0.0001):
            self.mpv = None
        elif (math.fabs(max_val-self.prob_1)<0.0001):
            self.mpv = 1
        elif (math.fabs(max_val-self.prob_2)<0.0001):
            self.mpv = 2
        elif (math.fabs(max_val-self.prob_3)<0.0001):
            self.mpv = 3
        elif (math.fabs(max_val-self.prob_4)<0.0001):
            self.mpv = 4
        elif (math.fabs(max_val-self.prob_5)<0.0001):
            self.mpv = 5
        elif (math.fabs(max_val-self.prob_6)<0.0001):
            self.mpv = 6
        elif (math.fabs(max_val-self.prob_7)<0.0001):
            self.mpv = 7
        elif (math.fabs(max_val-self.prob_8)<0.0001):
            self.mpv = 8
        elif (math.fabs(max_val-self.prob_9)<0.0001):
            self.mpv = 9
        elif (math.fabs(max_val-self.prob_0)<0.0001):
            self.mpv = 0


    def reset(self):
        self.seg_coord = []
        self.coord = []
    def initialize_segments(self):
        for seg in self.seg_coord:
            instance = Segment(self, seg)
            self.segments_list.append(instance)
        print '\n************************************************** DEBUG ************************************************\n\n'
        j = 0
        for inst in self.segments_list:
            j = j+1
            print 'SEGMENT NO. -- ',j, '\n'
            inst.debug()

    def print_prob(self):
        print '/n/n***************************************************** PROBABILITIES*******************************************/n/n'
        print 'Chances of finding 1 is ',self.prob_1
        print 'Chances of finding 2 is ',self.prob_2
        print 'Chances of finding 3 is ',self.prob_3
        print 'Chances of finding 4 is ',self.prob_4
        print 'Chances of finding 5 is ',self.prob_5
        print 'Chances of finding 6 is ',self.prob_6
        print 'Chances of finding 7 is ',self.prob_7
        print 'Chances of finding 8 is ',self.prob_8
        print 'Chances of finding 9 is ',self.prob_9
        print 'Chances of finding 0 is ',self.prob_0


    def calc_prob_numerals(self):
        self.prob_1 = 0
        self.prob_2 = 0
        self.prob_3 = 0
        self.prob_8 = 0
        self.prob_7 = 0
        self.prob_4 = 0
        self.prob_5 = 0
        self.prob_6 = 0
        self.prob_9 = 0
        self.prob_0 = 0
        if (len(self.segments_list) == 1):
            seg1 = self.segments_list[0]
            #print 'straightness for high:', seg1.mem_ST(seg1.mew_STRAIGHTNESS, 'HIGH')
            #print 'Verticalness for high:',seg1.mem_VER(seg1.mew_VERTICAL, 'HIGH')
            #print 'hor pos for center', seg1.mem_HP(seg1.mew_HP, 'CENTER')
            #print 'ver pos for center', seg1.mem_VP(seg1.mew_VP, 'CENTER')
            #print 'straightness for zero', seg1.mem_ST(seg1.mew_STRAIGHTNESS, 'ZERO')
            #print 'clike for MEDIUM', seg1.mem_CL(seg1.mew_CL, 'MEDIUM')
            #print 'clike for high', seg1.mem_CL(seg1.mew_CL, 'HIGH')
            #print 'ulike for high', seg1.mem_UL(seg1.mew_UL, 'HIGH')
            prob_1 = min( seg1.mem_ST(seg1.mew_STRAIGHTNESS, 'HIGH'), seg1.mem_VER(seg1.mew_VERTICAL, 'HIGH') )
            prob_8 = min( seg1.mem_HP(seg1.mew_HP, 'CENTER'), seg1.mem_VP(seg1.mew_VP, 'CENTER'), seg1.mem_ST(seg1.mew_STRAIGHTNESS, 'ZERO'), max(seg1.mem_CL(seg1.mew_CL, 'MEDIUM'), seg1.mem_CL(seg1.mew_CL, 'HIGH')), seg1.mem_UL(seg1.mew_UL, 'HIGH') )
            self.prob_1 = prob_1
            self.prob_8 = prob_8
        elif (len(self.segments_list) == 2):
            seg1 = self.segments_list[0]
            seg2 = self.segments_list[1]
            #print 'SEG 1: straightness for high:', seg1.mem_ST(seg1.mew_STRAIGHTNESS, 'HIGH')
            #print 'SEG 1: straightness for medium:', seg1.mem_ST(seg1.mew_STRAIGHTNESS, 'MEDIUM')
            #print 'SEG 1: straightness for low:', seg1.mem_ST(seg1.mew_STRAIGHTNESS, 'LOW')
            #print 'SEG 1: straightness for very low:', seg1.mem_ST(seg1.mew_STRAIGHTNESS, 'VERY_LOW')
            #print 'SEG 1: straightness for zero:', seg1.mem_ST(seg1.mew_STRAIGHTNESS, 'ZERO')

            #print 'SEG 1: verticalness for high:', seg1.mem_VER(seg1.mew_VERTICAL, 'HIGH')
            #print 'SEG 1: verticalness for medium:', seg1.mem_VER(seg1.mew_VERTICAL, 'MEDIUM')
            #print 'SEG 1: verticalness for low:', seg1.mem_VER(seg1.mew_VERTICAL, 'LOW')
            #print 'SEG 1: verticalness for very low:', seg1.mem_VER(seg1.mew_VERTICAL, 'VERY_LOW')
            #print 'SEG 1: verticalness for zero:', seg1.mem_VER(seg1.mew_VERTICAL, 'ZERO')
            #print 'SEG 1: Verticalness for VVL:',seg1.mem_VER(seg1.mew_VERTICAL, 'VVL')

            #print 'SEG 1: Horizontalnesss for zero:',seg1.mem_HOR(seg1.mew_HORIZONTAL, 'ZERO')
            #print 'SEG 1: Horizontalnesss for high:', seg1.mem_HOR(seg1.mew_HORIZONTAL, 'HIGH')
            #print 'SEG 1: Horizontalnesss for medium:', seg1.mem_HOR(seg1.mew_HORIZONTAL, 'MEDIUM')
            #print 'SEG 1: Horizontalnesss for low:', seg1.mem_HOR(seg1.mew_HORIZONTAL, 'LOW')
            #print 'SEG 1: Horizontalnesss for very low:', seg1.mem_HOR(seg1.mew_HORIZONTAL, 'VERY_LOW')

            #print 'SEG 1: arcness for high:', seg1.mem_ARC(seg1.mew_ARCNESS, 'HIGH')
            #print 'SEG 1: arcness for medium:', seg1.mem_ARC(seg1.mew_ARCNESS, 'MEDIUM')
            #print 'SEG 1: arcness for low:', seg1.mem_ARC(seg1.mew_ARCNESS, 'LOW')
            #print 'SEG 1: arcness for very low:', seg1.mem_ARC(seg1.mew_ARCNESS, 'VERY_LOW')
            #print 'SEG 1: arcness for zero:', seg1.mem_ARC(seg1.mew_ARCNESS, 'ZERO')

            #print 'SEG 1: ver pos for top center', seg1.mem_VP(seg1.mew_VP, 'TOP_CENTER')
            #print 'SEG 1: ver pos for slight top', seg1.mem_VP(seg1.mew_VP, 'SLIGHT_TOP')
            #print 'SEG 1: ver pos for center', seg1.mem_VP(seg1.mew_VP, 'CENTER')
            #print 'SEG 1: ver pos for bottom', seg1.mem_VP(seg1.mew_VP, 'BOTTOM')
            #print 'SEG 1: ver pos for bottom center', seg1.mem_VP(seg1.mew_VP, 'BOTTOM_CENTER')
            #print 'SEG 1: ver pos for top', seg1.mem_VP(seg1.mew_VP, 'TOP')

            #print 'SEG 1: hor pos for center', seg1.mem_HP(seg1.mew_HP, 'CENTER')
            #print 'SEG 1: hor pos for right center', seg1.mem_HP(seg1.mew_HP, 'RIGHT_CENTER')
            #print 'SEG 1: hor pos for left', seg1.mem_HP(seg1.mew_HP, 'LEFT')
            #print 'SEG 1: hor pos for left center', seg1.mem_HP(seg1.mew_HP, 'LEFT_CENTER')
            #print 'SEG 1: hor pos for right', seg1.mem_HP(seg1.mew_HP, 'RIGHT')

            #print 'SEG 1: ulike for low ',seg1.mem_UL(seg1.mew_UL, 'LOW')
            #print 'SEG 1: ulike for medium ',seg1.mem_UL(seg1.mew_UL, 'MEDIUM')
            #print 'SEG 1: ulike for high ',seg1.mem_UL(seg1.mew_UL, 'HIGH')

            #print 'SEG 1: alike for low ',seg1.mem_AL(seg1.mew_AL, 'LOW')
            #print 'SEG 1: alike for medium ',seg1.mem_AL(seg1.mew_AL, 'MEDIUM')
            #print 'SEG 1: alike for high ',seg1.mem_AL(seg1.mew_AL, 'HIGH')

            #print 'SEG 1: clike for low ',seg1.mem_CL(seg1.mew_CL, 'LOW')
            #print 'SEG 1: clike for medium ',seg1.mem_CL(seg1.mew_CL, 'MEDIUM')
            #print 'SEG 1: clike for high ',seg1.mem_CL(seg1.mew_CL, 'HIGH')

            #print 'SEG 1: dlike for low ',seg1.mem_DL(seg1.mew_DL, 'LOW')
            #print 'SEG 1: dlike for medium ',seg1.mem_DL(seg1.mew_DL, 'MEDIUM')
            #print 'SEG 1: dlike for high ',seg1.mem_DL(seg1.mew_DL, 'HIGH')

            #print 'SEG 1: positive slope for high', seg1.mem_PS(seg1.mew_PS,'HIGH')
            #print 'SEG 1: positive slope for low', seg1.mem_PS(seg1.mew_PS,'LOW')

            #print 'SEG 2: straightness for high:', seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'HIGH')
            #print 'SEG 2: straightness for medium:', seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'MEDIUM')
            #print 'SEG 2: straightness for low:', seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'LOW')
            #print 'SEG 2: straightness for very low:', seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'VERY_LOW')
            #print 'SEG 2: straightness for zero:', seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'ZERO')

            #print 'SEG 2: verticalness for high:', seg2.mem_VER(seg2.mew_VERTICAL, 'HIGH')
            #print 'SEG 2: verticalness for medium:', seg2.mem_VER(seg2.mew_VERTICAL, 'MEDIUM')
            #print 'SEG 2: verticalness for low:', seg2.mem_VER(seg2.mew_VERTICAL, 'LOW')
            #print 'SEG 2: verticalness for very low:', seg2.mem_VER(seg2.mew_VERTICAL, 'VERY_LOW')
            #print 'SEG 2: verticalness for zero:', seg2.mem_VER(seg2.mew_VERTICAL, 'ZERO')
            #print 'SEG 2: Verticalness for VVL:',seg2.mem_VER(seg2.mew_VERTICAL, 'VVL')

            #print 'SEG 2: Horizontalnesss for zero:',seg2.mem_HOR(seg2.mew_HORIZONTAL, 'ZERO')
            #print 'SEG 2: Horizontalnesss for high:', seg2.mem_HOR(seg2.mew_HORIZONTAL, 'HIGH')
            #print 'SEG 2: Horizontalnesss for medium:', seg2.mem_HOR(seg2.mew_HORIZONTAL, 'MEDIUM')
            #print 'SEG 2: Horizontalnesss for low:', seg2.mem_HOR(seg2.mew_HORIZONTAL, 'LOW')
            #print 'SEG 2: Horizontalnesss for very low:', seg2.mem_HOR(seg2.mew_HORIZONTAL, 'VERY_LOW')

            #print 'SEG 2: arcness for high:', seg2.mem_ARC(seg2.mew_ARCNESS, 'HIGH')
            #print 'SEG 2: arcness for medium:', seg2.mem_ARC(seg2.mew_ARCNESS, 'MEDIUM')
            #print 'SEG 2: arcness for low:', seg2.mem_ARC(seg2.mew_ARCNESS, 'LOW')
            #print 'SEG 2: arcness for very low:', seg2.mem_ARC(seg2.mew_ARCNESS, 'VERY_LOW')
            #print 'SEG 2: arcness for zero:', seg2.mem_ARC(seg2.mew_ARCNESS, 'ZERO')

            #print 'SEG 2: ver pos for top center', seg2.mem_VP(seg2.mew_VP, 'TOP_CENTER')
            #print 'SEG 2: ver pos for slight top', seg2.mem_VP(seg2.mew_VP, 'SLIGHT_TOP')
            #print 'SEG 2: ver pos for center', seg2.mem_VP(seg2.mew_VP, 'CENTER')
            #print 'SEG 2: ver pos for bottom', seg2.mem_VP(seg2.mew_VP, 'BOTTOM')
            #print 'SEG 2: ver pos for bottom center', seg2.mem_VP(seg2.mew_VP, 'BOTTOM_CENTER')
            #print 'SEG 2: ver pos for top', seg2.mem_VP(seg2.mew_VP, 'TOP')

            #print 'SEG 2: hor pos for center', seg2.mem_HP(seg2.mew_HP, 'CENTER')
            #print 'SEG 2: hor pos for right center', seg2.mem_HP(seg2.mew_HP, 'RIGHT_CENTER')
            #print 'SEG 2: hor pos for left', seg2.mem_HP(seg2.mew_HP, 'LEFT')
            #print 'SEG 2: hor pos for left center', seg2.mem_HP(seg2.mew_HP, 'LEFT_CENTER')
            #print 'SEG 2: hor pos for right', seg2.mem_HP(seg2.mew_HP, 'RIGHT')

            #print 'SEG 2: ulike for low ',seg2.mem_UL(seg2.mew_UL, 'LOW')
            #print 'SEG 2: ulike for medium ',seg2.mem_UL(seg2.mew_UL, 'MEDIUM')
            #print 'SEG 2: ulike for high ',seg2.mem_UL(seg2.mew_UL, 'HIGH')

            #print 'SEG 2: alike for low ',seg2.mem_AL(seg2.mew_AL, 'LOW')
            #print 'SEG 2: alike for medium ',seg2.mem_AL(seg2.mew_AL, 'MEDIUM')
            #print 'SEG 2: alike for high ',seg2.mem_AL(seg2.mew_AL, 'HIGH')

            #print 'SEG 2: clike for low ',seg2.mem_CL(seg2.mew_CL, 'LOW')
            #print 'SEG 2: clike for medium ',seg2.mem_CL(seg2.mew_CL, 'MEDIUM')
            #print 'SEG 2: clike for high ',seg2.mem_CL(seg2.mew_CL, 'HIGH')

            #print 'SEG 2: dlike for low ',seg2.mem_DL(seg2.mew_DL, 'LOW')
            #print 'SEG 2: dlike for medium ',seg2.mem_DL(seg2.mew_DL, 'MEDIUM')
            #print 'SEG 2: dlike for high ',seg2.mem_DL(seg2.mew_DL, 'HIGH')

            #print 'SEG 2: positive slope for high', seg2.mem_PS(seg2.mew_PS,'HIGH')
            #print 'SEG 2: positive slope for low', seg2.mem_PS(seg2.mew_PS,'LOW')




            #prob_1 = min(max(seg1.mem_VP(seg1.mew_VP,'TOP_CENTER'), seg1.mem_VP(seg1.mew_VP, 'SLIGHT_TOP')), seg1.mem_ST(seg1.mew_STRAIGHTNESS,'HIGH'),seg1.mem_HOR(seg1.mew_HORIZONTAL,'ZERO'),seg1.mem_VER(seg1.mew_VERTICAL,'ZERO'),seg1.mem_UL(seg1.mew_UL, 'MEDIUM'),seg1.mem_CL(seg1.mew_CL, 'MEDIUM'),seg1.mem_DL(seg1.mew_DL, 'MEDIUM'),seg1.mem_AL(seg1.mew_AL, 'MEDIUM')/
                         #seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'HIGH'), seg2.mem_VER(seg2.mew_VERTICAL, 'HIGH'))

            prob_1 = min(max(seg1.mem_VP(seg1.mew_VP,'TOP_CENTER'), seg1.mem_VP(seg1.mew_VP, 'SLIGHT_TOP')), seg1.mem_ST(seg1.mew_STRAIGHTNESS,'HIGH'), max(seg1.mem_HOR(seg1.mew_HORIZONTAL,'ZERO'),seg1.mem_VER(seg1.mew_VERTICAL,'ZERO'), seg1.mem_VER(seg1.mew_VERTICAL,'VVL')), seg1.mem_PS(seg1.mew_PS,'HIGH'), seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'HIGH'), seg2.mem_VER(seg2.mew_VERTICAL, 'HIGH'))
            prob_7 = min(seg1.mem_HP(seg1.mew_HP, 'CENTER'), seg1.mem_VP(seg1.mew_VP, 'TOP'), seg1.mem_ST(seg1.mew_STRAIGHTNESS,'HIGH'), max(seg1.mem_HOR(seg1.mew_HORIZONTAL,'HIGH'),seg1.mem_HOR(seg1.mew_HORIZONTAL,'MEDIUM')),\
                         seg2.mem_ST(seg2.mew_STRAIGHTNESS,'HIGH'), seg2.mem_VP(seg2.mew_VP, 'CENTER'), max(seg2.mem_PS(seg2.mew_PS,'HIGH'), seg2.mem_VER(seg2.mew_VERTICAL, 'HIGH') ))
            prob_2 = min(seg1.mem_VP(seg1.mew_VP, 'CENTER'),max(seg1.mem_ARC(seg1.mew_ARCNESS,'LOW'),seg1.mem_ARC(seg1.mew_ARCNESS,'VERY_LOW'),seg1.mem_ARC(seg1.mew_ARCNESS,'SLIGHT_LOW')),seg1.mem_DL(seg1.mew_DL, 'HIGH'),\
                         max(seg2.mem_ST(seg2.mew_STRAIGHTNESS,'HIGH'), seg2.mem_ST(seg2.mew_STRAIGHTNESS,'MEDIUM')), seg2.mem_VP(seg2.mew_VP, 'BOTTOM'), seg2.mem_HOR(seg2.mew_HORIZONTAL,'HIGH'), seg2.mem_HP(seg2.mew_HP, 'CENTER'))
            prob_3 = min(seg1.mem_VP(seg1.mew_VP, 'TOP_CENTER'),max(seg1.mem_ST(seg1.mew_STRAIGHTNESS,'LOW'),seg1.mem_ST(seg1.mew_STRAIGHTNESS,'ZERO'),seg1.mem_ST(seg1.mew_STRAIGHTNESS,'VERY_LOW')), seg1.mem_HP(seg1.mew_HP, 'CENTER'), seg1.mem_DL(seg1.mew_DL, 'HIGH'),\
                         seg2.mem_VP(seg2.mew_VP, 'BOTTOM_CENTER'),max(seg2.mem_ST(seg2.mew_STRAIGHTNESS,'LOW'),seg2.mem_ST(seg2.mew_STRAIGHTNESS,'ZERO'),seg2.mem_ST(seg2.mew_STRAIGHTNESS,'VERY_LOW')), seg2.mem_HP(seg2.mew_HP, 'CENTER'), seg2.mem_DL(seg2.mew_DL, 'HIGH'))
            prob_5 = min(max(seg1.mem_CL(seg1.mew_CL, 'HIGH'), seg1.mem_CL(seg1.mew_CL, 'MEDIUM')),seg1.mem_VP(seg1.mew_VP, 'TOP_CENTER'),seg1.mem_HP(seg1.mew_HP, 'CENTER'),\
                         max(seg2.mem_DL(seg2.mew_DL, 'HIGH'),seg2.mem_DL(seg2.mew_DL, 'MEDIUM')),seg2.mem_HP(seg2.mew_HP, 'CENTER'),seg2.mem_VP(seg2.mew_VP, 'BOTTOM_CENTER'))
            prob_6 = min(seg1.mem_CL(seg1.mew_CL, 'HIGH'),seg1.mem_VP(seg1.mew_VP, 'CENTER'),\
                         seg2.mem_DL(seg2.mew_DL, 'HIGH'),seg2.mem_VP(seg2.mew_VP, 'BOTTOM_CENTER'))
            prob_9 = min(seg1.mem_CL(seg1.mew_CL, 'HIGH'),seg1.mem_VP(seg1.mew_VP, 'TOP_CENTER'),\
                         seg2.mem_VP(seg2.mew_VP, 'CENTER'),max(seg2.mem_HP(seg2.mew_HP, 'RIGHT_CENTER'),seg2.mem_HP(seg2.mew_HP, 'RIGHT')))
            prob_0 = min(seg1.mem_CL(seg1.mew_CL, 'HIGH'),seg1.mem_VP(seg1.mew_VP, 'CENTER'),max(seg1.mem_HP(seg1.mew_HP, 'CENTER'),seg1.mem_HP(seg1.mew_HP, 'LEFT_CENTER')),\
                         seg2.mem_DL(seg2.mew_DL, 'HIGH'),seg2.mem_VP(seg2.mew_VP, 'CENTER'),seg2.mem_HP(seg2.mew_HP, 'RIGHT_CENTER'))
            self.prob_1 = prob_1
            self.prob_0 = prob_0
            self.prob_3 = prob_3
            self.prob_5 = prob_5
            self.prob_6 = prob_6
            self.prob_7 = prob_7
            self.prob_9 = prob_9
            self.prob_2 = prob_2

        elif(len(self.segments_list) == 3):
            seg1 = self.segments_list[0]
            seg2 = self.segments_list[1]
            seg3 = self.segments_list[2]
            #print 'SEG 1: straightness for high:', seg1.mem_ST(seg1.mew_STRAIGHTNESS, 'HIGH')
            #print 'SEG 1: straightness for medium:', seg1.mem_ST(seg1.mew_STRAIGHTNESS, 'MEDIUM')
##            print 'SEG 1: straightness for low:', seg1.mem_ST(seg1.mew_STRAIGHTNESS, 'LOW')
##            print 'SEG 1: straightness for very low:', seg1.mem_ST(seg1.mew_STRAIGHTNESS, 'VERY_LOW')
##            print 'SEG 1: straightness for zero:', seg1.mem_ST(seg1.mew_STRAIGHTNESS, 'ZERO')
##
##            print 'SEG 1: verticalness for high:', seg1.mem_VER(seg1.mew_VERTICAL, 'HIGH')
##            print 'SEG 1: verticalness for medium:', seg1.mem_VER(seg1.mew_VERTICAL, 'MEDIUM')
##            print 'SEG 1: verticalness for low:', seg1.mem_VER(seg1.mew_VERTICAL, 'LOW')
##            print 'SEG 1: verticalness for very low:', seg1.mem_VER(seg1.mew_VERTICAL, 'VERY_LOW')
##            print 'SEG 1: verticalness for zero:', seg1.mem_VER(seg1.mew_VERTICAL, 'ZERO')
##            print 'SEG 1: Verticalness for VVL:',seg1.mem_VER(seg1.mew_VERTICAL, 'VVL')
##
##            print 'SEG 1: Horizontalnesss for zero:',seg1.mem_HOR(seg1.mew_HORIZONTAL, 'ZERO')
##            print 'SEG 1: Horizontalnesss for high:', seg1.mem_HOR(seg1.mew_HORIZONTAL, 'HIGH')
##            print 'SEG 1: Horizontalnesss for medium:', seg1.mem_HOR(seg1.mew_HORIZONTAL, 'MEDIUM')
##            print 'SEG 1: Horizontalnesss for low:', seg1.mem_HOR(seg1.mew_HORIZONTAL, 'LOW')
##            print 'SEG 1: Horizontalnesss for very low:', seg1.mem_HOR(seg1.mew_HORIZONTAL, 'VERY_LOW')
##
##            print 'SEG 1: arcness for high:', seg1.mem_ARC(seg1.mew_ARCNESS, 'HIGH')
##            print 'SEG 1: arcness for medium:', seg1.mem_ARC(seg1.mew_ARCNESS, 'MEDIUM')
##            print 'SEG 1: arcness for low:', seg1.mem_ARC(seg1.mew_ARCNESS, 'LOW')
##            print 'SEG 1: arcness for very low:', seg1.mem_ARC(seg1.mew_ARCNESS, 'VERY_LOW')
##            print 'SEG 1: arcness for zero:', seg1.mem_ARC(seg1.mew_ARCNESS, 'ZERO')
##
##            print 'SEG 1: ver pos for top center', seg1.mem_VP(seg1.mew_VP, 'TOP_CENTER')
##            print 'SEG 1: ver pos for slight top', seg1.mem_VP(seg1.mew_VP, 'SLIGHT_TOP')
##            print 'SEG 1: ver pos for center', seg1.mem_VP(seg1.mew_VP, 'CENTER')
##            print 'SEG 1: ver pos for bottom', seg1.mem_VP(seg1.mew_VP, 'BOTTOM')
##            print 'SEG 1: ver pos for bottom center', seg1.mem_VP(seg1.mew_VP, 'BOTTOM_CENTER')
##            print 'SEG 1: ver pos for top', seg1.mem_VP(seg1.mew_VP, 'TOP')
##
##            print 'SEG 1: hor pos for center', seg1.mem_HP(seg1.mew_HP, 'CENTER')
##            print 'SEG 1: hor pos for right center', seg1.mem_HP(seg1.mew_HP, 'RIGHT_CENTER')
##            print 'SEG 1: hor pos for left', seg1.mem_HP(seg1.mew_HP, 'LEFT')
##            print 'SEG 1: hor pos for left center', seg1.mem_HP(seg1.mew_HP, 'LEFT_CENTER')
##            print 'SEG 1: hor pos for right', seg1.mem_HP(seg1.mew_HP, 'RIGHT')
##
##            print 'SEG 1: ulike for low ',seg1.mem_UL(seg1.mew_UL, 'LOW')
##            print 'SEG 1: ulike for medium ',seg1.mem_UL(seg1.mew_UL, 'MEDIUM')
##            print 'SEG 1: ulike for high ',seg1.mem_UL(seg1.mew_UL, 'HIGH')
##
##            print 'SEG 1: alike for low ',seg1.mem_AL(seg1.mew_AL, 'LOW')
##            print 'SEG 1: alike for medium ',seg1.mem_AL(seg1.mew_AL, 'MEDIUM')
##            print 'SEG 1: alike for high ',seg1.mem_AL(seg1.mew_AL, 'HIGH')
##
##            print 'SEG 1: clike for low ',seg1.mem_CL(seg1.mew_CL, 'LOW')
##            print 'SEG 1: clike for medium ',seg1.mem_CL(seg1.mew_CL, 'MEDIUM')
##            print 'SEG 1: clike for high ',seg1.mem_CL(seg1.mew_CL, 'HIGH')
##
##            print 'SEG 1: dlike for low ',seg1.mem_DL(seg1.mew_DL, 'LOW')
##            print 'SEG 1: dlike for medium ',seg1.mem_DL(seg1.mew_DL, 'MEDIUM')
##            print 'SEG 1: dlike for high ',seg1.mem_DL(seg1.mew_DL, 'HIGH')
##
##            print 'SEG 1: positive slope for high', seg1.mem_PS(seg1.mew_PS,'HIGH')
##            print 'SEG 1: positive slope for low', seg1.mem_PS(seg1.mew_PS,'LOW')
##
##            print 'SEG 2: straightness for high:', seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'HIGH')
##            print 'SEG 2: straightness for medium:', seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'MEDIUM')
##            print 'SEG 2: straightness for low:', seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'LOW')
##            print 'SEG 2: straightness for very low:', seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'VERY_LOW')
##            print 'SEG 2: straightness for zero:', seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'ZERO')
##
##            print 'SEG 2: verticalness for high:', seg2.mem_VER(seg2.mew_VERTICAL, 'HIGH')
##            print 'SEG 2: verticalness for medium:', seg2.mem_VER(seg2.mew_VERTICAL, 'MEDIUM')
##            print 'SEG 2: verticalness for low:', seg2.mem_VER(seg2.mew_VERTICAL, 'LOW')
##            print 'SEG 2: verticalness for very low:', seg2.mem_VER(seg2.mew_VERTICAL, 'VERY_LOW')
##            print 'SEG 2: verticalness for zero:', seg2.mem_VER(seg2.mew_VERTICAL, 'ZERO')
##            print 'SEG 2: Verticalness for VVL:',seg2.mem_VER(seg2.mew_VERTICAL, 'VVL')
##
##            print 'SEG 2: Horizontalnesss for zero:',seg2.mem_HOR(seg2.mew_HORIZONTAL, 'ZERO')
##            print 'SEG 2: Horizontalnesss for high:', seg2.mem_HOR(seg2.mew_HORIZONTAL, 'HIGH')
##            print 'SEG 2: Horizontalnesss for medium:', seg2.mem_HOR(seg2.mew_HORIZONTAL, 'MEDIUM')
##            print 'SEG 2: Horizontalnesss for low:', seg2.mem_HOR(seg2.mew_HORIZONTAL, 'LOW')
##            print 'SEG 2: Horizontalnesss for very low:', seg2.mem_HOR(seg2.mew_HORIZONTAL, 'VERY_LOW')
##
##            print 'SEG 2: arcness for high:', seg2.mem_ARC(seg2.mew_ARCNESS, 'HIGH')
##            print 'SEG 2: arcness for medium:', seg2.mem_ARC(seg2.mew_ARCNESS, 'MEDIUM')
##            print 'SEG 2: arcness for low:', seg2.mem_ARC(seg2.mew_ARCNESS, 'LOW')
##            print 'SEG 2: arcness for very low:', seg2.mem_ARC(seg2.mew_ARCNESS, 'VERY_LOW')
##            print 'SEG 2: arcness for zero:', seg2.mem_ARC(seg2.mew_ARCNESS, 'ZERO')
##
##            print 'SEG 2: ver pos for top center', seg2.mem_VP(seg2.mew_VP, 'TOP_CENTER')
##            print 'SEG 2: ver pos for slight top', seg2.mem_VP(seg2.mew_VP, 'SLIGHT_TOP')
##            print 'SEG 2: ver pos for center', seg2.mem_VP(seg2.mew_VP, 'CENTER')
##            print 'SEG 2: ver pos for bottom', seg2.mem_VP(seg2.mew_VP, 'BOTTOM')
##            print 'SEG 2: ver pos for bottom center', seg2.mem_VP(seg2.mew_VP, 'BOTTOM_CENTER')
##            print 'SEG 2: ver pos for top', seg2.mem_VP(seg2.mew_VP, 'TOP')
##
##            print 'SEG 2: hor pos for center', seg2.mem_HP(seg2.mew_HP, 'CENTER')
##            print 'SEG 2: hor pos for right center', seg2.mem_HP(seg2.mew_HP, 'RIGHT_CENTER')
##            print 'SEG 2: hor pos for left', seg2.mem_HP(seg2.mew_HP, 'LEFT')
##            print 'SEG 2: hor pos for left center', seg2.mem_HP(seg2.mew_HP, 'LEFT_CENTER')
##            print 'SEG 2: hor pos for right', seg2.mem_HP(seg2.mew_HP, 'RIGHT')
##
##            print 'SEG 2: ulike for low ',seg2.mem_UL(seg2.mew_UL, 'LOW')
##            print 'SEG 2: ulike for medium ',seg2.mem_UL(seg2.mew_UL, 'MEDIUM')
##            print 'SEG 2: ulike for high ',seg2.mem_UL(seg2.mew_UL, 'HIGH')
##
##            print 'SEG 2: alike for low ',seg2.mem_AL(seg2.mew_AL, 'LOW')
##            print 'SEG 2: alike for medium ',seg2.mem_AL(seg2.mew_AL, 'MEDIUM')
##            print 'SEG 2: alike for high ',seg2.mem_AL(seg2.mew_AL, 'HIGH')
##
##            print 'SEG 2: clike for low ',seg2.mem_CL(seg2.mew_CL, 'LOW')
##            print 'SEG 2: clike for medium ',seg2.mem_CL(seg2.mew_CL, 'MEDIUM')
##            print 'SEG 2: clike for high ',seg2.mem_CL(seg2.mew_CL, 'HIGH')
##
##            print 'SEG 2: dlike for low ',seg2.mem_DL(seg2.mew_DL, 'LOW')
##            print 'SEG 2: dlike for medium ',seg2.mem_DL(seg2.mew_DL, 'MEDIUM')
##            print 'SEG 2: dlike for high ',seg2.mem_DL(seg2.mew_DL, 'HIGH')
##
##            print 'SEG 2: positive slope for high', seg2.mem_PS(seg2.mew_PS,'HIGH')
##            print 'SEG 2: positive slope for low', seg2.mem_PS(seg2.mew_PS,'LOW')
##
##            print 'SEG 3: straightness for high:', seg3.mem_ST(seg3.mew_STRAIGHTNESS, 'HIGH')
##            print 'SEG 3: straightness for medium:', seg3.mem_ST(seg3.mew_STRAIGHTNESS, 'MEDIUM')
##            print 'SEG 3: straightness for low:', seg3.mem_ST(seg3.mew_STRAIGHTNESS, 'LOW')
##            print 'SEG 3: straightness for very low:', seg3.mem_ST(seg3.mew_STRAIGHTNESS, 'VERY_LOW')
##            print 'SEG 3: straightness for zero:', seg3.mem_ST(seg3.mew_STRAIGHTNESS, 'ZERO')
##
##            print 'SEG 3: verticalness for high:', seg3.mem_VER(seg3.mew_VERTICAL, 'HIGH')
##            print 'SEG 3: verticalness for medium:', seg3.mem_VER(seg3.mew_VERTICAL, 'MEDIUM')
##            print 'SEG 3: verticalness for low:', seg3.mem_VER(seg3.mew_VERTICAL, 'LOW')
##            print 'SEG 3: verticalness for very low:', seg3.mem_VER(seg3.mew_VERTICAL, 'VERY_LOW')
##            print 'SEG 3: verticalness for zero:', seg3.mem_VER(seg3.mew_VERTICAL, 'ZERO')
##            print 'SEG 3: Verticalness for VVL:',seg3.mem_VER(seg3.mew_VERTICAL, 'VVL')
##
##            print 'SEG 3: Horizontalnesss for zero:',seg3.mem_HOR(seg3.mew_HORIZONTAL, 'ZERO')
##            print 'SEG 3: Horizontalnesss for high:', seg3.mem_HOR(seg3.mew_HORIZONTAL, 'HIGH')
##            print 'SEG 3: Horizontalnesss for medium:', seg3.mem_HOR(seg3.mew_HORIZONTAL, 'MEDIUM')
##            print 'SEG 3: Horizontalnesss for low:', seg3.mem_HOR(seg3.mew_HORIZONTAL, 'LOW')
##            print 'SEG 3: Horizontalnesss for very low:', seg3.mem_HOR(seg3.mew_HORIZONTAL, 'VERY_LOW')
##
##            print 'SEG 3: arcness for high:', seg3.mem_ARC(seg3.mew_ARCNESS, 'HIGH')
##            print 'SEG 3: arcness for medium:', seg3.mem_ARC(seg3.mew_ARCNESS, 'MEDIUM')
##            print 'SEG 3: arcness for low:', seg3.mem_ARC(seg3.mew_ARCNESS, 'LOW')
##            print 'SEG 3: arcness for very low:', seg3.mem_ARC(seg3.mew_ARCNESS, 'VERY_LOW')
##            print 'SEG 3: arcness for zero:', seg3.mem_ARC(seg3.mew_ARCNESS, 'ZERO')
##
##            print 'SEG 3: ver pos for top center', seg3.mem_VP(seg3.mew_VP, 'TOP_CENTER')
##            print 'SEG 3: ver pos for slight top', seg3.mem_VP(seg3.mew_VP, 'SLIGHT_TOP')
##            print 'SEG 3: ver pos for center', seg3.mem_VP(seg3.mew_VP, 'CENTER')
##            print 'SEG 3: ver pos for bottom', seg3.mem_VP(seg3.mew_VP, 'BOTTOM')
##            print 'SEG 3: ver pos for bottom center', seg3.mem_VP(seg3.mew_VP, 'BOTTOM_CENTER')
##            print 'SEG 3: ver pos for top', seg3.mem_VP(seg3.mew_VP, 'TOP')
##
##            print 'SEG 3: hor pos for center', seg3.mem_HP(seg3.mew_HP, 'CENTER')
##            print 'SEG 3: hor pos for right center', seg3.mem_HP(seg3.mew_HP, 'RIGHT_CENTER')
##            print 'SEG 3: hor pos for right', seg3.mem_HP(seg3.mew_HP, 'RIGHT')
##            print 'SEG 3: hor pos for left center', seg3.mem_HP(seg3.mew_HP, 'LEFT_CENTER')
##            print 'SEG 3: hor pos for left', seg3.mem_HP(seg3.mew_HP, 'LEFT')
##
##            print 'SEG 3: ulike for low ',seg3.mem_UL(seg3.mew_UL, 'LOW')
##            print 'SEG 3: ulike for medium ',seg3.mem_UL(seg3.mew_UL, 'MEDIUM')
##            print 'SEG 3: ulike for high ',seg3.mem_UL(seg3.mew_UL, 'HIGH')
##
##            print 'SEG 3: alike for low ',seg3.mem_AL(seg3.mew_AL, 'LOW')
##            print 'SEG 3: alike for medium ',seg3.mem_AL(seg3.mew_AL, 'MEDIUM')
##            print 'SEG 3: alike for high ',seg3.mem_AL(seg3.mew_AL, 'HIGH')
##
##            print 'SEG 3: clike for low ',seg3.mem_CL(seg3.mew_CL, 'LOW')
##            print 'SEG 3: clike for medium ',seg3.mem_CL(seg3.mew_CL, 'MEDIUM')
##            print 'SEG 3: clike for high ',seg3.mem_CL(seg3.mew_CL, 'HIGH')
##
##            print 'SEG 3: dlike for low ',seg3.mem_DL(seg3.mew_DL, 'LOW')
##            print 'SEG 3: dlike for medium ',seg3.mem_DL(seg3.mew_DL, 'MEDIUM')
##            print 'SEG 3: dlike for high ',seg3.mem_DL(seg3.mew_DL, 'HIGH')
##
##            print 'SEG 3: positive slope for high', seg3.mem_PS(seg3.mew_PS,'HIGH')
##            print 'SEG 3: positive slope for low', seg3.mem_PS(seg3.mew_PS,'LOW')

            '''prob_1 = min(max(seg1.mem_VP(seg1.mew_VP,'TOP_CENTER'), seg1.mem_VP(seg1.mew_VP, 'SLIGHT_TOP')), seg1.mem_ST(seg1.mew_STRAIGHTNESS,'HIGH'),\
                                max(seg1.mem_HOR(seg1.mew_HORIZONTAL,'ZERO'),seg1.mem_VER(seg1.mew_VERTICAL,'ZERO'), seg1.mem_VER(seg1.mew_VERTICAL,'VVL')),\
                                seg1.mem_PS(seg1.mew_PS,'HIGH'), seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'HIGH'), seg2.mem_VER(seg2.mew_VERTICAL, 'HIGH'))
            prob_7 = min(seg1.mem_HP(seg1.mew_HP, 'CENTER'), seg1.mem_VP(seg1.mew_VP, 'TOP'), seg1.mem_ST(seg1.mew_STRAIGHTNESS,'HIGH'), max(seg1.mem_HOR(seg1.mew_HORIZONTAL,'HIGH'),seg1.mem_HOR(seg1.mew_HORIZONTAL,'MEDIUM')),\
                         seg2.mem_ST(seg2.mew_STRAIGHTNESS,'HIGH'), seg2.mem_VP(seg2.mew_VP, 'CENTER'), max(seg2.mem_PS(seg2.mew_PS,'HIGH'), seg2.mem_VER(seg2.mew_VERTICAL, 'HIGH') ))
            prob_2 = min(seg1.mem_VP(seg1.mew_VP, 'CENTER'),max(seg1.mem_ARC(seg1.mew_ARCNESS,'LOW'),seg1.mem_ARC(seg1.mew_ARCNESS,'VERY_LOW'),seg1.mem_ARC(seg1.mew_ARCNESS,'SLIGHT_LOW')),seg1.mem_DL(seg1.mew_DL, 'HIGH'),\
                         max(seg2.mem_ST(seg2.mew_STRAIGHTNESS,'HIGH'), seg2.mem_ST(seg2.mew_STRAIGHTNESS,'MEDIUM')), seg2.mem_VP(seg2.mew_VP, 'BOTTOM'), seg2.mem_HOR(seg2.mew_HORIZONTAL,'HIGH'), seg2.mem_HP(seg2.mew_HP, 'CENTER'))
            prob_3 = min(seg1.mem_VP(seg1.mew_VP, 'TOP_CENTER'),max(seg1.mem_ST(seg1.mew_STRAIGHTNESS,'LOW'),seg1.mem_ST(seg1.mew_STRAIGHTNESS,'ZERO'),seg1.mem_ST(seg1.mew_STRAIGHTNESS,'VERY_LOW')), seg1.mem_HP(seg1.mew_HP, 'CENTER'), seg1.mem_DL(seg1.mew_DL, 'HIGH'),\
                         seg2.mem_VP(seg2.mew_VP, 'BOTTOM_CENTER'),max(seg2.mem_ST(seg2.mew_STRAIGHTNESS,'LOW'),seg2.mem_ST(seg2.mew_STRAIGHTNESS,'ZERO'),seg2.mem_ST(seg2.mew_STRAIGHTNESS,'VERY_LOW')), seg2.mem_HP(seg2.mew_HP, 'CENTER'), seg2.mem_DL(seg2.mew_DL, 'HIGH'))
            prob_5 = min(max(seg1.mem_CL(seg1.mew_CL, 'HIGH'), seg1.mem_CL(seg1.mew_CL, 'MEDIUM')),seg1.mem_VP(seg1.mew_VP, 'TOP_CENTER'),seg1.mem_HP(seg1.mew_HP, 'CENTER'),\
                         max(seg2.mem_DL(seg2.mew_DL, 'HIGH'),seg2.mem_DL(seg2.mew_DL, 'MEDIUM')),seg2.mem_HP(seg2.mew_HP, 'CENTER'),seg2.mem_VP(seg2.mew_VP, 'BOTTOM_CENTER'))
            prob_6 = min(seg1.mem_CL(seg1.mew_CL, 'HIGH'),seg1.mem_VP(seg1.mew_VP, 'CENTER'),\
                         seg2.mem_DL(seg2.mew_DL, 'HIGH'),seg2.mem_VP(seg2.mew_VP, 'BOTTOM_CENTER'))
            prob_9 = min(seg1.mem_CL(seg1.mew_CL, 'HIGH'),seg1.mem_VP(seg1.mew_VP, 'TOP_CENTER'),\
                         seg2.mem_VP(seg2.mew_VP, 'CENTER'),max(seg2.mem_HP(seg2.mew_HP, 'RIGHT_CENTER'),seg2.mem_HP(seg2.mew_HP, 'RIGHT')))
            prob_0 = min(seg1.mem_CL(seg1.mew_CL, 'HIGH'),seg1.mem_VP(seg1.mew_VP, 'CENTER'),max(seg1.mem_HP(seg1.mew_HP, 'CENTER'),seg1.mem_HP(seg1.mew_HP, 'LEFT_CENTER')),\
                         seg2.mem_DL(seg2.mew_DL, 'HIGH'),seg2.mem_VP(seg2.mew_VP, 'CENTER'),seg2.mem_HP(seg2.mew_HP, 'RIGHT_CENTER'))'''

            prob_3 = min(seg1.mem_HOR(seg1.mew_HORIZONTAL,'HIGH'),seg1.mem_VP(seg1.mew_VP, 'TOP'),\
                         seg2.mem_PS(seg2.mew_PS,'HIGH'),seg2.mem_ST(seg2.mew_STRAIGHTNESS,'HIGH'),seg2.mem_VP(seg2.mew_VP, 'TOP_CENTER'),\
                         seg3.mem_VP(seg3.mew_VP, 'BOTTOM_CENTER'),max(seg3.mem_ST(seg3.mew_STRAIGHTNESS,'LOW'),seg3.mem_ST(seg3.mew_STRAIGHTNESS,'ZERO'),seg3.mem_ST(seg3.mew_STRAIGHTNESS,'VERY_LOW')), seg3.mem_HP(seg3.mew_HP, 'CENTER'), seg3.mem_DL(seg3.mew_DL, 'HIGH'))
            prob_4_1 = min(seg1.mem_HOR(seg1.mew_HORIZONTAL,'HIGH'),seg1.mem_VP(seg1.mew_VP, 'CENTER'),seg1.mem_HP(seg1.mew_HP, 'CENTER'),\
                         seg2.mem_PS(seg2.mew_PS,'HIGH'),seg2.mem_ST(seg2.mew_STRAIGHTNESS,'HIGH'),seg2.mem_VP(seg2.mew_VP, 'TOP_CENTER'),seg2.mem_HP(seg2.mew_HP, 'LEFT_CENTER'),\
                         seg3.mem_VER(seg3.mew_VERTICAL,'HIGH'),seg3.mem_VP(seg3.mew_VP, 'CENTER'),max(seg3.mem_HP(seg3.mew_HP, 'RIGHT_CENTER'),seg3.mem_HP(seg3.mew_HP, 'RIGHT')))
            prob_4_2 = min(max(seg1.mem_PS(seg1.mew_PS,'HIGH'),seg1.mem_VER(seg1.mew_VERTICAL, 'HIGH')),max(seg1.mem_ST(seg1.mew_STRAIGHTNESS,'HIGH'),seg1.mem_ST(seg1.mew_STRAIGHTNESS,'MEDIUM')),seg1.mem_VP(seg1.mew_VP, 'TOP_CENTER'),seg1.mem_HP(seg1.mew_HP, 'LEFT_CENTER'),\
                             max(seg2.mem_HOR(seg2.mew_HORIZONTAL,'MEDIUM'),seg2.mem_HOR(seg2.mew_HORIZONTAL,'HIGH')),seg2.mem_VP(seg2.mew_VP, 'CENTER'),seg2.mem_HP(seg2.mew_HP, 'CENTER'),\
                             max(seg3.mem_VER(seg3.mew_VERTICAL,'HIGH'), seg3.mem_HOR(seg3.mew_HORIZONTAL,'ZERO'),seg3.mem_HOR(seg3.mew_HORIZONTAL,'LOW'),seg3.mem_HOR(seg3.mew_HORIZONTAL,'VERY_LOW'), seg3.mem_PS(seg3.mew_PS, 'LOW')),seg3.mem_VP(seg3.mew_VP, 'CENTER'),max(seg3.mem_HP(seg3.mew_HP, 'RIGHT_CENTER'),seg3.mem_HP(seg3.mew_HP, 'RIGHT')))
            prob_7 = min(seg1.mem_HP(seg1.mew_HP, 'CENTER'), seg1.mem_VP(seg1.mew_VP, 'TOP'), seg1.mem_ST(seg1.mew_STRAIGHTNESS,'HIGH'), max(seg1.mem_HOR(seg1.mew_HORIZONTAL,'HIGH'),seg1.mem_HOR(seg1.mew_HORIZONTAL,'MEDIUM')),\
                         seg2.mem_ST(seg2.mew_STRAIGHTNESS,'HIGH'), seg2.mem_VP(seg2.mew_VP, 'CENTER'))
            prob_5=min(seg1.mem_HP(seg1.mew_HP, 'CENTER'), seg1.mem_VP(seg1.mew_VP, 'TOP'),seg1.mem_HOR(seg1.mew_HORIZONTAL,'HIGH'),\
                       seg2.mem_HP(seg2.mew_HP, 'LEFT'), seg2.mem_ST(seg2.mew_STRAIGHTNESS,'HIGH'), seg2.mem_VP(seg2.mew_VP, 'TOP_CENTER'),\
                       max(seg3.mem_DL(seg3.mew_DL, 'HIGH'),seg3.mem_DL(seg3.mew_DL, 'MEDIUM')),seg3.mem_HP(seg3.mew_HP, 'CENTER'),seg3.mem_VP(seg3.mew_VP, 'BOTTOM_CENTER'))
            for i in range (5):
                a = seg2.coord.pop(-1)
                print 'poping out ',a
            seg2.calc_boundary()
            seg2.calc_straightness()
            seg2.calc_len()
            seg2.calc_line_props()
            seg2.calc_pos()
            seg2.calc_UL()
            seg2.calc_AL()
            seg2.calc_CL()
            seg2.calc_DL()
            seg2.debug()
            prob_1 = min(max(seg1.mem_VP(seg1.mew_VP,'TOP_CENTER'), seg1.mem_VP(seg1.mew_VP, 'SLIGHT_TOP')), seg1.mem_ST(seg1.mew_STRAIGHTNESS,'HIGH'), max(seg1.mem_HOR(seg1.mew_HORIZONTAL,'ZERO'),seg1.mem_VER(seg1.mew_VERTICAL,'ZERO'), seg1.mem_VER(seg1.mew_VERTICAL,'VVL')), seg1.mem_PS(seg1.mew_PS,'HIGH'), seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'HIGH'), seg2.mem_VER(seg2.mew_VERTICAL, 'HIGH'),\
                          seg2.mem_ST(seg2.mew_STRAIGHTNESS, 'HIGH'), seg2.mem_VER(seg2.mew_VERTICAL, 'HIGH'),seg3.mem_HP(seg1.mew_HP, 'CENTER'),seg3.mem_VP(seg3.mew_VP, 'BOTTOM'),seg3.mem_HOR(seg3.mew_HORIZONTAL,'HIGH'))
            print 'msg prob_4_1:',prob_4_1,'prob_4_2:',prob_4_2
            self.prob_1 = prob_1
            self.prob_3 = prob_3
            self.prob_4 = max(prob_4_1,prob_4_2)
            self.prob_7 = prob_7
            self.prob_5 = prob_5





    def calc_boundary (self):
        x_list = []
        y_list = []
        for (x,y) in self.coord:
            x_list.append(x)
            y_list.append(y)
        self.x_max = max(x_list)
        self.y_max = max(y_list)
        self.x_min = min(x_list)
        self.y_min = min(y_list)
        self.x_center = (self.x_max+self.x_min)/2
        self.y_center = (self.y_max+self.y_min)/2
        slope_avg, intercept, r_value, p_value, slope_std_error = stats.linregress(x_list, y_list)
        self.AVG_SLOPE = slope_avg

        return

    #self.x_max = 0
    #self.y_max = 0
    #self.x_center = 0
    #self. y_center = 0

    step = 7
    seg_coord = []
    min_seg_thres = 20

    def prettify_segment(self):
        temp_seg_coord = list(self.seg_coord)
        print 'Temp_seg_coord are ',temp_seg_coord
        i = -1
        while(True):
            i = i+1
            if (i >= len(temp_seg_coord)):
                break
            print 'The value of i is', i
            if (len(temp_seg_coord[i]) < self.min_seg_thres) and (i != len(temp_seg_coord)-1):
                temp_sg=temp_seg_coord.pop(i)
                temp_seg_coord[i]=temp_sg + temp_seg_coord[i]
                i = i-1
        print 'PRETTIFIED LIST IS :',temp_seg_coord
        self.seg_coord = list(temp_seg_coord)


    def segment(self):
        last_break = 0
        for i in range(self.step, len(self.coord)-self.step,5):

            x_i = self.coord[i][0]
            y_i = self.coord[i][1]
            x_i_minus_step = self.coord[i-self.step][0]
            y_i_minus_step = self.coord[i-self.step][1]
            x_i_step = self.coord[i+self.step][0]
            y_i_step = self.coord[i+self.step][1]

            x_1_list = []
            y_1_list = []

            x_2_list = []
            y_2_list = []

            for j in range(i-self.step,i,1):
                x_1_list.append(self.coord[j][0])
                y_1_list.append(self.coord[j][1])

            for j in range(i,i+self.step,1):
                x_2_list.append(self.coord[j][0])
                y_2_list.append(self.coord[j][1])

            slope1, intercept, r_value, p_value, slope_std_error = stats.linregress(x_1_list, y_1_list)
            slope1  = math.fabs(slope1)

            slope2, intercept, r_value, p_value, slope_std_error = stats.linregress(x_2_list, y_2_list)
            slope2  = math.fabs(slope1)



            #slope1 = math.fabs(float(y_i) - y_i_minus_step)/(math.fabs(x_i - x_i_minus_step)+0.000000000001)
            psi1 = float(math.degrees(math.atan(slope1)))


            #slope2 = math.fabs(float(y_i_step) - y_i)/(math.fabs(x_i_step - x_i)+0.0001)
            psi2 = float(math.degrees(math.atan(slope2)))

            if((x_i_minus_step <= x_i) and (y_i_minus_step <= y_i)):
                theta1 = psi1
            elif ((x_i_minus_step >= x_i) and (y_i_minus_step <= y_i)):
                theta1 = 180 - psi1
            elif ((x_i_minus_step >= x_i) and (y_i_minus_step >= y_i)):
                theta1 = 180 + psi1
            elif ((x_i_minus_step <= x_i) and (y_i_minus_step >= y_i)):
                theta1 = 360 - psi1
            else:
                theta1 = psi1

            if((x_i <= x_i_step) and (y_i <= y_i_step)):
                theta2 = psi2
            elif ((x_i >= x_i_step) and (y_i <= y_i_step)):
                theta2 = 180 - psi2
            elif ((x_i >= x_i_step) and (y_i >= y_i_step)):
                theta2 = 180 + psi2
            elif ((x_i <= x_i_step) and (y_i >= y_i_step)):
                theta2 = 360 - psi2
            else:
                theta2 = psi2



            slope_diff = math.fabs(theta1-theta2)

            if slope_diff > 180:
                slope_diff = slope_diff - 180

            if slope_diff > 90:
                temp_list = []
                for c in self.coord[last_break:i]:
                    temp_list.append(c)
                self.seg_coord.append(temp_list)
                last_break = i
        temp_list = []
        for c in self.coord[last_break:len(self.coord)]:
            temp_list.append(c)
        self.seg_coord.append(temp_list)

    def segment1(self):
        last_break = 0
        for i in range(self.step, len(self.coord)-self.step,1):
            x_i = self.coord[i][0]
            y_i = self.coord[i][1]
            x_i_minus_step = self.coord[i-self.step][0]
            y_i_minus_step = self.coord[i-self.step][1]
            x_i_step = self.coord[i+self.step][0]
            y_i_step = self.coord[i+self.step][1]

            slope1 = math.fabs(float(y_i) - y_i_minus_step)/(math.fabs(x_i - x_i_minus_step)+0.0001)
            psi1 = math.degrees(math.atan(slope1))

            slope2 = math.fabs(float(y_i_step) - y_i)/(math.fabs(x_i_step - x_i)+0.0001)
            psi2 = math.degrees(math.atan(slope2))

            if((x_i_minus_step < x_i) and (y_i_minus_step < y_i)):
                theta1 = psi1
            elif ((x_i_minus_step > x_i) and (y_i_minus_step < y_i)):
                theta1 = 180 - psi1
            elif ((x_i_minus_step > x_i) and (y_i_minus_step > y_i)):
                theta1 = 180 + psi1
            elif ((x_i_minus_step < x_i) and (y_i_minus_step > y_i)):
                theta1 = 360 - psi1

            if((x_i < x_i_step) and (y_i < y_i_step)):
                theta2 = psi2
            elif ((x_i > x_i_step) and (y_i < y_i_step)):
                theta2 = 180 - psi2
            elif ((x_i > x_i_step) and (y_i > y_i_step)):
                theta2 = 180 + psi2
            elif ((x_i < x_i_step) and (y_i > y_i_step)):
                theta2 = 360 - psi2

            slope_diff = math.fabs(slope2-slope1)
            if slope_diff > 180:
                slope_diff = slope_diff - 180

            if slope_diff > 45:
                temp_list = []
                for c in self.coord[last_break:i]:
                    temp_list.append(c)
                self.seg_coord.append(temp_list)
                last_break = i
        temp_list = []
        for c in self.coord[last_break:len(self.coord)]:
            temp_list.append(c)
        self.seg_coord.append(temp_list)










class Example(wx.Frame):

    coord = []



    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title, style=wx.SYSTEM_MENU | wx.MAXIMIZE_BOX | wx.CAPTION | wx.CLOSE_BOX, size=(600, 600))

        self.InitUI()
        self.Centre()
        self.Show()

    def reset(self, e):
        print 'RESETING STARTED'
        if hasattr(self, 'temp_prev_x'):
            del self.temp_prev_x
        if hasattr(self, 'temp_prev_y'):
            del self.temp_prev_y
        self.numeral_instance.seg_coord = []
        #print 'DEBUG: check seg_coord is', self.numeral_instance.seg_coord
        if hasattr(self.numeral_instance, 'coord'):
            del self.numeral_instance.coord
        #if hasattr(self.numeral_instance, 'seg_coord'):
        #    del self.numeral_instance.seg_coord
        if hasattr(self.numeral_instance,'reset'):
            #print 'DEBUG: reset attr found'
            self.numeral_instance.reset()
        self.numeral_instance = None
        if hasattr(self, 'numeral_instance'):
            del self.numeral_instance
        self.coord = None
        self.coord = []
        #print 'after reseting coord is', self.coord
        self.seg_coord = []
        self.dc.Clear()
        #self.dc.Refresh()
        self.dc_in.Clear()
        #self.dc_in.Refresh()
        st_draw = wx.StaticText(self.top_panel, label='INPUT AREA: Draw the gesture in yellow box.', pos=(10,10))
        st_seg_out = wx.StaticText(self.top_panel, label='SEGMENTED OUTPUT: ', pos=(10,310))
        print 'RESETTING FINISHED'





    def InitUI(self):

        #self.bmp1 = wx.Image('a.gif', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        #self.bmp2 = wx.Image('b.gif', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        #self.bmp3 = wx.Image('c.gif', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        #self.bmp4 = wx.Image('d.gif', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        #self.bmp5 = wx.Image('e.gif', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        #self.bmp6 = wx.Image('f.gif', wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        self.top_panel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.midPan = wx.Panel(self.top_panel, size=(300,300))
        self.midPan.SetBackgroundColour('yellow')

        self.lowPan = wx.Panel(self.top_panel, size=(300,300))
        self.lowPan.SetBackgroundColour('GREY')

        vbox.Add(self.midPan, 1, wx.LEFT, 7)
        vbox.Add(self.lowPan, 1, wx.LEFT, 7)
        self.top_panel.SetSizer(vbox)

        #st_draw = wx.StaticText(self.top_panel, label='Draw the gesture of numeral by holding the mouse click and mouse-up wherever needed')
        st_draw = wx.StaticText(self.top_panel, label='INPUT AREA: Draw the gesture in yellow box.', pos=(10,10))
        st_seg_out = wx.StaticText(self.top_panel, label='SEGMENTED OUTPUT: ', pos=(10,310))
        menubar = wx.MenuBar()
        filem = wx.Menu()
        editm = wx.Menu()
        helpm = wx.Menu()

        menubar.Append(filem, '&File')
        menubar.Append(editm, '&Edit')
        menubar.Append(helpm, '&Help')
        self.SetMenuBar(menubar)

        self.midPan.Bind(wx.EVT_MOTION, self.OnMove)

        self.btn_submit = wx.Button(self.top_panel, label='Submit', size=(70, 50), pos=(350,100))
        self.btn_clear = wx.Button(self.top_panel, label='Clear', size=(70, 50), pos=(450,100))

        self.btn_submit.Bind(wx.EVT_LEFT_DOWN, self.onSubmit)
        self.btn_clear.Bind(wx.EVT_LEFT_DOWN, self.reset)
        #wx.TextCtrl(panel, pos=(3, 3), size=(250, 150))


    def onSubmit(self, e):

        self.numeral_instance = Numeral(list(self.coord))
        #self.numeral_instance.segment()
        length_bfr = len(self.numeral_instance.seg_coord)
        #self.numeral_instance.prettify_segment()
        print 'DEBUG: seg coords are',self.numeral_instance.seg_coord
        print 'length before prettifying is', length_bfr, 'and length after prettifying is', len(self.numeral_instance.seg_coord)
        self.show_segment()
        self.show_result()
        return

    def show_result(self):
        if(self.numeral_instance.mpv == None):
            msg = 'No numeral could be identified.'
        else:
            msg = 'The numeral is '+str(self.numeral_instance.mpv)
        wx.MessageBox(msg, 'Info', wx.OK | wx.ICON_INFORMATION)

    def show_segment(self):
        seg_coord = list(self.numeral_instance.seg_coord)
        zzz = 4
        #bmp_list = [self.bmp1, self.bmp2, self.bmp3, self.bmp4, self.bmp5, self.bmp6]
        #dc = wx.PaintDC(self)
        self.dc = wx.ClientDC(self.lowPan)

        for seg in seg_coord:
            zzz = zzz+1
            for (xx,yy) in seg:
                yy = 300-yy
                if (zzz%6 == 0):
                    self.dc.SetPen(wx.Pen('BLUE',3 , wx.SOLID))
                    self.dc.DrawPoint(xx, yy)
                    #bitmap1 = wx.StaticBitmap(self.lowPan, -1, self.bmp1, (xx, yy))
                elif (zzz%6 == 1):
                    self.dc.SetPen(wx.Pen('YELLOW',3 , wx.SOLID))
                    self.dc.DrawPoint(xx, yy)
                    #bitmap1 = wx.StaticBitmap(self.lowPan, -1, self.bmp2, (xx, yy))
                elif (zzz%6 == 2):
                    self.dc.SetPen(wx.Pen('BLACK',3 , wx.SOLID))
                    self.dc.DrawPoint(xx, yy)
                    #bitmap1 = wx.StaticBitmap(self.lowPan, -1, self.bmp3, (xx, yy))
                elif (zzz%6 == 3):
                    self.dc.SetPen(wx.Pen('ORANGE',3 , wx.SOLID))
                    self.dc.DrawPoint(xx, yy)
                    #bitmap1 = wx.StaticBitmap(self.lowPan, -1, self.bmp4, (xx, yy))
                elif (zzz%6 == 4):
                    self.dc.SetPen(wx.Pen('PINK',3 , wx.SOLID))
                    self.dc.DrawPoint(xx, yy)
                    #bitmap1 = wx.StaticBitmap(self.lowPan, -1, self.bmp5, (xx, yy))
                elif (zzz%6 == 5):
                    self.dc.SetPen(wx.Pen('RED',3 , wx.SOLID))
                    self.dc.DrawPoint(xx, yy)
                    #bitmap1 = wx.StaticBitmap(self.lowPan, -1, self.bmp6, (xx, yy))





    def OnMove(self, e):

        if e.Dragging() and e.LeftIsDown():
            print 'onmove called.'
            x, y = e.GetPosition()
            print 'moving at transformed coordinates',x,300-y


            self.dc_in = wx.ClientDC(self.midPan)
            self.dc_in.SetPen(wx.Pen('BLACK',2 , wx.SOLID))
            #self.img = 'b.gif'
            #self.bmp1 = wx.Image(self.img, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            #bitmap1 = wx.StaticBitmap(self.midPan, -1, self.bmp1, (x, y))
            #if hasattr(self, 'temp_prev_x') == False:

            #    self.temp_prev_x = x
            #    self.temp_prev_y= y

            #self.dc_in.DrawLine(self.temp_prev_x, self.temp_prev_y , x, y)
            self.dc_in.DrawPoint(x, y)

            self.coord.append((x,300-y))
            print 'length of coord is',len(self.coord)
            self.temp_prev_x = x
            self.temp_prev_y = y
        return






if __name__ == '__main__':

    app = wx.App()
    a = Example(None, title='Online Handwriting recognization')
    app.MainLoop()

from wpilib.command import Subsystem

from .cougarsystem import *

import ports
import wpilib
import math

from rev import CANSparkMax, MotorType, ControlType
from custom.config import Config

from networktables import NetworkTables as nt

class Hood(CougarSystem):
    '''Describe what this subsystem does.'''

    def __init__(self):
        super().__init__('Hood')
        
        disablePrints()

        self.motor = CANSparkMax(ports.hood.motorID, MotorType.kBrushless)
        self.encoder = self.motor.getEncoder()
        self.controller = self.motor.getPIDController()

        self.table = nt.getTable('Hood')

        self.controller.setP(0.001, 0)
        self.controller.setI(0, 0)
        self.controller.setD(0, 0)
        self.controller.setFF(0, 0)
        self.controller.setIZone(0, 0)

        source_ = wpilib.DigitalInput(ports.hood.absoluteThroughbore)
        self.tbEnc = wpilib.DutyCycle(source_)

        self.dir = 'u'
        self.setSpeed = 0.3

        self.angleMax = 240.00 # NOTE DO not actually make this 0 and 90. Place-holder only; make like 20, 110
        self.angleMin = 170.00 # was 166; need to adjust these values.
        self.LLHoodTuner = 13

        self.parallelToGroundish = 281.0
        self.llHeight = 19.5 # Height on robot.
        self.adjustment = 0

        self.zeroNetworkTables()

    def mobileHoodControl(self, y, areaControl=None):
        oldY = y
        mod = 0
        if areaControl != None:
            mod = (abs(areaControl) ** -0.2) * 5  # might need to check the signs here . . .
            y += mod

        #print('ogY ' + str(oldY))
        #print('moodddd ' + str(mod))
        #print('yyy ' + str(y))

        if abs(abs(oldY) - mod) <= 0.1: # Call oldY because this is the exact offset of the sensor.'
            self.stopHood()
            return True

        self.motor.set(math.copysign(max(min(0.6, abs(y / 80)), 0.03), -y))
        return False

    def getPosition(self):
        return self.tbEnc.getOutput() * 360

    def increaseAdjustment(self, val):
        self.adjustment = self.adjustment + val

    def decreaseAdjustment(self, val):
        self.adjustment = self.adjustment - val

    def setAdjustment(self, val):
        self.adjustment = val

    def getAdjustment(self):
        return self.adjustment

    def stopHood(self):
        self.motor.stopMotor()

    def setPercent(self, speed):
        self.motor.set(speed)

    def raiseHood(self):
        if self.getPosition() < self.angleMax:
            self.motor.set(0.1)
        else:
            self.motor.stopMotor()
        self.updateNetworkTables(self.getPosition())

    def lowerHood(self):
        print('hood ' + str(self.getPosition()))
        if self.getPosition() > self.angleMin:
            self.motor.set(-0.1)
        else:
            self.motor.stopMotor()
        self.updateNetworkTables(self.getPosition())

    def atHighest(self):
        if self.getPosition() >= self.angleMax:
            self.motor.stopMotor()
            return True
        else:
            return False

    def atLowest(self):
        if self.getPosition() <= self.angleMin:
            self.motor.stopMotor()
            return True
        else:
            return False

    def updateNetworkTables(self, angle=85.00):
        self.table.putNumber('HoodAngle', round(self.getPosition(), 2))
        self.table.putNumber('DesiredHoodAngle', round(angle, 2))
        self.table.putNumber('LaunchAngle', (((self.angleMax - self.getPosition()) / 2) + 8.84))
        self.table.putNumber('HoodAdjustment', round(self.adjustment, 2))

    def zeroNetworkTables(self):
        self.table.putNumber('HoodAngle', self.angleMin)
        self.table.putNumber('DesiredHoodAngle', self.angleMin)
        self.table.putNumber('LaunchAngle', self.angleMin)

    def OpenLoopSetPos(self, pos):
        self.angle = pos # give it in terms between min and max as of now, add 85 onto an angle between 0 and 35,
        # multiply that by 2: 85 + (2 * x). THIS WILL WORK
        if abs(self.getPosition() - self.angle) >= 2: # this way is better, angle will not be negative. 2 degrees of play
            self.rotate = .005 * (self.angle - self.getPosition()) # this should work
            self.setPercent(self.rotate)
        else:
            self.stopHood()

        self.updateNetworkTables(self.getPosition())

    def setShootAngle(self, angle):
        self.targetpos = self.angleMax - 2 * (angle - 8.84)
        self.error = -1* (self.getPosition() - self.targetpos)
        if (self.angleMin < self.targetpos < self.angleMax):
            if (abs(self.error) < .1):
                self.stopHood()
            else:
                self.speed = self.error * .01
                self.speed = math.copysign(min(0.5, abs(self.speed)), self.speed)
                self.setPercent(self.speed)

        return self.targetpos


    def setAngle(self, angle):
        self.targetpos = 260 - (2 * angle)
        self.error = -1 * (self.getPosition() - self.targetpos)
        if (self.angleMin < self.targetpos < self.angleMax):
            if (abs(self.error) < .1):
                self.stopHood()
            else:
                self.speed = self.error * .03
                if (abs(self.speed) > .5 ):
                    self.speed = math.copysign(.5, self.speed)
                self.setPercent(self.speed)

    def benCalcAngle(self, distance):
        y = 0.194735542 * abs(distance) + 170.4104165

        #theta = math.degrees(math.atan(98.25 - self.llHeight) / abs(distance))

        #y = -0.0014719708 * abs(distance) ** 2 + 0.739691936 * abs(distance) + 129.197073

        return self.benSetAngle(y)#self.parallelToGroundish - (theta * 2))

    def benSetAngle(self, desiredAngle):

        diff = self.getPosition() - desiredAngle

        if abs(diff) <= 3.0:
            self.stopHood()
            return True

        diff /= 120

        val = math.copysign(min(abs(max(abs(diff / 130), 0.08)), 0.3), -diff)

        self.motor.set(val)

        return False

    def goTo(self, angle): # angle is the raw encoder value.
        pos = self.getPosition()
        self.motor.set(math.copysign(max([0.3, (0.75 - max([angle / pos, pos / angle]))]), angle - pos)) # Damn, this is hot.

    def estimateAngle(self):
        return abs(self.parallelToGroundish - self.getPosition()) / 2

    def getLLHoodTuner(self):
        return self.LLHoodTuner

    def withinBounds(self):
        return (self.angleMin <= self.getPosition() <= self.angleMax)
    
    def alignAxises(self, y):
        if abs(y) <= 0.1:
            self.stopHood()
            return True
        
        self.motor.set(math.copysign(max(min(0.6, abs(y / 80)), 0.03), -y))
        
        return False
    
    def alignAxisesFar(self, y, area):
        y += self.calcOffset(area) 
        if abs(y) <= 0.1:
            self.stopHood()
            return True
        
        self.motor.set(math.copysign(max(min(0.6, abs(y / 80)), 0.03), -y))
    
        return False
    
    def calcOffset(self, area):
        return (1.5 - abs(area)) / 0.32

#!/usr/bin/env python3

import wpilib.command
wpilib.command.Command.isFinished = lambda x: False

from commandbased import CommandBasedRobot
from wpilib._impl.main import run
from wpilib import RobotBase

from rev import MotorType, CANSparkMax

from custom import driverhud
import controller.layout
import subsystems 
import shutil, sys

from subsystems.cougarsystem import CougarSystem
from wpilib.command import Subsystem

from subsystems.monitor import Monitor as monitor

from subsystems.revolver import Revolver as revolver
from subsystems.balllauncher import BallLauncher as balllauncher
from subsystems.shooter import Shooter as shooter
from subsystems.intake import Intake as intake
from subsystems.pneumatics import Pneumatics as pneumatics
from subsystems.ledsystem import LEDSystem as ledsystem
from subsystems.hood import Hood as hood
from subsystems.turret import Turret as turret
from subsystems.limelight import Limelight as limelight
from subsystems.climber import Climber as climber

from subsystems.falconbasedrive import FalconBaseDrive
from subsystems.neobasedrive import NeoBaseDrive

class KryptonBot(CommandBasedRobot):
    '''Implements a Command Based robot design'''

    def robotInit(self):
        print("robot init")
        '''Set up everything we need for a working robot.'''
        if RobotBase.isSimulation():
            import mockdata

        from subsystems.drivetrain import selectAgain
        from subsystems.skiddrive import selectDT
                
        if self.checkDrive():
                        
            skClass = selectDT(FalconBaseDrive)
            dtClass = selectAgain(skClass)
            
            setattr(sys.modules['robot'], 'drivetrain', dtClass())
            
        else:
            skClass = selectDT(NeoBaseDrive)
            dtClass = selectAgain(skClass)
            
            setattr(sys.modules['robot'], 'drivetrain', dtClass())
            
        del self.testMotor
        
        self.subsystems()

        controller.layout.init()
        driverhud.init()

        from commands.startupcommandgroup import StartUpCommandGroup
        StartUpCommandGroup().start()

    def autonomousInit(self):
        print("robot auto init")
        '''This function is called each time autonomous mode starts.'''

        # Send field data to the dashboard
        driverhud.showField()

        # Schedule the autonomous command
        auton = driverhud.getAutonomousProgram()
        auton.start()
                
        driverhud.showInfo("Starting %s" % auton)

    def disabledInit(self):
        self.captureDisbaleVars()

    def handleCrash(self, error):
        super().handleCrash()
        driverhud.showAlert('Fatal Error: %s' % error)

    def captureDisbaleVars(self):
        writeThese = []
        vars = globals()
        module = sys.modules['robot']

        for key, var in vars.items():
            try:
                if issubclass(var, CougarSystem) and var is not CougarSystem:
                    object_ = getattr(module, key)
                    try:
                        for data in object_.writeOnDisable:
                            writeThese.append([data[0], data[1], eval('object_' + str(data[2]))])
                    except(AttributeError):
                        pass
                    
            except(TypeError):
                continue

        try:
            with open('/home/lvuser/py/data.txt', 'w') as f:
                #print('len ' + str(writeThese))
                for listitem in writeThese:
                    f.write(str(listitem) + '\n')
        except(FileNotFoundError):
            pass
        
    def checkDrive(self):
        self.testMotor = CANSparkMax(1, MotorType.kBrushless)
        
        print(self.testMotor.getFirmwareString()[-11:].lower())
        
        return (self.testMotor.getFirmwareString()[-11:]).lower() == 'debug build' # True if Falcon (comp bot)
    
    @classmethod
    def subsystems(cls):
        vars = globals()
        module = sys.modules['robot']
        
        for key, var in vars.items():
            try:
                if issubclass(var, Subsystem) and var is not Subsystem and var is not CougarSystem and var is not FalconBaseDrive and var is not NeoBaseDrive and var:
                    try:
                        setattr(module, key, var())
                    except TypeError as e:
                        raise ValueError(f'Could not instantiate {key}') from e
            except TypeError:
                pass

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'deploy':
        shutil.rmtree('opkg_cache', ignore_errors=True)
        shutil.rmtree('pip_cache', ignore_errors=True)

    run(KryptonBot)

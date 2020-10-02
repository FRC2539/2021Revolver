from wpilib.command import Command

import robot


class FireSequenceCommand(Command):

    def __init__(self):
        super().__init__('Fire Sequence')

        self.requires(robot.revolver)
        self.requires(robot.balllauncher)

        robot.revolver.sequenceEngaged = False
        self.proceed = False

    def initialize(self):
        self.proceed = False
        
        robot.revolver.sequenceEngaged = True
        
        robot.revolver.resetRevolverEncoder()
        robot.pneumatics.retractBallLauncherSolenoid()
        
        #if all(abs(x) <= 10 for x in robot.drivetrain.getSpeeds()):
            #robot.revolver.setStaticSpeed()
        
        robot.revolver.setStaticSpeed()

        self.startPos = robot.revolver.getPosition()
        self.goTo = self.startPos - 10 
        
        if self.goTo < 0:
            self.goTo += 360

    def execute(self):
        print('\ntarget stat\n ' + str(robot.turret.onTarget))
        print('revPos: '+str(robot.revolver.getPosition()))
        if abs(self.goTo - robot.revolver.getPosition()) <= 5 and robot.turret.onTarget and not self.proceed:# and all(abs(x) <= 10 for x in robot.drivetrain.getSpeeds()):
            print('proceed')
            self.proceed = True
        
        print(robot.shooter.getRPM())
        print('d' + str(robot.revolver.inDropZone()))
        
        if robot.shooter.atGoal and robot.revolver.inDropZone() and self.proceed:
            print('shoot')
            robot.revolver.setStaticSpeed()
            robot.balllauncher.launchBalls()
            robot.pneumatics.extendBallLauncherSolenoid()

    def end(self):
        robot.revolver.sequenceEngaged = False
        self.proceed = False

        robot.pneumatics.retractBallLauncherSolenoid()
        robot.balllauncher.stopLauncher()
        robot.revolver.stopRevolver()

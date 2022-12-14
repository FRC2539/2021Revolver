from wpilib.command import Command

from subsystems.cougarsystem import *

import robot

class DefaultCommand(Command):

    def __init__(self):
        super().__init__('Default for pneumatics')

        self.requires(robot.ledsystem)
        self.requires(robot.pneumatics)
        
        robot.pneumatics.override = False

    def initalize(self):
        robot.ledsystem.rainbowLava()

    def execute(self):

        # Air
        
        #print(robot.pneumatics.intakeSolenoid.get())
        #print(robot.pneumatics.isIntakeLowered())
        
        robot.pneumatics.updatePressure()
        
        if not robot.shooter.shooting and not robot.intake.intaking and not robot.pneumatics.override: # If our pressure is low, run this. 
            robot.pneumatics.enableCLC()
            
        else:
            robot.pneumatics.disableCLC() # Call this just to ensure the compressor is always stopped. 
            robot.pneumatics.stopCompressor()
            
        # Intake / Revolver
        
        # Runs the auto intake during autonomous.
        
        if robot.revolver.defaultCheck:
            if robot.revolver.isEmpty():
                robot.revolver.stopRevolver()
            else:
                robot.revolver.setVariableSpeed(-0.2)
            
        # LEDs
        
        # Shooting should look like:
        # WHITE -> GREEN -> ORANGE
        # The heartbeat is determined by the air pressure. A hearbeat signal means LOW pressure (bad).
        # WHITE to let you know shooter isn't at speed yet, GREEN then to let you know at speed and ready,
        # just continue with the FireSequence command. Then, the ORANGE should be shooting balls.
        
        if robot.pneumatics.isCompressorRunning(): # Use heartbeat style.
                                                
            if robot.shooter.atGoal: # The shooter has reached the goal. Technically, don't need to check for shooting here.
                #print('at goal\n')
                
                if robot.revolver.sequenceEngaged: 
                    robot.ledsystem.colorOneHeartbeat() # Shooting!
                else:
                    robot.ledsystem.colorTwoHeartbeat() # Ready to shoot! (Green heartbeat)
            
            elif robot.shooter.shooting: # Not at the goal yet.
                robot.ledsystem.whiteHeartbeat()
                
            elif robot.intake.intaking: # Going to intake balls.
                robot.ledsystem.blueHeartbeat()
                
            else:
                robot.ledsystem.redHeartbeat() # Compressor should be running, because we ain't shooting. Intake will mask the compressor running however.
                
        else: # Use standard style. 
                        
            if robot.shooter.atGoal:
                
                if robot.revolver.sequenceEngaged:
                    robot.ledsystem.colorOneStrobe() # Shooting!
                else:
                    robot.ledsystem.setGreen() # Ready to shoot!
            
            elif robot.shooter.shooting:
                robot.ledsystem.setWhite()
                
            elif robot.intake.intaking:
                robot.ledsystem.setBlue()
                
            else:
                robot.ledsystem.rainbowLava() # The default, good to go setting.
        
    def end(self):
        robot.ledsystem.off() # Turn the LEDs off when we're done with the robot. 

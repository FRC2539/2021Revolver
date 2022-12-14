from wpilib.command import Command

import robot

class EnsureEmptinessCommand(Command):

    def __init__(self):
        super().__init__('Ensure Emptiness')

        self.requires(robot.revolver)

    def initialize(self):
        robot.revolver.setCustomRR(0.5)
        robot.pneumatics.extendIntakeSolenoid()
        if robot.revolver.isEmpty():
            robot.revolver.stopRevolver()
        else:
            robot.revolver.setVariableSpeed(-0.2)
    
    def execute(self):
        if robot.revolver.isEmpty():
            robot.revolver.stopRevolver()
        else:
            robot.revolver.setVariableSpeed(-0.2)
            
    def end(self):
        robot.intake.stopIntake()
        robot.pneumatics.retractIntakeSolenoid()
        robot.revolver.stopRevolver()
        robot.revolver.enableRampRate()
        

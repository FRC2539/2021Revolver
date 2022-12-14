from commands.balllauncher.extendlaunchercommand import ExtendLauncherCommand
from commands.balllauncher.launchballscommand import LaunchBallsCommand
from commands.balllauncher.reverseballscommand import ReverseBallsCommand

from commands.hood.lowerhoodcommand import LowerHoodCommand
from commands.hood.raisehoodcommand import RaiseHoodCommand

from commands.intake.deployintakecommand import DeployIntakeCommand
from commands.intake.intakecommand import IntakeCommand
from commands.intake.loadinemptycommandgroup import LoadInEmptyCommandGroup
from commands.intake.outakecommand import OutakeCommand
from commands.intake.kickcommand import KickCommand

from commands.limelight.sudocommandgroup import SudoCommandGroup

from commands.revolver.intakedirectioncommand import IntakeDirectionCommand
from commands.revolver.shooterdirectioncommand import ShooterDirectionCommand
from commands.revolver.variablespeedcommand import VariableSpeedCommand
from commands.revolver.firesequencecommand import FireSequenceCommand

from commands.shooter.endshootingprocesscommand import EndShootingProcessCommand
from commands.shooter.setrpmcommand import SetRPMCommand
from commands.shooter.shootwhenreadycommand import ShootWhenReadyCommand

from commands.turret.toggleturretmodecommand import ToggleTurretModeCommand
from commands.turret.turretlimelightcommand import TurretLimelightCommand
from commands.turret.increaseturretadjustmentcommand import IncreaseTurretAdjustmentCommand
from commands.turret.decreaseturretadjustmentcommand import DecreaseTurretAdjustmentCommand

from commands.hood.increasehoodadjustmentcommand import IncreaseHoodAdjustmentCommand
from commands.hood.decreasehoodadjustmentcommand import DecreaseHoodAdjustmentCommand

from commands.drivetrain.boogitycommand import BoogityCommand
from commands.drivetrain.autopilotcommand import AutoPilotCommand
from commands.drivetrain.musiccommand import MusicCommand
from commands.drivetrain.cyclesongleft import CycleSongLeft
from commands.drivetrain.cyclesongright import CycleSongRight
from commands.drivetrain.recordmovecommand import RecordMoveCommand
from commands.drivetrain.setpointcommand import SetPointCommand

from commands.shooter.maketherobotshootballsandonlyshootballscommand import MakeTheRobotShootBallsAndOnlyShootBallsCommand
from commands.revolver.actualrevolvershakecommand import ActualRevolverShakeCommand
from commands.revolver.revolvergobackcommand import RevolverGoBackCommand

from commands.resetcommand import ResetCommand
from . import logicalaxes
from .logitechdualshock import LogitechDualShock


def init():
    '''
    Declare all controllers, assign axes to logical axes, and trigger
    commands on various button events. Available event types are:
        - whenPressed
        - whileHeld: cancelled when the button is released
        - whenReleased
        - toggleWhenPressed: start on first press, cancel on next
        - cancelWhenPressed: good for commands started with a different button
    '''

    # The controller for driving the robot

    driveController = LogitechDualShock(0)

    operatorController = LogitechDualShock(1)

    logicalaxes.driveX = driveController.LeftX
    logicalaxes.driveY = driveController.LeftY
    logicalaxes.driveRotate = driveController.RightX
    logicalaxes.speedControl = driveController.RightY

    logicalaxes.turretX = operatorController.RightX

    driveController.Back.whenPressed(ResetCommand())
    driveController.Start.toggleWhenPressed(MusicCommand())

    driveController.A.whenPressed(IntakeCommand()) # Used at pickup station
    driveController.B.toggleWhenPressed(ShooterDirectionCommand())
    driveController.X.toggleWhenPressed(LaunchBallsCommand())
    driveController.Y.toggleWhenPressed(IntakeDirectionCommand())

    driveController.DPadUp.toggleWhenPressed(SudoCommandGroup(False))
    
    driveController.DPadRight.whileHeld(VariableSpeedCommand(-0.4))
    driveController.DPadLeft.whileHeld(VariableSpeedCommand(0.4))

    driveController.RightBumper.toggleWhenPressed(ExtendLauncherCommand())

    driveController.LeftTrigger.toggleWhenPressed(RecordMoveCommand())
    driveController.A.whenPressed(SetPointCommand())

    driveController.RightJoystick.whenPressed(KickCommand()) # Used on field
    driveController.LeftJoystick.whenPressed(IntakeCommand())
    
    #driveController.Start.toggleWhenPressed(SetRPMCommand(5000))

    # The controller for non-driving subsystems of the robot
    # actually just the driver controller but some stuff is switched (A and B, left trigger and bumper) and a command is gone

# operatorController goals:
# Needed buttons / controls:
# limelight control, with individual commands or sudo command (turret, shooter, hood)
# limelight adjustment, (hood up, down, turret left, right)
# Spin revolver
# Shoot balls
# turret control - joystick

    operatorController.RightBumper.toggleWhenPressed(SudoCommandGroup(False))

    operatorController.DPadUp.whileHeld(IncreaseHoodAdjustmentCommand())
    operatorController.DPadRight.whileHeld(IncreaseTurretAdjustmentCommand())
    operatorController.DPadDown.whileHeld(DecreaseHoodAdjustmentCommand())
    operatorController.DPadLeft.whileHeld(DecreaseTurretAdjustmentCommand())

    operatorController.A.toggleWhenPressed(MakeTheRobotShootBallsAndOnlyShootBallsCommand())
    operatorController.B.toggleWhenPressed(ReverseBallsCommand())
    operatorController.X.toggleWhenPressed(ActualRevolverShakeCommand())
    operatorController.Y.toggleWhenPressed(RevolverGoBackCommand())

    #operatorController.DPadUp.toggleWhenPressed(ExtendLauncherCommand())
    #operatorController.DPadDown.toggleWhenPressed(LoadInEmptyCommandGroup())
    #operatorController.DPadRight.toggleWhenPressed(SudoCommandGroup())

    operatorController.RightTrigger.toggleWhenPressed(ShooterDirectionCommand()) 

    #operatorController.RightBumper.whileHeld(TurretLimelightCommand()) # First

    operatorController.LeftTrigger.whileHeld(RaiseHoodCommand())
    operatorController.LeftBumper.whileHeld(LowerHoodCommand())
    
    #operatorController.X.toggleWhenPressed(BoogityCommand())

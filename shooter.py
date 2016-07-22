from enum import Enum
import wpilib

PICKUP_POWER = 0.75
LAUNCH_POWER = 1
SPINUP_TIME = 1.5 #Seconds
LAUNCH_TIME = 0.5

class ShooterState(Enum):
    READY = 1,
    ON_FIRE = 2,
    SPINNING_UP = 3,
    LAUNCH = 4,
    LAUNCHING = 5,
    RESETTING = 6

class shooter():
    def __init__(self, *args):
        self.launcher = args[0]
        self.pickup = args[1]
        self.ramp = args[2]
        self.ready = True
        self.state = ShooterState.READY
        self.shotClock = wpilib.Timer
    def deleteShooter(self):
        del self.launcher
        del self.pickup
        del self.ramp
    def stopShooter(self):
        self.ready = True
        self.ramp.set(0)
        self.pickup.set(0)
    def lowerRamp(self):
        self.ramp.set(-0.5)
    def raiseRamp(self):
        self.ramp.set(0.5)
    def stopRamp(self):
        self.ramp.set(0)
    def shoot(self):
        if self.state == ShooterState.READY:
            self.state = ShooterState.SPINNING_UP
            self.ramp.set(-1)
            self.launcher.set(PICKUP_POWER)
            self.shotClock.reset()
            self.shotClock.start()
            #break alternative?
        elif self.state == ShooterState.SPINNING_UP:
            if (self.shotClock.get() > SPINUP_TIME):
                self.state = ShooterState.LAUNCH
                self.shotClock.reset()
                self.shotClock.start()
            else:
                message = "Goku noises"
        elif self.state == ShooterState.LAUNCH:
            self.ramp.set(1)
            self.state = ShooterState.LAUNCHING
        elif self.state == ShooterState.LAUNCHING:
            if (self.shotClock.get() > LAUNCH_TIME):
                self.state = ShooterState.RESETTING
        elif self.state == ShooterState.RESETTING:
            self.ramp.set(0)
            self.launcher.set(0)
            self.pickup.set(0)
            self.state = ShooterState.READY
        elif self.state == ShooterState.ON_FIRE:
            message = "Something is wrong here"
    def pickUp(self, pickUpState = True):
        self.pickup.set(pickUpState * PICKUP_POWER)
        self.launcher.set(pickUpState * PICKUP_POWER * -0.75)
    def unJam(self):
        self.pickup.set(PICKUP_POWER * -0.75)
    def shootLow(self):
        self.pickup.set(-1)
    def setPower(self, power):
        self.pickup.set(power)
        self.launcher.set(power)
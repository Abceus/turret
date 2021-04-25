import RPi.GPIO as GPIO

class ServoControll:
    def __init__(self, max, min, speed_percent, pin_num, frequency=50):
        self.speed_percent = speed_percent
        self.pin_num = pin_num
        self.max = max
        self.min = min
        self.speed = (self.max - self.min) * (self.speed_percent / 100.0)
        self.current = 0.0
        GPIO.setup(self.pin_num, GPIO.OUT)
        self.pin = GPIO.PWM(self.pin_num, frequency)
        self.pin.start(0.0)
        self.pin.ChangeDutyCycle(self.min)

    def rotate(self, offset):
        self.current = min(max(self.current + (offset * self.speed), 0.0), 2.0)
        percent = self.current / 2.0
        pos = max(min(self.min + (self.max - self.min) * percent, self.min), self.max)
        # print(pos)
        self.pin.ChangeDutyCycle(pos)
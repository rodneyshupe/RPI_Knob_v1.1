from RPi import GPIO
import math


class LightArray:
    def __init__(self, light_pins):
        self.light_pins = light_pins

        GPIO.setmode(GPIO.BCM)
        for pin in light_pins:
            GPIO.setup(pin, GPIO.OUT)

        GPIO.output(light_pins[0], GPIO.HIGH)

    def set_value(self, percentage):
        n_pins = int(math.floor(percentage / (len(self.light_pins)-1)))
        for i in range(len(self.light_pins)):
            if i <= n_pins:
                GPIO.output(self.light_pins[i], GPIO.HIGH)
            else:
                GPIO.output(self.light_pins[i], GPIO.LOW)

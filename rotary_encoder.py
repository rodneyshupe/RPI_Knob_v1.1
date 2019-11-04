#!/usr/bin/env python3

"""
The daemon responsible for changing the volume in response to a turn or press
of the volume knob.
The volume knob is a rotary encoder. It turns infinitely in either direction.
Turning it to the right will increase the volume; turning it to the left will
decrease the volume. The knob can also be pressed like a button in order to
turn muting on or off.
The knob uses two GPIO pins and we need some extra logic to decode it. The
button we can just treat like an ordinary button. Rather than poll
constantly, we use threads and interrupts to listen on all three pins in one
script.
"""

import os

from RPi import GPIO


class RotaryEncoder:
    """
    A class to decode mechanical rotary encoder pulses.
    Ported to RPi.GPIO from the pigpio sample here:
    http://abyz.co.uk/rpi/pigpio/examples.html
    """

    def __init__(self, gpioA, gpioB, callback=None, buttonPin=None, buttonCallback=None):
        """
        Instantiate the class. Takes three arguments: the two pin numbers to
        which the rotary encoder is connected, plus a callback to run when the
        switch is turned.

        The callback receives one argument: a `delta` that will be either 1 or -1.
        One of them means that the dial is being turned to the right; the other
        means that the dial is being turned to the left. I'll be damned if I know
        yet which one is which.
        """

        self.lastGpio = None
        self.gpioA = gpioA
        self.gpioB = gpioB
        self.callback = callback

        self.gpioButton = buttonPin
        self.buttonCallback = buttonCallback

        self.levA = 0
        self.levB = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpioA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.gpioB, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(self.gpioA, GPIO.BOTH, self._callback)
        GPIO.add_event_detect(self.gpioB, GPIO.BOTH, self._callback)

        if self.gpioButton:
            GPIO.setup(self.gpioButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(
                self.gpioButton, GPIO.FALLING, self._buttonCallback, bouncetime=500)

    def destroy(self):
        GPIO.remove_event_detect(self.gpioA)
        GPIO.remove_event_detect(self.gpioB)
        GPIO.cleanup()

    def _buttonCallback(self, channel):
        self.buttonCallback(GPIO.input(channel))

    def _callback(self, channel):
        level = GPIO.input(channel)
        if channel == self.gpioA:
            self.levA = level
        else:
            self.levB = level

        # Debounce.
        if channel == self.lastGpio:
            return

        # When both inputs are at 1, we'll fire a callback. If A was the most
        # recent pin set high, it'll be forward, and if B was the most recent pin
        # set high, it'll be reverse.
        self.lastGpio = channel
        if channel == self.gpioA and level == 1:
            if self.levB == 1:
                self.callback(1)
        elif channel == self.gpioB and level == 1:
            if self.levA == 1:
                self.callback(-1)

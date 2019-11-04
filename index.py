import time
from rotary_encoder import RotaryEncoder
from light_array import LightArray
import signal
import subprocess
import sys
import threading
from Queue import Queue
import math

import argparse
from ensign_client import update_flag, get_percentage

parser = argparse.ArgumentParser()
parser.add_argument('--environment', '-e', help='The application environment')
parser.add_argument('--app', '-a', help='The application name')
parser.add_argument('--namespace', '-ns', help='The flag namespace')
parser.add_argument('--name', '-n', help='The flag name')
args = parser.parse_args()

use_ensign = (args.environment != None and args.app != None and args.namespace != None and args.name != None)

GPIO_A = 19
GPIO_B = 26
LED_PINS = [18, 23, 17, 22, 27, 10, 9, 11, 0, 5, 6]

QUEUE = Queue()
EVENT = threading.Event()


class Counter:
    def __init__(self, percentage=0, n_clicks=24):
        self.percentage = percentage
        self.n_clicks = n_clicks

    def count(self, delta):
        n = delta * 100 / self.n_clicks
        self.percentage = max(0, min(100, self.percentage + n))


if __name__ == "__main__":
    print "start"

    initial_percentage = 0
    if use_ensign:
        initial_percentage = get_percentage(**vars(args))
    counter = Counter(initial_percentage)
    light_array = LightArray(LED_PINS)

    gpioA = GPIO_A
    gpioB = GPIO_B

    light_array.set_value(counter.percentage)

    def on_turn(delta):
        QUEUE.put(delta)
        EVENT.set()

    def consume_queue():
        while not QUEUE.empty():
            delta = QUEUE.get()
            handle_delta(delta)

    def handle_delta(delta):
        counter.count(delta)
        light_array.set_value(counter.percentage)
        print counter.percentage

    def on_click(value):
        print("Button click")
        if use_ensign:
            update_flag(percentage=counter.percentage, **vars(args))

    def on_exit(a, b):
        print("Exiting...")
        encoder.destroy()
        sys.exit(0)

    encoder = RotaryEncoder(GPIO_A, GPIO_B, callback=on_turn,
                            buttonPin=13, buttonCallback=on_click)
    signal.signal(signal.SIGINT, on_exit)

    while True:
        # This is the best way I could come up with to ensure that this script
        # runs indefinitely without wasting CPU by polling. The main thread will
        # block quietly while waiting for the event to get flagged. When the knob
        # is turned we're able to respond immediately, but when it's not being
        # turned we're not looping at all.
        #
        # The 1200-second (20 minute) timeout is a hack; for some reason, if I
        # don't specify a timeout, I'm unable to get the SIGINT handler above to
        # work properly. But if there is a timeout set, even if it's a very long
        # timeout, then Ctrl-C works as intended. No idea why.
        EVENT.wait(1200)
        consume_queue()
        EVENT.clear()

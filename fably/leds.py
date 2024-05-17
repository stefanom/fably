"""Code to manage a series of LEDs."""

import time
import threading

try:
    from apa102_pi.driver import apa102
except (ImportError, NotImplementedError):
    apa102 = None

from fably import utils


class LEDs:
    """Class to manage a series of rgb LEDs."""

    def __init__(self, colors, brightness=1, step=1, pause=0.007):
        self.colors = colors
        self.brightness = brightness
        self.step = step
        self.pause = pause
        self.running = False
        self.thread = None

    def _run(self):
        # If we can't load the library, we can't do anything.
        # We shoudl not be getting here but just in case.
        if not apa102:
            return

        strip = apa102.APA102(num_led=len(self.colors))
        strip.clear_strip()

        while self.running:
            for i, color in enumerate(self.colors):
                new_color = utils.rotate_rgb_color(color, self.step)
                strip.set_pixel_rgb(i, new_color, self.brightness)
                self.colors[i] = new_color
            strip.show()
            time.sleep(self.pause)

        strip.clear_strip()
        strip.cleanup()

    def start(self):
        if not apa102 or self.thread:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def stop(self):
        if self.thread and self.running:
            self.running = False
            self.thread.join()
            self.thread = None

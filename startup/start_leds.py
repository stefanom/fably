#!/usr/bin/env python
import time

from pixels import Pixels

if __name__ == '__main__':
    pixels = Pixels()

    pixels.speak()
    time.sleep(3)
    pixels.off()

    time.sleep(1)

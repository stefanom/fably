#!/usr/bin/env python

from apa102_pi.colorschemes import colorschemes

NUM_LED = 3
BRIGHTNESS = 15

def main():
    my_cycle = colorschemes.TheaterChase(num_led=NUM_LED, pause_value=0.03,
                                         num_steps_per_cycle=35, num_cycles=1, order='rgb',
                                         global_brightness=BRIGHTNESS)
    my_cycle.start()


if __name__ == '__main__':
    main()

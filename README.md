# Fably

A device that tells bedtime stories to kids

![fably](https://raw.githubusercontent.com/stefanom/fably/main/images/fably.webp)


# Hardware

You will need:

 - a Raspberry Pi Zero 2w (amazon)
 - a mic hat
 - a power supply
 - a bluetooth speaker (you can also use a google home or similar)


# Software

# Step 1 - Install Raspian on the rPI

To install the OS we recommend using the official installer located at https://www.raspberrypi.com/software/.

The best choice is the "Raspberry Pi OS (legacy, 64-bit) Lite" which contains the bare minimum to get us going but consumes the least amount of resources and contains the minimum amount of attack surface.

Note that you can press "Ctrl+Shift+X" to open the advanced options that allow you to setup your device with things like hostname, ssh and wifi password. See https://kevinhaffner.blogspot.com/2021/06/hidden-settings-in-raspberry-pi-imager.html for more details.

Once you are able to ssh into the device, you're ready for the next step.

# Step 2 - Install Fably into the rPI

ssh into the rPI and type

```bash
git clone https://github.com/stefanom/fably
cd fably
```

these commands copied the contents of this git repo onto your device in a folder named `fably` and then moved you into it. If everything went well, you're ready to go to the next step.

# Step 3 - Configure the rPI

We want this little machine to be as low maintenance as possible but this also means that it needs to be smart enough to update itself and do all those nice things.

... more later ...
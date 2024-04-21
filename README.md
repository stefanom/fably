# Fably

Use AI to generate and tell bedtime stories to kids.

Run it on your computer or on very cheap (<30$) hardware.

<img src="https://raw.githubusercontent.com/stefanom/fably/main/images/fably.webp" alt="Fably" width="300" height="300"/>

## Installation

All you need to get started is a computer (doesn't matter which operating system) with:

* python installed
* git installed
* a speaker

type this into your command line

```sh
git clone git@github.com:stefanom/fably.git
cd fably
pip install -r requirements.txt
```

### Listening to examples

In the `example` folder, there are several examples of generated stories along with the synthetized speech. You can listen to them directly here from github or you can run the following command to run use Fably itself to tell the story already generated

```sh
python fably.py --query "Tell me a story about a princess and a frog" --stories-home=./examples/openai_cheap
```

will play the example from `openai_cheap` which uses GPT-3.5 and TTS-1 as the LLM and TTS model respectively. If you change the above to `openai_expensive`, it will play the example from `openai_expensive` which used GPT-4 and TTS-1-HD instead.

### Setting up the OpenAI Key

Go to https://platform.openai.com/api-keys and obtain a new API key.

Then run this command in Windows

```sh
copy env.example .env
```

or this command in MacOS/Linux

```sh
cp env.example .env
```

and add your OpenAI key in that file.

### Creating a story

For this, we'll need to have a microphone available to our computer. Once a microphone is available, run this command to create a story and listen to it:

```bash
python fably.py 
```

Say out loud "tell me a story about a dog" and ear the magic.

## Troubleshooting

We'll add more content here as we run into issues.

## Installing on a RaspberryPI Zero 2W

We will need:

* a Raspberry Pi Zero 2w
* a mic hat (as the zero doesn't a mic nor USB ports)
* a power supply
* a bluetooth speaker

### Step 1 - Install Raspian on the rPI

To install the OS we recommend using the official installer located at https://www.raspberrypi.com/software/.

The best choice is the "Raspberry Pi OS (legacy, 64-bit) Lite" which contains the bare minimum to get us going but consumes the least amount of resources and contains the minimum amount of attack surface.

Note that you can press "Ctrl+Shift+X" to open the advanced options that allow you to setup your device with things like hostname, ssh and wifi password. See https://kevinhaffner.blogspot.com/2021/06/hidden-settings-in-raspberry-pi-imager.html for more details.

Once you are able to ssh into the device, you're ready for the next step.

### Step 2 - Install Fably into the rPI

ssh into the rPI and type

```bash
git clone https://github.com/stefanom/fably
cd fably
pip install -r requirements.txt
pip install git+https://github.com/pybluez/pybluez.git#egg=pybluez
```

### Step 3 - Configure the rPI

We want this little machine to be as low maintenance as possible but this also means that it needs to be smart enough to update itself and do all those nice things.

... more later ...

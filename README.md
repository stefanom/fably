# Fably

A device that tells bedtime stories to kids

![fably](https://raw.githubusercontent.com/stefanom/fably/main/images/fably.webp)

## How does it work?

Fably uses generative AI to create and tell stories but it is also conceived to be run on cheap hardware (ideally, less than $30). This means that the heavy lifting in terms of computation needs to be done by other devices. This is not ideal but AI models that deliver state-of-the-art quality for speech recognition, story generation and natural speech synthesis are currently way too big to run on small edge devices even when they are available as open weight models.

For that reason, Fably is designed to call out to other computers via the network that offer all the advanced functionality that requires heavy computing.

For now, we only support OpenAI cloud APIs to perform these functions but this is just a starting point as we wish to support a variety of options here, including running your own models on your own hardware in your home under your direct control.

## How good is it? How can I try it out?

In the `example` folder, there are several examples of generated stories along with the synthetized speech. You can listen to them directly here from github or you can run the following command to run use Fably itself to tell the story already generated

```bash
python fably.py --query "Tell me a story about a princess and a frog" --stories-home=./examples/openai_cheap
```

will play the example from `openai_cheap` which uses GPT-3.5 and TTS-1 as the LLM and TTS model respectively. If you change the above to `openai_expensive`, it will play the example from `openai_expensive` which used GPT-4 and TTS-1-HD instead.

## How expensive is this to run?

Assuming a story of 1000 tokens, 4000 characters, it will cost roughly 7 cents with the cheap option (GPT-3.5 + TTS-1) and 17 cents with the most expensive (GPT-4 + TTS-1-HD).

Note that if you just bought an NVIDIA 4090 GPU card at 1599$ (MSRP) and your child listened to 50 stories a day every day it would take you 4 years to spend that much in cloud API costs in the cheap option and 7 months with the most expensive option. And this doesn't even take into account the electricity to power the card and the rest of the hardware you'd need to run it, let alone the cost of your own time maintaining the whole thing.

Also note that we can set spending limits on your OpenAI account so that we don't have to be worried about our children going crazy and spending a fortune in cloud compute without realizing.

## How safe is this?

Giving unsupervised AI to children feels dangerous but Fably does several things to help us
mitigate risks:

* a query guard can be set to prevent queries to run that don't start with a given template. The default template is 'tell me a story about' which significantly constrains the action of the generative model.
* the OpenAI models are censored and aligned, meaning that they follow scrupolous testing and rules for safety.
* the prompt sent to the LLM can be easily configured to further restrict its activity along restriction instructions
that we can control directly.
* each story that gets generated is saved so that it can be inspected later.

## How do I test this out?

Before installing on an edge device, we recommend to try to run Fably from a regular computer first, get it to work with that and test it to make sure that it meets your needs and expectations. You don't need to setup an OpenAI key to do this as we have saved in this repository examples already generated from it.

### Installation

All you need to get started is a computer with:

* python installed
* a speaker

```bash
git clone git@github.com:stefanom/fably.git
cd fably
pip install -r requirements.txt
```

### Listening to examples

In the `example` folder, there are several examples of generated stories along with the synthetized speech. You can listen to them directly here from github or you can run the following command to run use Fably itself to tell the story already generated

```bash
python fably.py --query "Tell me a story about a princess and a frog" --stories-home=./examples/openai_cheap
```

will play the example from `openai_cheap` which uses GPT-3.5 and TTS-1 as the LLM and TTS model respectively. If you change the above to `openai_expensive`, it will play the example from `openai_expensive` which used GPT-4 and TTS-1-HD instead.

### Setting up the OpenAI Key

Go to https://platform.openai.com/api-keys and obtain a new API key.

Then run this command

```bash
cp env.example .env
```

and add your OpenAI key in that file.

### Creating a story

For this, we'll need to have a microphone available to our computer. Once a microphone is available, run this command to create a story and listen to it:

```bash
python fably.py 
```

Say out loud "tell me a story about a dog" and watch the magic happen.

## Troubleshooting

More on this later.

## Installing on a RaspberryPI Zero 2W

We will need:

* a Raspberry Pi Zero 2w
* a mic hat (as the zero doesn't have USB ports)
* a power supply
* a bluetooth speaker (you can also use a google home or similar)

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

# Fably

Use AI to generate and tell bedtime stories to kids.

Run it on your computer or on very cheap (<30$) hardware.

![fably](https://raw.githubusercontent.com/stefanom/fably/main/images/fably.webp)

## How does it work?

Fably uses generative AI to create and tell stories but it is also conceived to be run on cheap hardware (ideally, less than $30). This means that the heavy lifting in terms of computation needs to be done by other devices. This is not ideal but AI models that deliver state-of-the-art quality for speech recognition, story generation and natural speech synthesis are currently way too big to run on edge devices even when the models weight are available.

Fably is designed from the start to call out to other computers via a network. This allows us to run on very cheap devices but have low latency and high quality. Also we have the additional benefit that we can pay-as-we-go and we don't have to invest into expensive GPUs to even see if
our kids will use it or like it.

For now, we only support OpenAI cloud APIs but we wish to support as many options as they are available out there, including running your own models on your own hardware if that's what you prefer.

## Is the experience any good?

You should judge for yourself.

In the `example` folder, there are several examples of generated stories along with the synthetized speech. You can listen to them here or you can run the following command to run use Fably itself to tell the story already generated

```bash
python fably.py --query "Tell me a story about a princess and a frog" --stories-home=./examples/openai_cheap
```

will play the example from `openai_cheap` which uses GPT-3.5 and TTS-1 as the LLM and TTS model respectively.

If you change the above to `openai_expensive` instead, it will play the examples generated using GPT-4 and TTS-1-HD instead.

## How's te latency?

Fably has been designed with latency in mind because kids are not exactly known for their patience. The software has been designed to do as much work concurrently as possible precisely to reduce the time from query to first sound.

Generally, it takes only a couple of seconds from query to first sound, even for the largest models.

## How expensive is this to run?

Assuming a story of 1000 tokens, 4000 characters, it will cost roughly 7 cents with the cheap option (GPT-3.5 + TTS-1) and 17 cents with the most expensive (GPT-4 + TTS-1-HD). A good rule of thumb is that high quality is 3x more expensive than standard quality.

Note that if you just bought an NVIDIA 4090 GPU card at 1599$ (MSRP) and your child listened to 50 stories a day every single day it would take you 4 years to spend that much in cloud API costs in the cheap option and 7 months with the most expensive option. And this doesn't even take into account the electricity to power the card and the rest of the hardware you'd need to run it, let alone the cost of your own time maintaining the whole thing.

Also note that we can set spending limits on your OpenAI account so that we don't have to worry about budget overruns. Although than we have to worry about unhappy kids, but that's another matter entirely.

## Is this safe?

Giving unsupervised AI to children feels dangerous but Fably does several things to help us
mitigate risks:

* a query guard can be set to prevent queries to run that don't start with a given template. The default template is 'tell me a story about' which significantly constrains the action of the generative model.
* large language models "hallucinate" by confidently inventing things that might not be true or exist. But while this "fabulism" tendency is a danger for anyone using these models as oracles, it is a feature when they are used as muses, like in this case.
* the OpenAI models are censored and aligned, meaning that they follow scrupolous testing and rules for safety. As in, they're not going to make you a story about nazis even if the kids ask for it.
* the prompt sent to the LLM can be easily configured to further restrict its activity. If we don't want the LLM to tell stories about particular topics, we can say so and the LLM will oblige. The kids are not going to try to jailbrake it... and if they do successfully, well, they are probably sophisticated enough to deal with the story anyway.
* each story that gets generated is saved so that it can be inspected later. The kids have no way to disable this.

## How do I test this out?

Before installing on an edge device, we recommend to try to run it on your regular personal computer first. It's a lot easier to get it to work there and you can test it and make sure that it meets our needs and expectations.

### Installation

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

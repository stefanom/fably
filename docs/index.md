Use AI to generate and tell bedtime stories to kids.

Run it on a computer or on very cheap (<50$) hardware as a satellite.

<img src="https://raw.githubusercontent.com/stefanom/fably/main/images/fably.webp" alt="Fably" width="500" height="500"/>

Watch Fably running on a Raspberry PI Zero 2W below:

<iframe width="560" height="315" src="https://www.youtube.com/embed/zILPuh84OcY" frameborder="0" allowfullscreen></iframe>

## How does it work?

Fably uses generative AI to create and tell stories but it is also conceived to be run on cheap hardware (ideally, less than $50). This means that the heavy lifting in terms of computation needs to be done by other devices. This is not ideal but AI models that deliver state-of-the-art quality for speech recognition, story generation and natural speech synthesis are currently way too big to run on edge devices even when the models weight are available.

Fably is designed from the start to call out to other computers via a network. This allows us to run on very cheap devices but have low latency and high quality. Also we have the additional benefit that we can pay-as-we-go and we don't have to invest into expensive GPUs to even see if
our kids will use it or like it.

For now, we only support OpenAI cloud APIs but we wish to support as many options as they are available out there, including running our own models on our own hardware that we fully control.

## Is the experience any good?

Judge for yourself!

This is the combined audio generated with GPT-3.5-turbo and the TTS-1 model (the cheapest option) for "Tell me a story about a bull":

<audio controls>
  <source src="https://github.com/stefanom/fably/raw/main/fably/examples/openai_cheap/about_a_bull/story.mp3" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>

and for "tell me a story about a space spider"

<audio controls>
  <source src="https://github.com/stefanom/fably/raw/main/fably/examples/openai_cheap/about_a_space_spider/story.mp3" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>

while this is the combined audio of a story generated with GPT-4 and the TTS-1-HD model (about 3x more expensive per story) for "Tell me a story about a princess and a frog":

<audio controls>
  <source src="https://github.com/stefanom/fably/raw/main/fably/examples/openai_expensive/about_a_princess_and_a_frog/story.mp3" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>

and for "Tell me a story about a planet invated by aliens"

<audio controls>
  <source src="https://github.com/stefanom/fably/raw/main/fably/examples/openai_expensive/about_a_planet_invaded_by_aliens/story.mp3" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>

## What about latency?

Fably has been designed with latency in mind because kids are not exactly known for their patience. The software has been designed to do as much work concurrently as possible precisely to reduce the time from query to first sound.

Generally, it takes only a couple of seconds from query to first sound, even for the more expensive and larger models.

## How expensive is this to run?

Assuming a story of 1000 tokens, 4000 characters, it will cost roughly 7 cents with the cheap option (GPT-3.5 + TTS-1) and 17 cents with the most expensive (GPT-4 + TTS-1-HD). A good rule of thumb is that high quality is 3x more expensive than standard quality.

This sounds like it will get expensive fast, but note that if we just bought an NVIDIA 4090 GPU card at the 1599$ MSRP (and if we can find it at that price!) and our kids listened to 50 stories a day every single day it would take us 4 years to spend that much in cloud API costs in the cheap option and 7 months with the most expensive option. And this doesn't even take into account the electricity to power the card and the rest of the hardware we'd need to run it, let alone the cost of our own time maintaining the whole thing.

Also note that we can set spending limits on our OpenAI account so that we don't have to worry about budget overruns. Although than we have to worry about unhappy kids, but that's another matter entirely.

## Is this safe?

Giving unsupervised AI to children does feels dangerous and scary but Fably does several things to help us mitigate risks:

* a query guard can be set to prevent queries to run that don't match given templates. The default template is that the queries must start with 'tell me a story about'. This significantly constrains how the kids can interact with it.
* large language models "hallucinate" by confidently inventing things that might not be true or exist. But while this "fabulism" can a danger while using these models as oracles or search engines, it is a feature when they are used as muses or entertainers, like in our case.
* the OpenAI models are censored and aligned, meaning that they follow scrupolous testing and rules for safety. As in, they're not going to make up a story with nazis even if the kids were somehow asking for it or the model misheard their voice query that way.
* the prompt sent to the LLM can be easily configured to further restrict its activity. If we don't want the LLM to tell stories about particular topics, we can tell it so and the LLM will oblige. And if our kids find a way to around that, well, they are probably sophisticated enough to deal with whatever story Fably came up with anyway.
* each story that gets generated is saved so that it can be inspected later.

## How do I test this out?

Before installing on an edge device, we recommend to try to run it on a regular personal computer first. It's a lot easier to get it to work there and we can test it and make sure that it meets our needs and expectations.

Follow the instructions [here](https://github.com/stefanom/fably)

## References

Here's a list of [interesting pointers and other projects](references.md) that Fably depends or may depend on in the future.

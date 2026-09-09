# Development log of piPokedex

## 2026.09.07 - Start of project
I haven't done any side projects in a while. I was and still am stuck doing tedious tasks in my projects
that revolve around data collection or CRUD-style applications. I wanted to learn something new that would teach
me new things I haven't done yet and start implementing it on my own.

I chose to do a Pokédex since I recently started playing the trading card game. Since I'm mostly
familiar with the first generation of Pokémon I have a hard time understanding what the new card do.
I can use this device to help me become a pokémon master, just like Ash in his voyage.

Today I started with breaking up what I want this project to achieve, the MVP if you will. Here's the breakdown:
1. Read video feed from camera and detect the pokémon card in it
2. Read text of the card image
3. Search a pokémon entry from a pokémon DB
4. Display image of pokémon
5. Read the flavor text from the Pokédex with TTS using a custom voice matching the polish Pokédex VA


Based on those tasks I know what I wanted to achieve. So I started with some POC for all the requirements.

### POC - Read from Camera
I had no idea how to do image processing, so I used claude to come up with a way. The initial setup consists of
OpenCV to get the image displayed from my camera and tried to detect a 4 point rectangle in the feed. This wasn't working.

I quickly changed it to have a area in the camera where we need to position the card to make it detect the rectangle.
This fixed a lot of the issues, as the tracking worked better in a closed area, the autofocus would have a easier job 
because the card needs to match the dimensions of the area. In the end I was able to get the card image from the bigger camera.

![Screenshot 2026-09-07 174448.png](static/img/Screenshot%202026-09-07%20174448.png)

With this I should be able now to use the image for further processing.

## 2026.09.08 - Playing with text-to-speech
So I started playing around with the `piper` text to speech module today, and I'm astonished how easy it is to set it up.
Just in under 10 minutes I had a working demo that would read out the text using a existing polish voice model.

Here's the .wav file I generated from the first line. Try to guess what Pokémon the TTS is trying to pronounce in polish:

<audio controls>
  <source src="static/audio/tts-first_test.wav" type="audio/wav">
  Your browser does not support the audio element.
</audio>

Fallback link if the player doesn't render: [tts-first_test.wav](static/audio/tts-first_test.wav)

So with this proof of concept I noticed a few outliers:

- There is a delay between starting the synthesizing and obtaining the audio file
  > This should be fine as even in the anime there was a cue sound before the pokedex would read the entry

- The polish voice model has difficulties pronouncing the pokemon name. 
  > Charizard hard to be spelled out like 'Cha Ri Zard' for the system to make it understanable. We can make it work by using generated phonomes
  > 

### Piper's phonemizer steps
Piper uses phonemes (i.e. smallest unit of sound in speech) by breaking down the sentence and then generating sounds for the sequences of phonemes.
This means that we can combine phenomes that would be used to pronounce a word in a given language and combine them with phonemes of another language, meaning - 
**Speak the Pokémon name in English, then read out the rest in Polish**.
and the sounds can then be displayed. So the appraoch would be like this:
1. Construct sentence where we provide which word should be pronounced in a different language (e.g Charizard)
2. Construct the phonemes for the specified word.
3. Construct the phonemes for the whole sentence.
4. Replace the phonemes of given word in the generated sentence's phonemes.
5. Synthesize using the phonemes.

With this I started a 2nd POC to have it worked out. This gave me the 2nd result:

<audio controls>
  <source src="static/audio/tts-second_test.wav" type="audio/wav">
  Your browser does not support the audio element.
</audio>

Fallback link if the player doesn't render: [tts-second_test.wav](static/audio/tts-second_test.wav)

So yeah, this failed miserable as the polish synthesizer voice had problem reading it. It's not making it better.

### Simple approach
So I'm thinking about a 3rd attempt - Since in the anime the name of the Pokémon is only read out once, let's use a english voice for the name,
then read the flavor text in Polish. With this I would get 2 audio files that can be played one after another. The effect of this you can imagine.

For now this will be the approach I take and continue structuring the project around. Maybe with some more research I can combine the phonemes as planed?




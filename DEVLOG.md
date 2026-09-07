# Development log of piPokedex

## 2026.09.07 - Start of project
I haven't done any side projects in a while. I was and still am stuck doing tedious tasks in my projects
that revolve around data collection or CRUD-style applications. I wanted to learn something new that would teach
me new things I haven't done yet and start implementing it on my own.

I chose to do a pokedex since I recently started playing the trading card game. Since I'm mostly
familiar with the first generation of pokemon I have a hard time understanding what the new card do.
I can use this device to help me become a pokemon master, just like Ash in his voyage.

Today I started with breaking up what I want this project to achieve, the MVP if you will. Here's the breakdown:
1. Read video feed from camera and detect the pokemon card in it
2. Read text of the card image
3. Search a pokemon entry from a Pokemon DB
4. Display image of pokemon
5. Read the flavor text from the pokedex with TTS using a custom voice matching the polish Pokedex VA


Based on those tasks I know what I wanted to achieve. So I started with some POC for all of the requirements.

### POC - Read from Camera
I had no idea how to do image processing so I used claude to compe up with a way. The initial setup consists of
OpenCV to get the image displayed from my camera and tried to detect a 4 point rectangle in the feed. This wasn't working.

I quickly changed it to have a area in the camera where we need to position the card to make it detect the rectangle.
This fixed a lot of the issues, as the tracking worked better in a closed area, the autofocus would have a easier job 
because the card needs to match the dimensions of the area. In the end I was able to get the card image from the bigger camera.

![Screenshot 2026-09-07 174448.png](static/Screenshot%202026-09-07%20174448.png)

With this I should be able now to use the image for further processing.

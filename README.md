# Flappy Taco

Its Flappy Bird... with a tasty twist... <br>
_Built on Python using the PyGame module._

## How to Install Correctly
Go to the _Releases_ Page and download the .exe file in the latest release. <br>
_(Don't download the source code)_

## How to Play
- `[LEFT MOUSE BUTTON]` to jump upwards
- Jump through the Forks to progress
- Collect Chillies to refuel your Energy
- Choose which taco you play as from the menu

Most importantly - have fun!

## Game Saves
Where is the game save data stored? Flappy Taco stores all progress data at `%appdata%/08BitPixels/Flappy Taco/saves/`.

## Configuration
_* All of this info is also in the config text file_ <br>
Using config.txt (located at `%appdata%/08BitPixels/Flappy Taco/config/`), you can configure;

### Screen Settings
- Screen **Width** / **Height**
- **FPS** (Enter `0` to uncap the FPS, or you can specify a custom value)
- **VSync** (`0 = off, 1 = on`; syncs refresh rate to that of the monitor (can help to reduce screen tearing) - when this is set to 1 (on) FPS value is ignored.)
  - EXPERIMENTAL FEATURE - due to the specific requirements of VSync, it may not work; you are not garanteed to get a VSync window on your specific setup.
  - Due to this, it is reccomended that you set the FPS value to the refresh rate of your monitor anyways.
  - You will know if VSync has not worked if your FPS seems to be uncapped, even though you have set VSync to be on - in this case, just disable VSync and use the FPS value as normal.
  - ALSO if VSync is on, you will not be able to change the large-ness of the window, but you can still change the ratio (for an annoying reason)

### Audio
- Music + SFX Volume (A float between 0-1 `(0 = off, 1 = max)`)

## Credits
Thanks to ClearCode (https://www.youtube.com/@ClearCode) for teaching me how to use Pygame. He does loads of awesome Python and Pygame tutorials so if you want to learn how to use Pygame, I highly reccomend checking him out.

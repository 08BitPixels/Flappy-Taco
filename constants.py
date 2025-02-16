import sys
import os

def save_path(relative_path: str) -> str:

	if getattr(sys, 'frozen', False): return os.path.join(os.getenv('APPDATA', ''), '08BitPixels/Flappy Taco/', relative_path)
	else: return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def save_config(settings: dict[str, int | float]) -> None:
		
		'''
		'SCREEN_WIDTH': int | str,
		'SCREEN_HEIGHT': int | str,
		'FPS': int,
		'VSYNC': int,

		'MUSIC_VOL': float | int,
		'SFX_VOL': float | int
		'''

		print('\nSaving Config...')
		with open(save_path('saves\\config.txt'), 'w') as config: 
			
			config.write(

f'''# CONFIG

## Screen Setup ----
{'\n'.join([f'{setting} = {data}' for setting, data in list(settings.items())[:4]])}

## Audio ----
{'\n'.join([f'{setting} = {data}' for setting, data in list(settings.items())[4:]])}

----------------------------------------------------
# CONFIG EXPLAINED

## Screen Setup ----
FPS: number (0 = uncapped)
VSYNC: 0 = off, 1 = on; syncs refresh rate to that of the monitor (can help to reduce screen tearing) - when this is set to 1 (on) FPS value is ignored. 
| EXPERIMENTAL FEATURE - due to the specific requirements of VSync, it may not work; you are not garanteed to get a VSync display on your specific setup.
| Due to this, it is reccomended that you set the FPS value to the refresh rate of your monitor anyways.
| You will know if VSync has not worked if your FPS seems to be uncapped, even though you have set VSync to be on - in this case, just disable VSync and use the FPS value as normal.
| ALSO if VSync is on, you will not be able to change the large-ness of the window, but you can still change the ratio (for an annoying reason)

## Audio ----
MUSIC & SFX VOL: float between 0-1 (0 = off, 1 = max)'''

			)

		print('Saved\n')

def load_config() -> dict:

	if os.path.isfile(save_path('saves\\config.txt')):

		with open(save_path('saves\\config.txt'), 'r') as config_file: 

			config = {}
			contents = config_file.readlines()

			for line in contents[3:7] + contents[9:11]:

				setting = line.split(' = ')[0].strip('\n')
				data = line.split(' = ')[1].strip('\n')
				config[setting] = int(data) if data.isnumeric() else float(data)
		
			return config

	else:

		print('\nNo config file present; creating new one...')
		if not os.path.isdir(save_path('saves\\')): os.makedirs(save_path('saves\\'))
		save_config(settings = DEFAULT_CONFIG)
		return DEFAULT_CONFIG

def splashscreen_size(img_size: tuple[int | float, int | float], screen_size: tuple[int, int]) -> tuple[float, float]:

	if img_size[0] > screen_size[0]: img_size = (screen_size[0], (screen_size[0] / img_size[0]) * img_size[1])
	if img_size[1] > screen_size[1]: img_size = ((screen_size[1] / img_size[1]) * img_size[0], screen_size[1]) 

	return img_size

# Default Settings
DEFAULT_CONFIG = {

	'SCREEN_WIDTH': 1000,
	'SCREEN_HEIGHT': 750,
	'FPS': 60,
	'VSYNC': 0,

	'MUSIC_VOL': 1.0,
	'SFX_VOL': 1.0

}

config = load_config()

# Screen Setup
WIDTH, HEIGHT = config['SCREEN_WIDTH'], config['SCREEN_HEIGHT']
FPS = config['FPS']
VSYNC = config['VSYNC']

CENTRE_X = WIDTH / 2
CENTRE_Y = HEIGHT / 2

# Audio
MUSIC_VOL = config['MUSIC_VOL']
SFX_VOL = config['MUSIC_VOL']

# COLOURS
YELLOW = '#ffd500'
LIGHT_YELLOW = '#fff700'
LIGHT_GREY = '#d4d4d4'
WHITE = '#ffffff'
BLACK = '#000000'
RED = '#ff0000'
GREEN = '#0ac900'
import sys
import os

def save_path(relative_path: str) -> str:

    if getattr(sys, 'frozen', False): return os.path.join(os.getenv('APPDATA'), '08BitPixels/Flappy Taco/', relative_path)
    else: return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def save_config(
		
		  	settings: dict[
				  
				'SCREEN_WIDTH': int | str,
				'SCREEN_HEIGHT': int | str,
				'FPS': int,

				'MUSIC_VOL': float | int,
				'SFX_VOL': float | int

			]
			
		) -> None:

		print('\nSaving Config...')
		with open(save_path('saves\\config.txt'), 'w') as config: 
			
			config.write(

f'''# CONFIG

## Screen Setup ----
{'\n'.join([f'{setting} = {data}' for setting, data in list(settings.items())[:3]])}

## Audio ----
{'\n'.join([f'{setting} = {data}' for setting, data in list(settings.items())[3:]])}

----------------------------------------------------
# CONFIG EXPLAINED

## Screen Setup ----
FPS: number (0 = uncapped)

## Audio ----
MUSIC & SFX VOL: float between 0-1 (0 = off, 1 = max)'''

			)

		print('Saved\n')

def load_config() -> dict:

	if os.path.isfile(save_path('saves\\config.txt')):

		with open(save_path('saves\\config.txt'), 'r') as config_file: 

			config = {}
			contents = config_file.readlines()

			for line in contents[3:6] + contents[8:10]:

				setting = line.split(' = ')[0].strip('\n')
				data = line.split(' = ')[1].strip('\n')
				config[setting] = int(data) if data.isnumeric() else float(data)
		
			return config

	else:

		print('\nNo config file present; creating new one...')
		if not os.path.isdir(save_path('saves\\')): os.makedirs(save_path('saves\\'))
		save_config(settings = DEFAULT_CONFIG)
		return DEFAULT_CONFIG

def splashscreen_size(img_size: tuple[int, int], screen_size: tuple[int, int]) -> tuple[int, int]:

	if img_size[0] > screen_size[0]: img_size = (screen_size[0], (screen_size[0] / img_size[0]) * img_size[1])
	if img_size[1] > screen_size[1]: img_size = ((screen_size[1] / img_size[1]) * img_size[0], screen_size[1]) 

	return img_size

# Default Settings
DEFAULT_CONFIG = {

	'SCREEN_WIDTH': 1080,
	'SCREEN_HEIGHT': 720,
	'FPS': 60,

	'MUSIC_VOL': 1.0,
	'SFX_VOL': 1.0

}

config = load_config()

# Screen Setup
WIDTH, HEIGHT = config['SCREEN_WIDTH'], config['SCREEN_HEIGHT']
FPS = config['FPS']

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
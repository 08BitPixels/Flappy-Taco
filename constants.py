import os
import toml
import ctypes
from textwrap import dedent

def splashscreen_size(img_size: tuple[int | float, int | float], screen_size: tuple[int, int]) -> tuple[float, float]:

	if img_size[0] > screen_size[0]: img_size = (screen_size[0], (screen_size[0] / img_size[0]) * img_size[1])
	if img_size[1] > screen_size[1]: img_size = ((screen_size[1] / img_size[1]) * img_size[0], screen_size[1]) 

	return img_size

class FileHandler:

	def __init__(self) -> None:

		self.base_path = os.path.dirname(os.path.abspath(__file__))
		self.save_dir_name = 'save_data\\'
		self.config_file_name = 'config.toml'
		self.user_data_file_name = 'user_data.toml'

		self.config_path = self.save_path(self.config_file_name)
		self.user_data_path =self.save_path(self.user_data_file_name)

		self.DEFAULT_CONFIG: dict[str, dict[str, int | float]] = {
			'screen_setup': {
				'width': 1000,
				'height': 750,
				'FPS': 60,
				'VSYNC': 0
			},
			'audio_volume': {
				'music': 1.0,
				'sfx': 1.0
			}
		}
		self.config: dict[str, dict[str, int | float]] = {}
		self.user_data: dict[str, int] = {}

		if not os.path.isdir(self.save_path()): os.makedirs(self.save_path())
		check_path = os.path.join(os.getenv('APPDATA', ''), '08BitPixels\\')
		self.to_remove: list[str] = []
		self.clear_dir(path = check_path)
		if self.to_remove: self.remove_dir(path = self.to_remove[-1])

		self.load_config()
		self.load_user_data()

	def save_path(self, relative_path: str = '') -> str:
		return os.path.join(self.base_path, self.save_dir_name, relative_path)

	def remove_dir(self, path: str) -> None:

		try:
			os.remove(path = path)

		except PermissionError:

			message = dedent(
				f'''\
				Depreciated program directory found: 
				"{path}"

				This is due to a change in saving mechanics - your save files have been moved automatically to:
				"{self.save_path('')}"

				Feel free to remove this old directory as its use is now depreciated! \
				'''
			)
			ctypes.windll.user32.MessageBoxW(0, message, 'Depreciated Directory Found', 0 | 0x40)

	def clear_dir(self, path: str) -> None:

		print(f'\nchecking: {path}')

		if os.path.isdir(path):

			print('| dir exists')
			dir_contents = os.listdir(path)

			if dir_contents:

				print('| dir is not empty; contents:')
				print(f'| {dir_contents}')

				if 'Flappy Taco' in dir_contents or 'saves' in dir_contents:

					present = ('Flappy Taco', 'saves')['saves' in dir_contents]
					self.clear_dir(path = os.path.join(path, present))
					dir_contents.remove(present)
					if not dir_contents: self.to_remove.append(path)

				else:
					
					if 'config.txt' in dir_contents:
						
						self.load_old_config(path = os.path.join(path, 'config.txt'))
						os.remove(os.path.join(path, 'config.txt'))
					
					if 'saves.txt' in dir_contents: 
						
						self.load_old_user_data(path = os.path.join(path, 'saves.txt'))
						os.remove(os.path.join(path, 'saves.txt'))

			else:

				print('| dir is empty')
				self.to_remove.append(path)

		else:

			print('| dir does not exist; skipping')

	def save_data(self, mode: int, data: dict[str, dict[str, int | float]] | dict[str, int]) -> None:

		match mode:

			case 0:
			
				'''
				{
					'screen_setup': {
						'width': int,
						'height': int,
						'FPS': int,
						'VSYNC': int; 0 / 1
					},
					'audio_volume': {
						'music': float; 0-1,
						'sfx': float; 0-1
					}
				}

				'''

				comments = dedent(
					'''
					# [CONFIG EXPLAINED]

					# [screen setup]
					# width & height: integers; the dimensions of the game window in pixels
					# FPS: integer (-1 = uncapped)
					# VSYNC: 0 = off, 1 = on; syncs refresh rate to that of the monitor (can help to reduce screen tearing) - when this is set to 1 (on) FPS value is ignored. 
					# | EXPERIMENTAL FEATURE - due to the specific requirements of VSync, it may not work; you are not garanteed to get a VSync display on your specific setup.
					# | Due to this, it is reccomended that you set the FPS value to the refresh rate of your monitor anyways.
					# | You will know if VSync has not worked if your FPS seems to be uncapped, even though you have set VSync to be on - in this case, just disable VSync and use the FPS value as normal.
					# | ALSO if VSync is on, you will not be able to change the scale of the window, but you can still change the ratio (for an annoying reason)

					# [audio volume]
					# music & sfx: float, between 0-1 (0 = mute, 1 = max) \
					'''
				)

				print('\nSaving Config...')

				text = toml.dumps(data) + comments
				path = self.config_path

			case 1:

				print('\nSaving User Data...')

				text = toml.dumps(data)
				path = self.user_data_path

		file = open(path, 'w') 
		file.write(text)
		file.close()

		print('Saved')

	def load_config(self) -> None:

		print('\nloading config...')

		if os.path.isfile(self.config_path):

			file = open(self.config_path, 'r')
			self.config = toml.load(file)
			file.close()

		else:

			print('\nNo config file present; creating new one...')
			self.config = self.DEFAULT_CONFIG
			self.save_data(mode = 0, data = self.config)
		
		print('config loaded')

	def load_user_data(self) -> None:

		print('\nloading user data...')

		if os.path.isfile(self.user_data_path):

			file = open(self.user_data_path, 'r') 
			self.user_data = toml.load(file)
			file.close()

		else:

			print('No user data file present; creating new one...')
			self.user_data = {'highscore': 0, 'costume_index': 0}
			self.save_data(mode = 1, data = self.user_data)

		print('user data loaded')
	
	def load_old_config(self, path: str) -> None:

		print('\nold config file detected; upgrading to new format...')

		old_config = {}

		file = open(path, 'r')
		contents = file.readlines()
		file.close()

		for line in contents[3:7] + contents[9:11]:

			setting = line.split(' = ')[0].strip('\n')
			data = line.split(' = ')[1].strip('\n')
			old_config[setting] = int(data) if data.isnumeric() else float(data)
	
		self.config = {
			'screen_setup': {
				'width': old_config['SCREEN_WIDTH'],
				'height': old_config['SCREEN_HEIGHT'],
				'FPS': old_config['FPS'],
				'VSYNC': old_config['VSYNC']
			},
			'audio_volume': {
				'music': old_config['MUSIC_VOL'],
				'sfx': old_config['SFX_VOL']
			}
		}
		self.save_data(mode = 0, data = self.config)

	def load_old_user_data(self, path: str) -> None:

		print('\nold user data file detected; upgrading to new format...')

		file = open(self.save_path(path), 'r')
		contents = file.readlines()
		file.close()

		high_score = int(contents[0].split('=')[1].strip('\n'))
		costume_index = int(contents[1].split('=')[1].strip('\n'))

		self.user_data = {
			'highscore': high_score,
			'costume_index': costume_index
		}
		self.save_data(mode = 1, data = self.user_data)

file_handler = FileHandler()
config = file_handler.config

# Screen Setup
WIDTH, HEIGHT = int(config['screen_setup']['width']), int(config['screen_setup']['height'])
FPS = config['screen_setup']['FPS']
VSYNC = int(config['screen_setup']['VSYNC'])

CENTRE_X = int(WIDTH // 2)
CENTRE_Y = int(HEIGHT // 2)

# Audio
MUSIC_VOL = config['audio_volume']['music']
SFX_VOL = config['audio_volume']['sfx']

# COLOURS
YELLOW = '#ffd500'
LIGHT_YELLOW = '#fff700'
LIGHT_GREY = '#d4d4d4'
WHITE = '#ffffff'
BLACK = '#000000'
RED = '#ff0000'
GREEN = '#0ac900'
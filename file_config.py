import os
import toml
import ctypes
from textwrap import dedent
from typing import TypedDict, Literal, get_type_hints

from assets import EXE, WORKING_DIR, SAVE_DIR, CONFIG_PATH, USER_DATA_PATH
import logs

logger = logs.get_logger(file = __file__) # get logger

def validate_typeddict(data: dict, typed_dict: type, ranges: dict = {}) -> None:

	type_hints = get_type_hints(typed_dict)

	for key, expected_type in type_hints.items():

		if hasattr(expected_type, '__bases__') and expected_type.__bases__[0] is dict: 
			validate_typeddict(data = data[key], typed_dict = expected_type, ranges = ranges[key])

		else:

			if key not in data:
				raise KeyError(f'Missing key for type {typed_dict}: {key}')
			
			if expected_type is Literal[0, 1] or expected_type is Literal[0, 1, 2, 3, 4, 5, 6, 7]:
				expected_type = int
			
			if expected_type is float:
				if type(data[key]) is int:
					data[key] = float(data[key])

			if type(data[key]) is not expected_type:
				raise TypeError(f'invalid config value [{data[key]}], for key "{key}"; expected type {expected_type}, got type {type(data[key])}')
		
			if ranges and key in ranges:
				if len(ranges[key]) == 1: min, max = ranges[key][0], None
				else: min, max = ranges[key]
				if min > data[key] or (max and data[key] > max):
					raise ValueError(f'invalid config value [{data[key]}], for key "{key}"; expected range {min} <= value <= {max}')

class ScreenSetupDict(TypedDict):
		
	width: int
	height: int
	FPS: int
	VSYNC: Literal[0, 1]

class VolumeDict(TypedDict):

	music: float
	sfx: float

class ColoursDict(TypedDict):

	black: str | tuple[int, int, int]
	light_grey: str | tuple[int, int, int]
	white: str | tuple[int, int, int]
	red: str | tuple[int, int, int]
	green: str | tuple[int, int, int]
	yellow: str | tuple[int, int, int]
	light_yellow: str | tuple[int, int, int]

class ConfigDict(TypedDict):

	screen_setup: ScreenSetupDict
	audio_volume: VolumeDict

class OldConfigDict(TypedDict):

	SCREEN_WIDTH: int
	SCREEN_HEIGHT: int
	FPS: int
	VSYNC: Literal[0, 1]
	MUSIC_VOL: float
	SFX_VOL: float

class UserDataDict(TypedDict):

	high_score: int
	costume_index: Literal[0, 1, 2, 3, 4, 5, 6, 7]

class ConstantsDict(TypedDict):

	screen_dimensions: tuple[int, int]
	centre_coords: tuple[int, int]
	FPS: int
	VSYNC: Literal[0, 1]
	volumes: VolumeDict
	colours: ColoursDict

# File Handler Object
class FileHandler:

	def __init__(self) -> None:

		self._DEFAULT_CONFIG: ConfigDict = {
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

		if not EXE and not os.path.isdir(SAVE_DIR): os.makedirs(SAVE_DIR)
		check_path = os.path.join(os.getenv('APPDATA', ''), '08BitPixels\\')
		to_remove = self._clear_dir(path = check_path)
		if to_remove: self._remove_dir(path = to_remove[-1])

	def save_data(self, mode: int, data: ConfigDict | UserDataDict) -> None:

		match mode:

			case 0:

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
				path = CONFIG_PATH

			case 1:

				print('\nSaving User Data...')

				text = toml.dumps(data)
				path = USER_DATA_PATH

		file = open(path, 'w') 
		file.write(text)
		file.close()

		print('Saved')

	def load_config(self) -> ConfigDict:

		print('\nloading config...')
		config: ConfigDict = self._DEFAULT_CONFIG

		if os.path.isfile(CONFIG_PATH):

			file = open(CONFIG_PATH, 'r')
			config = toml.load(file)
			file.close()

			validate_typeddict(
				data = dict(config),
				typed_dict = ConfigDict,
				ranges = {
					'screen_setup': {
						'FPS': [-1],
						'VSYNC': (0, 1),
					},
					'audio_volume': {
						'music': (0.0, 1.0),
						'sfx': (0.0, 1.0)
					}
				}
			)

		else:

			print('\nNo config file present; creating new one...')
			self.save_data(mode = 0, data = config)
		
		print('config loaded')
		return config

	def load_user_data(self) -> UserDataDict:

		print('\nloading user data...')
		user_data: UserDataDict = {'high_score': 0, 'costume_index': 0}

		if os.path.isfile(USER_DATA_PATH):

			file = open(USER_DATA_PATH, 'r') 
			user_data = toml.load(file)
			file.close()
			validate_typeddict(
				data = dict(user_data),
				typed_dict = UserDataDict,
				ranges = {
					'high_score': [0],
					'costume_index': (0, 7)
				}
			)

		else:

			print('No user data file present; creating new one...')
			self.save_data(mode = 1, data = user_data)

		print('user data loaded')
		return user_data

	def _remove_dir(self, path: str) -> None:

		try:
			os.remove(path = path)

		except PermissionError:

			message = dedent(
				f'''\
				Depreciated program directory found: 
				"{path}"

				This is due to a change in saving mechanics - your save files have been moved automatically to:
				"{WORKING_DIR}"

				Feel free to remove this old directory as its use is now depreciated! \
				'''
			)
			ctypes.windll.user32.MessageBoxW(0, message, 'Depreciated Directory Found', 0 | 0x40)

	def _clear_dir(self, path: str, to_remove: list[str] = []) -> list[str]:

		print(f'\nchecking: {path}')

		if os.path.isdir(path):

			print('| dir exists')
			dir_contents = os.listdir(path)

			if dir_contents:

				print('| dir is not empty; contents:')
				print(f'| {dir_contents}')

				if 'Flappy Taco' in dir_contents or 'saves' in dir_contents:

					present = ('Flappy Taco', 'saves')['saves' in dir_contents]
					to_remove = self._clear_dir(path = os.path.join(path, present), to_remove = to_remove)
					dir_contents.remove(present)
					if not dir_contents: to_remove.append(path)

				elif 'config.txt' in dir_contents or 'saves.txt' in dir_contents:
					
					if 'config.txt' in dir_contents:
						
						config = self._load_old_config(path = os.path.join(path, 'config.txt'))
						self.save_data(mode = 0, data = config)
						os.remove(os.path.join(path, 'config.txt'))
					
					if 'saves.txt' in dir_contents: 
						
						user_data = self._load_old_user_data(path = os.path.join(path, 'saves.txt'))
						self.save_data(mode = 1, data = user_data)
						os.remove(os.path.join(path, 'saves.txt'))
					
				else:
					print('dir does not contain old Flappy Taco directories; skipping...')

			else:

				print('| dir is empty; removing...')
				to_remove.append(path)

		else:

			print('| dir does not exist; skipping')

		return to_remove
	
	def _load_old_config(self, path: str) -> ConfigDict:

		print('\nold config file detected; upgrading to new format...')

		old_config: OldConfigDict = {
			'SCREEN_WIDTH': 0,
			'SCREEN_HEIGHT': 0,
			'FPS': 0,
			'VSYNC': 0,
			'MUSIC_VOL': 0.0,
			'SFX_VOL': 0.0
		}

		file = open(path, 'r')
		contents = file.readlines()
		file.close()

		for index, line in enumerate(contents[3:7] + contents[9:11]):

			key = line.split(' = ')[0].strip('\n')
			value = line.split(' = ')[1].strip('\n')

			match key:

				case 'SCREEN_WIDTH': 
					if value.isdecimal(): 
						old_config['SCREEN_WIDTH'] = int(value)
					else: 
						raise ValueError(f'invalid config value "{value}" for key "{key}" of config file {path}; must be type {type(old_config[key])}')

				case 'SCREEN_HEIGHT': 
					if value.isdecimal(): 
						old_config['SCREEN_HEIGHT'] = int(value)
					else: 
						raise ValueError(f'invalid config value "{value}" for key "{key}" of config file {path}; must be type {type(old_config[key])}')

				case 'FPS': 
					if value.isdecimal() and -1 <= int(value): 
						old_config['FPS'] = int(value)
					else: 
						raise ValueError(f'invalid config value "{value}" for key "{key}" of config file {path}; must be type {type(old_config[key])}: must be larger than -1')

				case 'VSYNC': 
					if value.isdecimal() and int(value) in (0, 1): 
						old_config['VSYNC'] = (0, 1)[int(value)]
					else: 
						raise ValueError(f'invalid config value "{value}" for key "{key}" of config file {path}; must be type {type(old_config[key])}: must be either 0 or 1')

				case 'MUSIC_VOL': 
					if value.replace('.', '').isdecimal() and 0.0 <= float(value) <= 1.0: 
						old_config['MUSIC_VOL'] = float(value)
					else: 
						raise ValueError(f'invalid config value "{value}" for key "{key}" of config file {path}; must be type {type(old_config[key])}: must be between 0 and 1')

				case 'SFX_VOL': 
					if value.replace('.', '').isdecimal() and 0.0 <= float(value) <= 1.0: 
						old_config['SFX_VOL'] = float(value)
					else: 
						raise ValueError(f'invalid config value "{value}" for key "{key}" of config file {path}; must be type {type(old_config[key])}: must be between 0 and 1')

				case _:
					raise ValueError(f'invalid config key "{key}" on line {index} of config file {path}; must be one of {old_config.keys()}')
	
		config: ConfigDict = {
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
		
		return config

	def _load_old_user_data(self, path: str) -> UserDataDict:

		print('\nold user data file detected; upgrading to new format...')
		user_data: UserDataDict = {'high_score': 0, 'costume_index': 0}

		file = open(path, 'r')
		contents = file.readlines()
		file.close()

		high_score = contents[0].split('=')[1].strip('\n')
		costume_index = contents[1].split('=')[1].strip('\n')

		if high_score.isdigit(): 
			user_data['high_score'] = int(high_score)
		else: 
			raise ValueError(f'key "high_score" of user data file file "{path}" must be type: {type(user_data['high_score'])}')
		
		if costume_index.isdigit() and int(costume_index) in (0, 1, 2, 3, 4, 5, 6, 7): 
			user_data['costume_index'] = (0, 1, 2, 3, 4, 5, 6, 7)[int(costume_index)]
		else: 
			raise ValueError(f'key "high_score" of user data file file "{path}" must be type: {type(user_data['high_score'])}')

		return user_data

def init() -> tuple[FileHandler, ConstantsDict, UserDataDict]:

	file_handler = FileHandler()
	config = file_handler.load_config()
	user_data = file_handler.load_user_data()

	# Screen Setup
	WIDTH, HEIGHT = config['screen_setup']['width'], config['screen_setup']['height']
	CENTRE_X = WIDTH // 2
	CENTRE_Y = HEIGHT // 2

	FPS = config['screen_setup']['FPS']
	VSYNC = config['screen_setup']['VSYNC']

	# Audio
	VOLUMES: VolumeDict = config['audio_volume']

	# COLOURS
	COLOURS: ColoursDict = {
		'black': '#000000',
		'light_grey': '#d4d4d4',
		'white': '#ffffff',
		'red': '#ff0000',
		'green': '#0ac900',
		'yellow': '#ffd500',
		'light_yellow': '#fff700'
	}

	constants: ConstantsDict = {
		'screen_dimensions': (WIDTH, HEIGHT),
		'centre_coords': (CENTRE_X, CENTRE_Y),
		'FPS': FPS,
		'VSYNC': VSYNC,
		'volumes': VOLUMES,
		'colours': COLOURS
	}

	return file_handler, constants, user_data

if __name__ == '__main__': init()
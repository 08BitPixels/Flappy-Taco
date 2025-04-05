import os
import sys
import ctypes

# runtime info
EXE = bool(getattr(sys, '_MEIPASS', False)) # is program being run from exe

# version info
CURRENT_VERSION = 'v1.2.0'
API_URL = 'https://api.github.com/repos/08BitPixels/Flappy-Taco/releases/latest'

# environment paths
WORKING_DIR = os.path.dirname(__file__) # exe: _internal
FILE_NAMES = {
	'config': 'config.toml',
	'user_data': 'user_data.toml',
}
# save data
SAVE_DIR = '' if EXE else os.path.join(WORKING_DIR, 'save_data\\')
CONFIG_PATH = os.path.join(WORKING_DIR, '..' if EXE else SAVE_DIR, FILE_NAMES['config'])
USER_DATA_PATH = os.path.join(WORKING_DIR, '' if EXE else SAVE_DIR, FILE_NAMES['user_data'])
# logs
LOGS_DIR = os.path.join(WORKING_DIR, '..' if EXE else '', 'logs\\')

def save_path(relative_path: str) -> str:
	return os.path.join(WORKING_DIR, relative_path)

def resource_path(relative_path: str) -> str:

	if EXE: 
		path = os.path.join('_internal', relative_path)
	else: 
		path = relative_path

	return path

def popup_window(title: str, description: str, perams: int) -> int: # -> response

	'''
	WINDOW CODES

	MessageBoxW(
		hWnd,      | owner window
		lpText,    | description
		lpCaption, | title
		uType      | icon & buttons perameters (seperate codes with '|' operator)
	)

	Buttons
	0 | OK
	1 | OK, Cancel
	2 | Abort, Retry, Ignore
	3 | Yes, No, Cancel
	4 | Yes, No
	5 | Retry, Cancel
	6 | Cancel, Try Again, Continue

	Icons
	0x10 | Stop
	0x20 | Question
	0x30 | Warning
	0x40 | Info

	Return Value - which button was pressed
	1  | Ok
	2  | Cancel
	3  | Abort
	4  | Retry
	5  | Ignore
	6  | Yes
	7  | No
	10 | Try Again
	11 | Continue
	'''

	response = ctypes.windll.user32.MessageBoxW(
		0, 
		description, 
		title, 
		perams
	)
	return response

def splashscreen_size(img_size: tuple[int | float, int | float], screen_size: tuple[int, int]) -> tuple[float, float]:

	if img_size[0] > screen_size[0]: img_size = (screen_size[0], (screen_size[0] / img_size[0]) * img_size[1])
	if img_size[1] > screen_size[1]: img_size = ((screen_size[1] / img_size[1]) * img_size[0], screen_size[1]) 

	return img_size
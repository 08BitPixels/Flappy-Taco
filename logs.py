import logging
import datetime
import os
import sys

LOG_FORMAT = '[%(asctime)s] [%(name)s/ %(funcName)s] [%(levelname)s]: %(message)s'
TIME_FORMAT = '%H:%M:%S'
TODAY = datetime.date.today().strftime('%d-%m-%y')
data: dict[str, int | str] = {}
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def save_path(relative_path: str) -> str:

	if getattr(sys, '_MEIPASS', False):
		path = os.path.join(BASE_PATH, '..', relative_path)
	
	else:
		path = os.path.join(BASE_PATH, relative_path)

	return path

DIR_PATH = save_path(os.path.join('logs', TODAY))
os.makedirs(DIR_PATH, exist_ok = True)
runs = len(os.listdir(DIR_PATH)) + 1
FILE_PATH = os.path.join(DIR_PATH, f'{runs}.log')

FORMATTER = logging.Formatter(
	fmt = LOG_FORMAT,
	datefmt = TIME_FORMAT
)

logging.basicConfig(

	filename = FILE_PATH, 
	format = LOG_FORMAT, 
	datefmt = TIME_FORMAT,
	level = logging.CRITICAL

)

def exception(exc_type, exc_value, exc_traceback):
	
	sys.__excepthook__(exc_type, exc_value, exc_traceback)
	logging.critical('\n\n', exc_info = (exc_type, exc_value, exc_traceback))

sys.excepthook = exception

def get_logger(name: str) -> logging.Logger:

	file_handler = logging.FileHandler(filename = FILE_PATH)
	file_handler.setFormatter(FORMATTER)

	logger = logging.getLogger(name = name)
	logger.setLevel(logging.DEBUG)
	logger.addHandler(file_handler)
	logger.propagate = False
	logger.info(f'logger "{name}" initialised')

	return logger
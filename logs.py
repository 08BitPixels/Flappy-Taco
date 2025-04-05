import logging
import datetime
import os
import sys
from assets import save_path, EXE, LOGS_DIR

LOG_FORMAT = '[%(asctime)s.%(msecs)05d] [%(name)s] [%(levelname)s]: %(message)s'
TIME_FORMAT = '%H:%M:%S'
TODAY = datetime.date.today().strftime('%d-%m-%y')
data: dict[str, int | str] = {}

TODAY_DIR = save_path(os.path.join('..' if EXE else '', LOGS_DIR, TODAY))
os.makedirs(LOGS_DIR, exist_ok = True)
os.makedirs(TODAY_DIR, exist_ok = True)
runs = len(os.listdir(TODAY_DIR)) + 1
FILE_NAME = f'{runs}.log'
FILE_PATH = os.path.join(TODAY_DIR, FILE_NAME)

FORMATTER = logging.Formatter(fmt = LOG_FORMAT, datefmt = TIME_FORMAT)

FILE_HANDLER = logging.FileHandler(filename = FILE_PATH)
FILE_HANDLER.setFormatter(FORMATTER)

# uncaught exception handling
def exception(exc_type, exc_value, exc_traceback):
	
	sys.__excepthook__(exc_type, exc_value, exc_traceback)
	logging.critical('\n\n', exc_info = (exc_type, exc_value, exc_traceback))

logging.basicConfig(

	filename = FILE_PATH, 
	format = LOG_FORMAT, 
	datefmt = TIME_FORMAT,
	level = logging.CRITICAL

)
sys.excepthook = exception

# create new logger for new file
def get_logger(file: str) -> logging.Logger:

	file_name = os.path.basename(file)
	logger = logging.getLogger(name = file_name)
	logger.setLevel(logging.DEBUG)
	logger.addHandler(FILE_HANDLER)
	logger.propagate = False
	logger.info(f'logger "{file_name}" initialised')

	return logger
import logging
import datetime
import os
import sys
import shutil
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
def exception(exc_type, exc_value, exc_traceback) -> None:
	
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

def delete_old_logs(logger: logging.Logger) -> None:

	logger.info('deleting old log directories...')
	dir_contents = os.listdir(LOGS_DIR)
	old_dirs = [dir for dir in dir_contents if dir != os.path.basename(TODAY_DIR)]

	if not old_dirs:
		logger.info('no old log directories found')

	for dir in old_dirs:

		path = save_path(os.path.join('..' if EXE else '', LOGS_DIR, dir))

		try:
			os.chmod(path, 0o777)
			shutil.rmtree(path = path)
			logger.info(f'successfully removed {dir}\'s logs ("{path}")')

		except PermissionError:
			logger.error(f'permission denied whilst trying to remove {dir}\'s logs ("{path}")')
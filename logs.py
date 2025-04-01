import loguru
import datetime
import os
import sys

print('logger init')
logger = loguru.logger
format = '{time} {level} {message}'

def exception(exc_type, exc_value, exc_traceback):
	
	sys.__excepthook__(exc_type, exc_value, exc_traceback)
	logger.critical('\n\n', exc_info = (exc_type, exc_value, exc_traceback))

# sys.excepthook = exception

today = datetime.date.today().strftime('%d-%m-%y')
data: dict[str, int | str] = {}
base_path = os.path.dirname(os.path.abspath(__file__))
dir_path = os.path.join(base_path, '..' if getattr(sys, '_MEIPASS', False) else '', 'logs', today)

os.makedirs(dir_path, exist_ok = True)
runs = len(os.listdir(dir_path)) + 1
file_name = os.path.join(dir_path, f'{runs}.log')

if not os.path.isdir(dir_path):
	os.makedirs(dir_path)

def make_filter(name):
	
    def filter(record): return record['extra'].get('name') == name
    return filter

def get_logger(name: str) -> loguru.logger:
	
	# logger.add(format = f'[%(asctime)s] [{name}]/%(levelname)s]: %(message)s', filter = make_filter(name))

	logger.add(
		sink = file_name, 
		level = 'DEBUG', 
		format = format, 
		filter = make_filter(name),
		colorize = True, 
		backtrace = True
	)
	new_logger = logger.bind(name = name)
	new_logger.info(f'"{name}" logger initialised')

	return new_logger

logger = get_logger(name = 'logs.py') # get logger
logger.info('initialising program...')
pnint()
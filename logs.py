import logging
import datetime
import os
import sys

def make_filter(name):
	
    def filter(record): return record['extra'].get('name') == name
    return filter

print('logger init')
today = datetime.date.today().strftime('%d-%m-%y')
data: dict[str, int | str] = {}

base_path = os.path.dirname(os.path.abspath(__file__))
dir_path = os.path.join(base_path, '..' if getattr(sys, '_MEIPASS', False) else '', 'logs', today)

if not os.path.isdir(dir_path):
	os.makedirs(dir_path)

os.makedirs(dir_path, exist_ok = True)
runs = len(os.listdir(dir_path)) + 1

logger = logging.getLogger(name = __name__)
logging.basicConfig(

	filename = os.path.join(dir_path, f'{runs}.log'), 
	datefmt = '%H:%M:%S',
	level = logging.DEBUG

)

def exception(exc_type, exc_value, exc_traceback):
	
	sys.__excepthook__(exc_type, exc_value, exc_traceback)
	logger.critical('\n\n', exc_info = (exc_type, exc_value, exc_traceback))

sys.excepthook = exception

def get_logger(name: str) -> logging.Logger:
	
	logger.add(format = f'[%(asctime)s] [{name}]/%(levelname)s]: %(message)s', filter = make_filter(name))
	
	new_logger = logger.bind(name = name)
	logger.info(f'"{name}" logger initialised')

	return logger
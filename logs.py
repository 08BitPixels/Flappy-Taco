import logging
import datetime
import os
import sys

print('logger init')
today = datetime.date.today().strftime('%d-%m-%y')
data: dict[str, int | str] = {}

base_path = os.path.dirname(os.path.abspath(__file__))
dir_path = os.path.join(base_path, '..' if getattr(sys, '_MEIPASS', False) else '', 'logs', today)

if not os.path.isdir(dir_path):
	os.makedirs(dir_path)

os.makedirs(dir_path, exist_ok = True)
runs = len(os.listdir(dir_path)) + 1

def get_logger(file: str) -> logging.Logger:

	logger = logging.getLogger(name = file)
	logging.basicConfig(

		filename = os.path.join(dir_path, f'{runs}.log'), 
		format = f'[%(asctime)s] [{file}]/%(levelname)s]: %(message)s', 
		datefmt = '%H:%M:%S',
		level = logging.DEBUG

	)
	logger.info('logger initialised')

	def exception(exc_type, exc_value, exc_traceback):
	
		sys.__excepthook__(exc_type, exc_value, exc_traceback)
		logger.critical('\n\n', exc_info = (exc_type, exc_value, exc_traceback))
	
	sys.excepthook = exception

	return logger
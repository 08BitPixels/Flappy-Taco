import requests
import shutil
import zipfile
import os

from textwrap import dedent

import logs
from assets import CURRENT_VERSION, API_URL, popup_window

logger = logs.get_logger(file = __file__)

def check_update() -> tuple[bool, str, dict]: # -> update available, latest version, dict (containing download info) - if any

	logger.info('checking for updates...')
	response = requests.get(API_URL)

	if response.status_code == 200:

		release_data = response.json()
		latest_version = release_data['tag_name']

		if latest_version and latest_version != CURRENT_VERSION: 
			logger.info('new update available')
			return True, latest_version, release_data
		
		else: 
			logger.info('no update available')
			return False, '', {}

	else:
		
		logger.error(f'error fetching update info: {response.status_code}')
		popup_window(
			title = 'Error',
			description = f'There was an unexpected error fetching update info;\nerror code: {response.status_code}',
			perams = 0 | 0x30
		)
		return False, '', {}

def update(latest_version: str, data: dict) -> None:

	zip_path = f'download_temp/FlappyTaco_{latest_version}.zip'
	dest_path = '../FlappyTaco'

	def download() -> None:

		assets = data.get('assets', [])[0]
		download_url = assets.get('browser_download_url', '')
		
		if not download_url: 

			popup_window(
				title = 'Error',
				description = 'no .zip file found for new version - this is an error on the developer\'s side, please flag this with them on the github page: \nhttps://github.com/08BitPixels/Flappy-Taco/issues',
				perams = 0 | 0x30
			) 
			return

		response = requests.get(download_url, stream = True)
		os.makedirs('download_temp')

		zip_file = open(zip_path, 'wb')
		shutil.copyfileobj(response.raw, zip_file)
		zip_file.close()

		logger.info(f'successfully downloaded: Flappy Taco {latest_version} -> "{zip_path}"')

	def install() -> None:

		zip_file = zipfile.ZipFile(zip_path, 'r')
		zip_file.extractall(dest_path)
		zip_file.close()

		logger.info(f'successfully extracted "{zip_path}" -> "{dest_path}"')

		shutil.rmtree('download_temp')
		logger.info(f'deleted "{zip_path}"')

	logger.info(f'downloading: Flappy Taco {latest_version} ...')

	download()
	install()

	logger.info(f'successfully installed Flappy Taco {latest_version}')
	popup_window(
		title = 'Complete',
		description = dedent(
			f'''
			Download + Installation of Flappy Taco {latest_version} completed successfully.
			Please restart the game to run the updated version.
			'''
		),
		perams = 0 | 0x40
	)

def init() -> None:

	update_available, latest_version, data = check_update()

	if update_available and data:

		description = dedent(
			f'''
			Download: Flappy Taco {latest_version}?
			(The new version will be downloaded and installed automatically)
			'''
		)
		response = popup_window(title = 'Update Available', description = description, perams = 4 | 0x40)
		to_update = not (response - 6)

		if to_update: 
			logger.info('update requested')
			update(latest_version, data)
		else:
			logger.info('update declined')

if __name__ == '__main__': init()
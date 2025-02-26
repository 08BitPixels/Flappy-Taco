import ctypes
import requests
import shutil
import zipfile
import os
import subprocess

CURRENT_VERSION = 'v1.2.0'
API_URL = 'https://api.github.com/repos/08BitPixels/Flappy-Taco/releases/latest'

def check_update() -> tuple[bool, str]: # -> update available, latest version

	response = requests.get(API_URL)

	if response.status_code == 200:

		release_data = response.json()
		latest_version = release_data['tag_name']

		if latest_version and latest_version != CURRENT_VERSION: 
			return True, latest_version
		else: 
			print('No Update Available')
			return False, ''

	else:
		
		print(f'Error: {response.status_code}')
		return False, ''

def update(latest_version: str) -> None:

	zip_path = f'download_temp/FlappyTaco_{latest_version}.zip'
	dest_path = f'../Flappy Taco {latest_version}'

	def download(response: requests.Response) -> None:

		release_data = response.json()

		for asset in release_data.get('assets', []):
			if asset.get('browser_download_url'):
				download_url = asset['browser_download_url']
				break
		
		if not download_url: 
			ctypes.windll.user32.MessageBoxW(0, 'No latest version to download', 'Error', 0)
			return

		response = requests.get(download_url, stream = True)
		os.makedirs('download_temp')

		with open(zip_path, 'wb') as zip_file:
			shutil.copyfileobj(response.raw, zip_file)

		print(f'Successfully Downloaded: Flappy Taco {latest_version} -> {zip_path}')

	def install() -> None:

		with zipfile.ZipFile(zip_path, 'r') as zip_ref:
			zip_ref.extractall(dest_path)

		print(f'Successfully Extracted {zip_path} -> {dest_path}')

		shutil.rmtree('download_temp')
		print(f'- Deleted {zip_path}')

	print(f'Downloading: Flappy Taco {latest_version} ...')

	response = requests.get(API_URL)

	if response.status_code == 200:

		download(response)
		install()

		exe_path = f'{dest_path}/FlappyTaco.exe'
		subprocess.run([exe_path], shell = True)

		current_dir = os.path.dirname(__file__)

		#shutil.rmtree(current_dir)

	else:
		
		ctypes.windll.user32.MessageBoxW(0, f'Error during request fetch: {response.status_code}', 'Error', 0)

def main() -> None:

	update_available, latest_version = check_update()

	if update_available:

		to_update = not (ctypes.windll.user32.MessageBoxW(0, f'Download: Flappy Taco {latest_version}?\n(The new version will be downloaded and installed automatically)', 'Update Available', 4) - 6)

		if to_update: update(latest_version)

if __name__ == '__main__': main()
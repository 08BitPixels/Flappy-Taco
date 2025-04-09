from random import randint
from time import time
from typing import TypedDict, Literal

import pygame

import assets
import logs
# import update
import file_config

# ORDER OF MODULE INITIALISATION	
# 1. assets.py 		-> main funcs + constant vars
# 2. logs.py   		-> initialise logging for program
# 3. update.py 		-> check for updates
# 4. file_config.py -> retreive config + user data
# 5. main.py   		-> run game

# logging
logger = logs.get_logger(file = __file__) # get logger
logger.info('initialising game...')

# updates
# update.main() # check for updates

# assets
file_handler, CONSTANTS, USER_DATA = file_config.init()
WIDTH, HEIGHT = CONSTANTS['screen_dimensions']
CENTRE_X, CENTRE_Y = CONSTANTS['centre_coords']
FPS, VSYNC = CONSTANTS['FPS'], CONSTANTS['VSYNC']
VOLUMES = CONSTANTS['volumes']
COLOURS = CONSTANTS['colours']
logger.info('constants imported')

# PYGAME SETUP
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED if VSYNC else 0, vsync = VSYNC)
clock = pygame.time.Clock()
logger.info('pygame initialised: screen and clock objects created')

# Window Setup
icon = pygame.image.load(assets.resource_path('images/icon.ico')).convert_alpha()
splashscreen = pygame.image.load(assets.resource_path('images/splashscreen.png')).convert_alpha()
splashscreen = pygame.transform.scale(splashscreen, assets.splashscreen_size(img_size = splashscreen.get_size(), screen_size = (WIDTH, HEIGHT))).convert_alpha()

pygame.display.set_icon(icon)
pygame.display.set_caption('Flappy Taco | INITIALISING...')
screen.blit(splashscreen, splashscreen.get_rect(center = (CENTRE_X, CENTRE_Y)))
pygame.display.update()

# Fonts
main_font = pygame.font.Font(assets.resource_path('fonts/slkscrb.ttf'), size = 50)
secondary_font = pygame.font.Font(assets.resource_path('fonts/slkscr.ttf'), size = 30)
logger.info('fonts loaded')

# Typed Dictionaries
# SFX
class ChilliSFXDict(TypedDict):
	collect: pygame.mixer.Sound

class PlayerSFXDict(TypedDict):
	death: pygame.mixer.Sound
	jump: pygame.mixer.Sound

class ButtonSFXDict(TypedDict):
	click: pygame.mixer.Sound

class SFXDict(TypedDict):
	chilli: ChilliSFXDict
	player: PlayerSFXDict
	button: ButtonSFXDict

# Game States
class GameStatesDict(TypedDict):
	menu: Literal[0]
	help: Literal[1]
	choose_taco: Literal[2]
	play: Literal[3]
	over: Literal[4]

# Sprites
class Game:

	STATES: GameStatesDict = {
		'menu': 0,
		'help': 1,
		'choose_taco': 2,
		'play': 3,
		'over': 4
	}

	# Fork Settings
	_FORK_SPEED = 400
	_FORK_COUNT = 5
	_FORK_FREQUENCY = 1000
	# Timers
	CHILLI_FREQUENCY = 1
	FORK_TIMER = pygame.USEREVENT + 1

	def __init__(self, user_data: file_config.UserDataDict) -> None:
		
		self._state: Literal[0, 1, 2, 3, 4] = self.STATES['menu']
		self._started = False
		self._paused = False
		self.score = 0
		self.high_score: int = user_data['high_score']

		# Audio
		self._MUSIC = pygame.mixer.Sound(assets.resource_path('audio/music/raining-tacos.mp3'))
		self._MUSIC.set_volume(VOLUMES['music'])

		self.SFX: SFXDict = {
			'chilli': {
				'collect': pygame.mixer.Sound(assets.resource_path('audio/sfx/chilli/collect.mp3')),
			},
			'player': {
				'death': pygame.mixer.Sound(assets.resource_path('audio/sfx/player/death.mp3')),
				'jump': pygame.mixer.Sound(assets.resource_path('audio/sfx/player/jump.wav'))
			},
			'button': {
				'click': pygame.mixer.Sound(assets.resource_path('audio/sfx/button/click.wav'))
			}
		}
		
		logger.info('audio initialised')

		self.text = Text(self)
		self.player = pygame.sprite.GroupSingle(Player(game = self, user_data = user_data))
		self.forks: pygame.sprite.Group = pygame.sprite.Group()
		self.chillies: pygame.sprite.Group = pygame.sprite.Group()
		self.background = pygame.sprite.Group(
			Background(CENTRE_X), 
			Background(CENTRE_X + WIDTH)
		)
		self.menu_sprites = pygame.sprite.Group(
			IntroSprite(type = 'rays', pos = (CENTRE_X + 150, CENTRE_Y + 215), game = self),
			IntroSprite(type = 'taco', pos = (CENTRE_X + 150, CENTRE_Y + 225), game = self),
			Button(type = 'play', pos = (120, CENTRE_Y + 120), animation_type = 'slide', animation_offset = 25, press_state = self.STATES['play'], game = self),
			Button(type = 'help', pos = (WIDTH - 85, HEIGHT - 100), animation_type = 'float', animation_offset = 0.2, press_state = self.STATES['help'], game = self),
			Button(type = 'choose-taco', pos = (147, HEIGHT - 100), animation_type = 'slide', animation_offset = 25, press_state = self.STATES['choose_taco'], game = self)
		)
		self.choose_taco_sprites = pygame.sprite.Group(
			IntroSprite(type = 'rays', pos = (CENTRE_X, CENTRE_Y + 10), game = self),
			Button(type = 'ok!', pos = (CENTRE_X, CENTRE_Y + 250), animation_type = 'float', animation_offset = 0.2, press_state = self.STATES['menu'], game = self),
			Button(type = 'arrow-left', pos = (CENTRE_X - 300, CENTRE_Y), animation_type = 'float', animation_offset = 0.4, press_state = 'last-costume', game = self),
			Button(type = 'arrow-right', pos = (CENTRE_X + 300, CENTRE_Y), animation_type = 'float', animation_offset = 0.4, press_state = 'next-costume', game = self)
		)
		self.game_over_sprites = pygame.sprite.Group(
			MenuBackground(pos = (CENTRE_X, 0), offset = HEIGHT // 2),
			Button(type = 'try-again', pos = (CENTRE_X, CENTRE_Y + 60), animation_type = 'float', animation_offset = 0.2, press_state = self.STATES['play'], game = self),
			Button(type = 'main-menu', pos = (CENTRE_X, CENTRE_Y + 160), animation_type = 'float', animation_offset = 0.2, press_state = self.STATES['menu'], game = self)
		)
		self.pause_sprites = pygame.sprite.Group(
			MenuBackground(pos = (CENTRE_X, 0), offset = HEIGHT // 2),
			Button(type = 'resume', pos = (CENTRE_X, CENTRE_Y + 50), animation_type = 'float', animation_offset = 0.2, press_state = 'unpause', game = self),
			Button(type = 'main-menu', pos = (CENTRE_X, CENTRE_Y + 150), animation_type = 'float', animation_offset = 0.2, press_state = self.STATES['menu'], game = self)
		)
		logger.info('sprites inititalised')

		# Timers
		pygame.time.set_timer(self.FORK_TIMER, self._FORK_FREQUENCY)

		self._MUSIC.play(loops = -1)
	
	@ property
	def paused(self) -> bool:
		return self._paused

	@ paused.setter
	def paused(self, paused: bool) -> None:
		self._paused = paused

	@ property
	def state(self) -> Literal[0, 1, 2, 3, 4]:
		return self._state

	@ state.setter
	def state(self, state: Literal[0, 1, 2, 3, 4]) -> None:
		self._state = self.STATES[('menu', 'help', 'choose_taco', 'play', 'over')[state]]

	def start(self) -> None:
		self._started = True
	
	@ property
	def started(self) -> bool:
		return self._started

	def chilli_collected(self) -> None:
		self.player.sprite.chilli_energy += 200

	def restart(self) -> None:

		self.state = self.STATES['play']
		self._started = False
		self._paused = False
		self.score = 0
		self.player.sprite.reset()
		self.forks.empty()
		self.chillies.empty()
		[sprite.reset() for sprite in self.game_over_sprites.sprites() if hasattr(sprite, 'reset')]
		[sprite.reset() for sprite in self.menu_sprites.sprites() if hasattr(sprite, 'reset')]
		
	def handle_game_over(self) -> None:

		self.SFX['player']['death'].play()
		self.state = self.STATES['over']

	def point(self) -> None:

		self.score += 1
		if self.score > self.high_score: self.high_score = self.score

	def quit(self) -> None:

		logger.info('quit requested, confirming...')

		response = assets.popup_window(
			title = 'Quit',
			description = 'Are you sure you want to quit the game?', 
			perams = 4 | 0x20
		)
		to_quit = not (response - 6)

		if to_quit:

			logger.info('quit confirmed, quitting game...')
			
			config: file_config.ConfigDict = {
				'screen_setup': {
					'width': WIDTH,
					'height': HEIGHT,
					'FPS': FPS,
					'VSYNC': VSYNC
				},
				'audio_volume': {
					'music': VOLUMES['music'],
					'sfx': VOLUMES['sfx']
				},
				'del_old_logs': file_handler.del_old_logs
			}
			user_data: file_config.UserDataDict = {
				'high_score': self.high_score, 
				'costume_index': (0, 1, 2, 3, 4, 5, 6)[self.player.sprite.image_index]
			}

			file_handler.save_data(mode = 0, data = config)
			file_handler.save_data(mode = 1, data = user_data)

			pygame.quit()
			exit()
		
		logger.info('quit cancelled')

class Text:

	def __init__(self, game: Game) -> None:

		self.game = game
		self.texts: list[tuple[pygame.surface.Surface, pygame.rect.Rect]] = []

		# Texts

		self.fps_text1 = secondary_font.render('FPS:', False, COLOURS['light_grey'], COLOURS['black'])
		self.fps_text1_rect = self.fps_text1.get_rect(topleft = (0, 0))

		self.fps_text2 = pygame.surface.Surface((0, 0))
		self.fps_text2_rect = self.fps_text2.get_rect(topleft = (0, 0))

		# Menu Screen
		self.menu_txt1 = pygame.image.load(assets.resource_path('images/text/flappy.png')).convert_alpha()
		self.menu_txt1 = pygame.transform.scale_by(self.menu_txt1, 0.25)
		self.menu_txt1_rect = self.menu_txt1.get_rect(topleft = (100, 100))

		self.menu_txt2 = pygame.image.load(assets.resource_path('images/text/taco!.png')).convert_alpha()
		self.menu_txt2 = pygame.transform.scale_by(self.menu_txt2, 0.4)
		self.menu_txt2_rect = self.menu_txt2.get_rect(center = (CENTRE_X, CENTRE_Y - 50))

		# Control Screen
		self.control_txt1 = pygame.image.load(assets.resource_path('images/text/help.png')).convert_alpha()
		self.control_txt1 = pygame.transform.scale(self.control_txt1, (WIDTH, HEIGHT))
		self.control_txt1_rect = self.control_txt1.get_rect(center = (CENTRE_X, CENTRE_Y))

		# Game Over Screen
		self.over_txt1 = pygame.image.load(assets.resource_path('images/text/game-over.png')).convert_alpha()
		self.over_txt1 = pygame.transform.scale_by(self.over_txt1, 0.25)
		self.over_txt1_rect = self.over_txt1.get_rect(center = (CENTRE_X, CENTRE_Y - 150))

		self.over_txt2 = pygame.surface.Surface((0, 0))
		self.over_txt2_rect = self.over_txt2.get_rect(topleft = (0, 0))

		self.over_txt3 = pygame.surface.Surface((0, 0))
		self.over_txt3_rect = self.over_txt3.get_rect(topleft = (0, 0))

		self.over_txt4 = pygame.surface.Surface((0, 0))
		self.over_txt4_rect = self.over_txt4.get_rect(topleft = (0, 0))

		# Play Screen
		self.play_txt1 = main_font.render('Click to Begin', False, COLOURS['light_yellow'])
		self.play_txt1_rect = self.play_txt1.get_rect(center = (CENTRE_X, CENTRE_Y - 100))

		self.play_txt2 = pygame.image.load(assets.resource_path('images/text/paused.png')).convert_alpha()
		self.play_txt2 = pygame.transform.scale_by(self.play_txt2, 0.3)
		self.play_txt2_rect = self.play_txt2.get_rect(center = (CENTRE_X, CENTRE_Y - 120))

		self.play_txt4 = secondary_font.render('SCORE:', False, COLOURS['light_grey'], COLOURS['black'])
		self.play_txt4_rect = self.play_txt4.get_rect(topright = (WIDTH, 80))

		self.score_txt = pygame.surface.Surface((0, 0))
		self.score_txt_rect = self.score_txt.get_rect(topleft = (0, 0))

		self.play_txt5 = secondary_font.render('HIGHSCORE:', False, COLOURS['light_grey'], COLOURS['black'])
		self.play_txt5_rect = self.play_txt5.get_rect(topright = (WIDTH, 0))

		self.high_score_txt = pygame.surface.Surface((0, 0))
		self.high_score_txt_rect = self.high_score_txt.get_rect(topleft = (0, 0))

		self.play_txt6 = secondary_font.render('CHILLI ENERGY:', False, COLOURS['yellow'], COLOURS['black'])
		self.play_txt6_rect = self.play_txt6.get_rect(topleft = (0, 40))

		self.chilli_energy_txt = pygame.surface.Surface((0, 0))
		self.chilli_energy_txt_rect = self.chilli_energy_txt.get_rect(topleft = (0, 0))

		# Choose Taco Screen
		self.choose_taco_txt1 = pygame.image.load(assets.resource_path('images/text/choose-costume.png')).convert_alpha()
		self.choose_taco_txt1 = pygame.transform.scale_by(self.choose_taco_txt1, 0.3)
		self.choose_taco_txt1_rect = self.choose_taco_txt1.get_rect(center = (CENTRE_X, 75))

		self.choose_taco_txt2 = pygame.surface.Surface((0, 0))
		self.choose_taco_txt2_rect = self.choose_taco_txt2.get_rect(topleft = (0, 0))

	def update(self) -> None:

		fps = round(clock.get_fps())
		fps_colour = COLOURS['green'] if (fps >= 60) else COLOURS['yellow'] if (fps < 60 and fps >= 10) else COLOURS['red']
		self.fps_text2 = secondary_font.render(str(fps), False, fps_colour, COLOURS['black'])
		self.fps_text2_rect = self.fps_text2.get_rect(topleft = (75, 0))

		state = self.game.state

		if state == self.game.STATES['menu']:

			self.high_score_txt = main_font.render(str(self.game.high_score), False, COLOURS['white'], COLOURS['black'])
			self.high_score_txt_rect = self.high_score_txt.get_rect(topright = (WIDTH, 30))

			self.choose_taco_txt2 = main_font.render(self.game.player.sprite.costume_name(), False, COLOURS['light_yellow'], COLOURS['black'])
			self.choose_taco_txt2_rect = self.choose_taco_txt2.get_rect(center = (CENTRE_X + 150, CENTRE_Y + 75))

			self.texts = [
				(self.menu_txt1, self.menu_txt1_rect), 
				(self.menu_txt2, self.menu_txt2_rect),
				(self.play_txt5, self.play_txt5_rect),
				(self.high_score_txt, self.high_score_txt_rect),
				(self.fps_text1, self.fps_text1_rect),
				(self.fps_text2, self.fps_text2_rect),
				(self.choose_taco_txt2, self.choose_taco_txt2_rect)
			]
		
		elif state == self.game.STATES['help']:

			self.texts = [
				(self.control_txt1, self.control_txt1_rect),
			]

		elif state == self.game.STATES['over']:

			self.over_txt2 = secondary_font.render(f"Final Score: {self.game.score}", False, COLOURS['light_grey'], COLOURS['black'])
			self.over_txt2_rect = self.over_txt2.get_rect(center = (CENTRE_X, CENTRE_Y - 40))

			self.over_txt3 = secondary_font.render(f"HIGHSCORE: {self.game.high_score}", False, COLOURS['light_grey'], COLOURS['black'])
			self.over_txt3_rect = self.over_txt3.get_rect(center = (CENTRE_X, CENTRE_Y - 10))

			self.over_txt4 = secondary_font.render(f"You {self.game.player.sprite.death_cause}!", False, COLOURS['red'], COLOURS['black'])
			self.over_txt4_rect = self.over_txt4.get_rect(center = (CENTRE_X, CENTRE_Y - 80))

			self.texts = [
				(self.over_txt1, self.over_txt1_rect),
				(self.over_txt2, self.over_txt2_rect),
				(self.over_txt3, self.over_txt3_rect),
				(self.over_txt4, self.over_txt4_rect),
				(self.play_txt4, self.play_txt4_rect),
				(self.play_txt5, self.play_txt5_rect),
				(self.play_txt6, self.play_txt6_rect),
				(self.score_txt, self.score_txt_rect),
				(self.high_score_txt, self.high_score_txt_rect),
				(self.chilli_energy_txt, self.chilli_energy_txt_rect),
				(self.fps_text1, self.fps_text1_rect),
				(self.fps_text2, self.fps_text2_rect)
			]

		elif state == self.game.STATES['play']:

			self.score_txt = main_font.render(str(self.game.score), False, COLOURS['white'], COLOURS['black'])
			self.score_txt_rect = self.score_txt.get_rect(topright = (WIDTH, 110))

			self.high_score_txt = main_font.render(str(self.game.high_score), False, COLOURS['white'], COLOURS['black'])
			self.high_score_txt_rect = self.high_score_txt.get_rect(topright = (WIDTH, 30))

			self.chilli_energy_txt = main_font.render(str(self.game.player.sprite.chilli_energy), False, COLOURS['light_yellow'], COLOURS['black'])
			self.chilli_energy_txt_rect = self.chilli_energy_txt.get_rect(topleft = (0, 70))

			if not self.game.started:

				self.texts = [
					(self.play_txt1, self.play_txt1_rect),
					(self.play_txt4, self.play_txt4_rect),
					(self.play_txt5, self.play_txt5_rect),
					(self.play_txt6, self.play_txt6_rect),
					(self.score_txt, self.score_txt_rect),
					(self.high_score_txt, self.high_score_txt_rect),
					(self.chilli_energy_txt, self.chilli_energy_txt_rect),
					(self.fps_text1, self.fps_text1_rect),
					(self.fps_text2, self.fps_text2_rect)
				]

			elif self.game.started and self.game.paused:

				self.texts = [
					(self.play_txt2, self.play_txt2_rect),
					(self.play_txt4, self.play_txt4_rect),
					(self.play_txt5, self.play_txt5_rect),
					(self.play_txt6, self.play_txt6_rect),
					(self.score_txt, self.score_txt_rect),
					(self.high_score_txt, self.high_score_txt_rect),
					(self.chilli_energy_txt, self.chilli_energy_txt_rect),
					(self.fps_text1, self.fps_text1_rect),
					(self.fps_text2, self.fps_text2_rect)	
				]

			else:

				self.texts = [
					(self.play_txt4, self.play_txt4_rect),
					(self.play_txt5, self.play_txt5_rect),
					(self.play_txt6, self.play_txt6_rect),
					(self.score_txt, self.score_txt_rect),
					(self.high_score_txt, self.high_score_txt_rect),
					(self.chilli_energy_txt, self.chilli_energy_txt_rect),
					(self.fps_text1, self.fps_text1_rect),
					(self.fps_text2, self.fps_text2_rect)
				]

		elif state == self.game.STATES['choose_taco']:

			self.choose_taco_txt2 = main_font.render(self.game.player.sprite.costume_name(), False, COLOURS['light_yellow'], COLOURS['black'])
			self.choose_taco_txt2_rect = self.choose_taco_txt2.get_rect(center = (CENTRE_X, CENTRE_Y - 150))
		
			self.texts = [
				(self.choose_taco_txt1, self.choose_taco_txt1_rect),
				(self.choose_taco_txt2, self.choose_taco_txt2_rect),
				(self.fps_text1, self.fps_text1_rect),
				(self.fps_text2, self.fps_text2_rect)
			]

		else:
			self.texts.clear()

class Player(pygame.sprite.Sprite):

	def __init__(self, user_data: file_config.UserDataDict, game: Game) -> None:

		super().__init__()
		self.game = game

		self.images = [pygame.transform.scale_by(pygame.image.load(assets.resource_path(f'images/player/taco{i}.png')).convert_alpha(), 0.3) for i in range(7)]

		self.image_index = int(user_data['costume_index'])
		self.image = self.images[self.image_index]
		self.mask = pygame.mask.from_surface(self.images[0])

		self.rect = self.images[0].get_rect(center = (CENTRE_X - 200, CENTRE_Y))
		self.pos = pygame.math.Vector2(self.rect.center)

		self.SFX: PlayerSFXDict = self.game.SFX['player']
		self.SFX['jump'].set_volume(2 * VOLUMES['sfx'])

		self.GRAVITY = 3000
		self.MAX_CHILLI_ENERGY = 1000
		self.JUMP_COST = 25
		self.JUMP_BOOST = 750
		self.y_vel = 0.0
		self.chilli_energy = self.MAX_CHILLI_ENERGY
		self.death_cause = ''
		self.jumping = False

	def update(self, dt: float) -> None:

		self.pos = pygame.math.Vector2(self.pos)
		self.rect.center = (round(self.pos.x), round(self.pos.y))
		if self.chilli_energy > self.MAX_CHILLI_ENERGY: self.chilli_energy = self.MAX_CHILLI_ENERGY
		self.input()
		self.check_death()
		self.fall(dt)

	def input(self) -> None:
		
		mouse_pressed = pygame.mouse.get_pressed()[0]

		if mouse_pressed and not self.jumping:

			self.jumping = True
			self.jump()

		elif not mouse_pressed:
			self.jumping = False

	def reset(self) -> None:

		self.pos = pygame.math.Vector2(CENTRE_X - 200, CENTRE_Y)
		self.image = self.images[self.image_index]
		self.mask = pygame.mask.from_surface(self.images[0])
		self.rect = self.images[0].get_rect(center = self.pos)
		self.chilli_energy = self.MAX_CHILLI_ENERGY
		self.y_vel = 0.0
		self.jumping = False
		self.death_cause = ''

	def check_death(self) -> None:

		if pygame.sprite.spritecollide(self, self.game.forks, False, pygame.sprite.collide_rect):

			if pygame.sprite.spritecollide(self, self.game.forks, False, pygame.sprite.collide_mask): 
			
				self.death_cause = 'crashed into a Fork'
				self.game.handle_game_over()

		if self.pos.y <= 0 + (self.image.get_height() / 2) or self.pos.y >= HEIGHT - (self.image.get_height() / 2): 
			
			self.death_cause = 'went out of bounds'
			self.game.handle_game_over()

		if self.chilli_energy <= 0: 
			
			self.death_cause = 'ran out of Chilli Energy'
			self.chilli_energy = 0

	def fall(self, dt: float) -> None:

		self.pos.y += self.y_vel * dt
		self.y_vel += self.GRAVITY * dt

	def jump(self) -> None:

		if self.chilli_energy > 0:

			self.SFX['jump'].play()
			self.y_vel = -self.JUMP_BOOST
			self.chilli_energy -= self.JUMP_COST

	def costume_display(self) -> None:

		self.image = self.images[self.image_index]
		self.image = pygame.transform.scale_by(self.images[self.image_index], 1.75)
		self.rect = self.image.get_rect(center = (CENTRE_X, CENTRE_Y))

	def costume_name(self) -> str:
		return ['Taco', 'Wizard Taco', 'MLG Taco', 'Skateboarder Taco', 'Savage Taco', 'Gamer Taco', 'Holy Taco', 'Red Hot Devil Taco'][self.image_index]

class Fork(pygame.sprite.Sprite):

	def __init__(self, speed: int, orientation: str, offset: int, game: Game) -> None:

		super().__init__()

		self.image = pygame.image.load(assets.resource_path('images/fork/fork.png')).convert_alpha()
		self.image = pygame.transform.scale_by(self.image, 1.5)

		if orientation == 'up':

			self.image = pygame.transform.rotate(self.image, 180.0)
			self.rect = self.image.get_rect(bottomleft = (WIDTH, offset - 150))
		
		if orientation == 'down':
			self.rect = self.image.get_rect(topleft = (WIDTH, offset + 150))

		self.pos = pygame.math.Vector2(self.rect.center)
		self.SPEED = speed
		self.orientation = orientation
		self.game = game
		self.passed = False
	
	def update(self, dt: float) -> None:

		self.rect.center = (round(self.pos.x), round(self.pos.y))	
		self.scroll(dt)
		if not self.passed: self.update_score()

	def scroll(self, dt: float) -> None:

		self.pos.x -= self.SPEED * dt
		if self.pos.x + (self.image.get_width() / 2) <= 0: self.kill()

	def update_score(self) -> None:

		if self.orientation == 'up':

			if self.pos.x <= self.game.player.sprite.pos.x: 
				
				self.passed = True
				self.game.point()

class Chilli(pygame.sprite.Sprite):

	def __init__(self, speed: int, y_offset: int, game: Game) -> None:

		super().__init__()
		self.game = game

		self.chilli = pygame.image.load(assets.resource_path('images/chilli/chilli.png')).convert_alpha()
		self.chilli = pygame.transform.scale_by(self.chilli, 1.25)
		self.collect = main_font.render('+100', False, COLOURS['light_yellow'], COLOURS['black'])

		self.image = self.chilli
		self.rect = self.image.get_rect(center = (WIDTH + 50, y_offset))
		self.pos = pygame.math.Vector2(self.rect.center)

		self.SFX: ChilliSFXDict = self.game.SFX['chilli']
		self.SFX['collect'].set_volume(5 * VOLUMES['sfx'])

		self.speed = speed
		self.collected = False

	def update(self, dt: float) -> None:

		self.rect.center = (round(self.pos.x), round(self.pos.y))
		self.scroll(dt)
		if not self.collected: self.check_collision()

	def scroll(self, dt: float) -> None:

		self.pos.x -= self.speed * dt
		if self.pos.x + (self.image.get_width() / 2) <= 0: self.kill()

	def check_collision(self) -> None:

		if pygame.sprite.collide_rect(self, self.game.player.sprite): 
			
			self.collected = True
			self.game.chilli_collected()
			self.SFX['collect'].play()
			self.image = self.collect
			self.rect = self.image.get_rect(center = self.pos)

class Background(pygame.sprite.Sprite):

	def __init__(self, x_pos: int) -> None:

		super().__init__()

		self.image = pygame.image.load(assets.resource_path('images/background/stars.png')).convert_alpha()
		self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
		self.rect = self.image.get_rect(center = (x_pos, CENTRE_Y))
		self.pos = pygame.math.Vector2(self.rect.center)

		self.SPEED = 100

	def update(self, dt: float) -> None:

		self.rect.center = (round(self.pos.x), round(self.pos.y))
		self.scroll(dt)

	def scroll(self, dt: float) -> None:

		self.pos.x -= self.SPEED * dt
		if self.pos.x <= 0 - WIDTH / 2: self.pos.x = WIDTH + WIDTH / 2

class Button(pygame.sprite.Sprite):

	def __init__(self, type: str, pos: tuple, animation_type: str, animation_offset: int | float, press_state: Literal[0, 1, 2, 3, 4, 'next-costume', 'last-costume', 'unpause'], game: Game) -> None:

		super().__init__()
		self.game = game

		self.default = pygame.image.load(assets.resource_path(f'images/button/{type}/{type}.png')).convert_alpha()

		if animation_type == 'slide':

			self.select = pygame.image.load(assets.resource_path(f'images/button/{type}/{type}-select.png')).convert_alpha()
			self.frames = [self.default, self.select]
			self.state = 0
			self.image = self.frames[self.state]

		if animation_type == 'float':

			self.image = self.default
			self.scale = 1.0

		self.rect = self.image.get_rect(center = pos)
		self.pos = pygame.math.Vector2(self.rect.center)

		self.SFX: ButtonSFXDict = self.game.SFX['button']
		self.SFX['click'].set_volume(0.25 * VOLUMES['sfx'])

		self.type = type
		self.start_pos = pos
		self.animation_type = animation_type
		self.animation_offset = animation_offset
		self.press_state = press_state
		self.pressing = False
		self.ANIMATION_SPEED = 20

	def update(self, dt: float) -> None:

		if self.animation_type == 'slide': self.image = self.frames[self.state]
		self.rect.center = (round(self.pos.x), round(self.pos.y))
		self.input(dt)

	def input(self, dt: float) -> None:

		mouse_pos = pygame.mouse.get_pos()
		mouse_pressed = pygame.mouse.get_pressed()

		if self.rect.collidepoint(mouse_pos): 
			
			if self.animation_type == 'slide': self.state = 1
			self.animate(self.animation_type, 'out', dt)

			if mouse_pressed[0] and not self.pressing: 
				
				self.pressing = True
				self.pressed()

			elif not mouse_pressed[0]: self.pressing = False

		elif not self.rect.collidepoint(mouse_pos): 
			
			if self.animation_type == 'slide': self.state = 0
			self.animate(self.animation_type, 'in', dt)

	def animate(self, type: str, dir: str, dt: float) -> None:

		if type == 'slide':

			if dir == 'out': self.pos.x += (self.ANIMATION_SPEED * dt) * ((self.start_pos[0] + self.animation_offset) - self.pos.x)
			if dir == 'in': self.pos.x += (self.ANIMATION_SPEED * dt) * (self.start_pos[0] - self.pos.x)

		if type == 'float':
			
			if dir == 'out': 
				
				self.scale += (self.ANIMATION_SPEED * dt) * ((1 + self.animation_offset) - self.scale)
				self.image = pygame.transform.scale_by(self.default, self.scale)
				self.rect = self.image.get_rect(center = self.pos)

			if dir == 'in': 
				
				self.scale += (self.ANIMATION_SPEED * dt) * (1 - self.scale)
				self.image = pygame.transform.scale_by(self.default, self.scale)
				self.rect = self.image.get_rect(center = self.pos)

	def pressed(self) -> None:

		self.SFX['click'].play()

		if self.press_state == self.game.STATES['play']: 
			self.game.restart()

		elif self.press_state == 'unpause': 
			self.game.paused = False

		elif self.press_state == 'next-costume': 

			self.game.player.sprite.image_index = (self.game.player.sprite.image_index + 1) % len(self.game.player.sprite.images)

		elif self.press_state == 'last-costume':

			if self.game.player.sprite.image_index <= 0: self.game.player.sprite.image_index = len(self.game.player.sprite.images)
			self.game.player.sprite.image_index -= 1

		else: 
			self.game.state = self.press_state

		self.reset()

	def reset(self) -> None:

		self.pos = pygame.math.Vector2(self.start_pos)
		if self.animation_type == 'slide': self.state = 0
		if self.animation_type == 'float': self.scale = 1

class IntroSprite(pygame.sprite.Sprite):

	def __init__(self, type: str, pos: tuple, game: Game) -> None:

		super().__init__()

		self.game = game
		self.type = type
		self.pos = pos
		
		if type == 'rays':

			self.og_image = pygame.image.load(assets.resource_path('images/intro-sprite/god-rays.png')).convert_alpha()
			self.og_image = pygame.transform.scale_by(self.og_image, 0.75).convert_alpha()
			self.image = self.og_image
			self.rect = self.image.get_rect(center = pos)
			self.rotation = 0
			self.rotation_speed = 50

		if type == 'taco':

			self.frame_vel = 2
			self.SCALE = 1.5
			self.normal = pygame.transform.scale_by(self.game.player.sprite.images[self.game.player.sprite.image_index], self.SCALE).convert_alpha()
			self.large = pygame.transform.scale_by(self.normal, 1.3).convert_alpha()
			self.frames = [self.normal, self.large]
			self.frame_index = 0.0
			self.image = self.frames[int(self.frame_index)]
			self.rect = self.image.get_rect(center = self.pos)
	
	def update(self, dt: float) -> None:

		if self.type == 'taco': self.animate(dt)

	def animate(self, dt: float) -> None:

		self.normal = pygame.transform.scale_by(self.game.player.sprite.images[self.game.player.sprite.image_index], self.SCALE).convert_alpha()
		self.large = pygame.transform.scale_by(self.normal, 1.3).convert_alpha()
		self.frames = [self.normal, self.large]
		self.frame_index = self.frame_index + (self.frame_vel * dt)
		self.frame_index %= len(self.frames)
		self.image = self.frames[int(self.frame_index)]
		self.rect = self.image.get_rect(center = (self.pos[0], self.pos[1] - 15))

	def reset(self) -> None:

		self.rect = self.image.get_rect(center = self.pos)

		if self.type == 'taco':
			
			self.frame_index = 0
			self.image = self.frames[self.frame_index]

class MenuBackground(pygame.sprite.Sprite):

	def __init__(self, pos: tuple, offset: int) -> None:

		super().__init__()

		self.image = pygame.image.load(assets.resource_path('images/game-over-menu/game-over-menu.png')).convert_alpha()
		self.image = pygame.transform.scale_by(self.image, 0.3)
		self.rect = self.image.get_rect(midbottom = pos)
		self.pos = pygame.math.Vector2(self.rect.center)

		self.start_pos = pos
		self.offset = offset
		self.ANIMATION_SPEED = 20

	def update(self, dt: float) -> None:

		self.rect.center = (round(self.pos.x), round(self.pos.y))
		self.animate(dt)

	def animate(self, dt: float) -> None:
		self.pos.y += (self.ANIMATION_SPEED * dt) * ((self.start_pos[1] + self.offset) - self.pos.y)

	def reset(self) -> None:
		self.pos = pygame.math.Vector2(self.start_pos)

def main() -> None:

	start_time = time()

	game = Game(user_data = USER_DATA)
	text = game.text
	player = game.player
	forks = game.forks
	chillies = game.chillies
	background = game.background
	menu_sprites = game.menu_sprites
	choose_taco_sprites = game.choose_taco_sprites
	game_over_sprites = game.game_over_sprites
	pause_sprites = game.pause_sprites

	logger.info(f'game initialised in {round(time() - start_time, 3)}s')
	pygame.display.set_caption('Flappy Taco')
	previous_time = time()

	while True:

		dt = time() - previous_time
		previous_time = time()
		
		for event in pygame.event.get():

			match event.type:

				case pygame.QUIT:

					logger.info('pygame.QUIT event detected')
					game.quit()

				case pygame.MOUSEBUTTONDOWN:

					logger.info('[LEFT MOUSE BUTTON] pressed')

					if game.state == game.STATES['help']: 
						game.state = game.STATES['menu']

					elif game.state == game.STATES['play'] and not game.started: 
						game.start()

				case pygame.KEYDOWN:

					if event.key == pygame.K_ESCAPE:

						logger.info('[ESC] pressed')
							
						if game.state == game.STATES['play']: 

							if game.started and not game.paused: 
								game.paused = True

							elif game.paused: 
								game.paused = False
							
						elif game.state == game.STATES['over']:
							game.state = game.STATES['menu']

						elif game.state == game.STATES['menu']:
							game.quit()

				case game.FORK_TIMER:

					if game.state == game.STATES['play'] and game.started and not game.paused:
						
						y_offset = randint(int(HEIGHT / 3), int(HEIGHT - HEIGHT / 3))

						forks.add(
							Fork(orientation = 'up', speed = game._FORK_SPEED, offset = y_offset, game = game), 
							Fork(orientation = 'down', speed = game._FORK_SPEED, offset = y_offset, game = game)
						)

						if randint(0, game.CHILLI_FREQUENCY) == 0: 
							chillies.add(Chilli(speed = game._FORK_SPEED, y_offset = y_offset, game = game))

		# Background
		screen.fill(COLOURS['black'])
		background.draw(screen)

		if game.state == game.STATES['menu']:

			# Intro Sprites
			menu_sprites.update(dt)
			menu_sprites.draw(screen)

		elif game.state == game.STATES['choose_taco']:

			# Choose Taco Sprites
			choose_taco_sprites.update(dt)
			choose_taco_sprites.draw(screen)

			# Player
			player.sprite.costume_display()
			player.draw(screen)

		elif game.state == game.STATES['play']:

			if game.started:
			
				if not game.paused:

					# Background
					background.update(dt)

					# Forks
					forks.update(dt)
					forks.draw(screen)

					# Chillies
					chillies.update(dt)
					chillies.draw(screen)

					# Player
					player.draw(screen)
					player.update(dt)
				
				elif game.paused:

					# Player
					player.draw(screen)

					# Forks
					forks.draw(screen)

					# Chillies
					chillies.draw(screen)

					# Pause Sprites
					pause_sprites.update(dt)
					pause_sprites.draw(screen)
			
			elif not game.started:

				# Player
				player.draw(screen)

				# Forks
				forks.draw(screen)

				# Chillies
				chillies.draw(screen)

		elif game.state == game.STATES['over']:

				# Player
				player.draw(screen)

				# Forks
				forks.draw(screen)

				# Chillies
				chillies.draw(screen)

				# Game Over Sprites
				game_over_sprites.update(dt)
				game_over_sprites.draw(screen)

		# Text
		text.update()
		[screen.blit(line[0], line[1]) for line in text.texts]

		pygame.display.update()
		clock.tick(0 if VSYNC else FPS)

if __name__ == '__main__': main()
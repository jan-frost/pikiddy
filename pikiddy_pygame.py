import pygameui as ui
import pygame
import pyglet
import os
import fnmatch

import logging

PREVIOUS_SONG = "previous song",
NEXT_SONG = "next song",
PREVIOUS_ALBUM = "previous album",
NEXT_ALBUM = "next album",
TOGGLE_PAUSE = "toggle pause",
QUIT = "quit",

log_format = '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s'
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)


# os.putenv('SDL_FBDEV', '/dev/fb0')
# os.putenv('SDL_MOUSEDRV', 'TSLIB')
# os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

class AlbumScene(ui.Scene):
    def __init__(self, folder):
        ui.Scene.__init__(self)

        self.last_action = "none"
        self.on_key_up.connect(self.key_pressed)

        self.music_files = []
        for music_file in fnmatch.filter(os.listdir(folder), '*.mp3'):
            self.music_files.append(os.path.join(folder, music_file))
        self.current_track = 0
        self.player = pyglet.media.Player()

        cover_rect = pygame.Rect(75, 35, 160, 160)
        cover_file = fnmatch.filter(os.listdir(folder), 'cover.*')[0]
        img = pygame.image.load(os.path.join(folder, cover_file))
        img = pygame.transform.scale(img, (cover_rect.width, cover_rect.height))
        img_button = ui.ImageButton(cover_rect, img)
        img_button.on_clicked.connect(self.image_clicked)
        self.add_child(img_button)

        left_rect = pygame.Rect(5, 35, 65, 170)
        left_button = ui.Button(left_rect, '<')
        left_button.on_clicked.connect(self.left_clicked)
        self.add_child(left_button)

        right_rect = pygame.Rect(250, 35, 65, 170)
        right_button = ui.Button(right_rect, '>')
        right_button.on_clicked.connect(self.right_clicked)
        self.add_child(right_button)

        up_rect = pygame.Rect(75, 5, 170, 25)
        up_button = ui.Button(up_rect, '^')
        up_button.on_clicked.connect(self.up_clicked)
        self.add_child(up_button)

        down_rect = pygame.Rect(75, 210, 170, 25)
        down_button = ui.Button(down_rect, 'v')
        down_button.on_clicked.connect(self.down_clicked)
        self.add_child(down_button)

        title_rect = pygame.Rect(5, 210, 65, 25)
        self.title_label = ui.Label(title_rect, '1')
        self.add_child(self.title_label)

        total_title_rect = pygame.Rect(250, 210, 65, 25)
        total_title_label = ui.Label(total_title_rect, str(len(self.music_files)))
        self.add_child(total_title_label)

    def entered(self):
        ui.Scene.entered(self)
        self.play(self.current_track)

    def exited(self):
        ui.Scene.exited(self)
        self.pause()

    def play(self, index):
        if index < 0 or index >= len(self.music_files):
            return

        self.player.delete()
        self.player = pyglet.media.Player()
        self.player.on_player_eos = self.on_player_eos

        music_file = self.music_files[index]
        source = pyglet.media.load(music_file)
        self.player.queue(source)
        self.player.play()

    def on_player_eos(self):
        self.perform_action(NEXT_SONG)
        if self.current_track == 0:
            self.pause()

    def pause(self):
        self.player.pause()

    def toggle_pause(self):
        if self.player.playing:
            self.player.pause()
        else:
            self.player.play()

    def key_pressed(self, sender, key):
        action = {
            pygame.K_LEFT: PREVIOUS_SONG,
            pygame.K_RIGHT: NEXT_SONG,
            pygame.K_UP: PREVIOUS_ALBUM,
            pygame.K_DOWN: NEXT_ALBUM,
            pygame.K_RETURN: TOGGLE_PAUSE,
            pygame.K_ESCAPE: QUIT,
        }.get(key, 'none')
        self.perform_action(action)

    def perform_action(self, action):
        self.last_action = action
        if action == PREVIOUS_ALBUM or action == NEXT_ALBUM or action == QUIT:
            ui.scene.pop()
        elif action == NEXT_SONG:
            self.current_track += 1
            if self.current_track >= len(self.music_files):
                self.current_track = 0
            self.title_label.text = str(self.current_track + 1)
            self.play(self.current_track)
            logger.info('next song: ' + str(self.current_track))
        elif action == PREVIOUS_SONG:
            self.current_track -= 1
            if self.current_track < 0:
                self.current_track = len(self.music_files) - 1
            self.title_label.text = str(self.current_track + 1)
            self.play(self.current_track)
            logger.info('previous song: ' + str(self.current_track))
        elif action == TOGGLE_PAUSE:
            self.toggle_pause()
            logger.info('toggle pause')

    def image_clicked(self, sender, button):
        self.perform_action(TOGGLE_PAUSE)

    def left_clicked(self, sender, button):
        self.perform_action(PREVIOUS_SONG)

    def right_clicked(self, sender, button):
        self.perform_action(NEXT_SONG)

    def up_clicked(self, sender, button):
        self.perform_action(PREVIOUS_ALBUM)

    def down_clicked(self, sender, button):
        self.perform_action(NEXT_ALBUM)

    def layout(self):
        ui.Scene.layout(self)

    def update(self, dt):
        ui.Scene.update(self, dt)


class PikiddyScene(ui.Scene):
    def __init__(self, root_path):
        ui.Scene.__init__(self)

        music_folders = []
        for root, dirnames, filenames in os.walk(root_path):
            if fnmatch.filter(filenames, 'cover.*'):
                music_folders.append(root)

        self.albums = []
        for folder in music_folders:
            self.albums.append(AlbumScene(folder))
        self.current_album = 0

    def layout(self):
        ui.Scene.layout(self)

    def update(self, dt):
        ui.Scene.update(self, dt)

    def entered(self):
        ui.Scene.entered(self)

        action = self.albums[self.current_album].last_action
        if action == PREVIOUS_ALBUM:
            self.current_album -= 1
            if self.current_album < 0:
                self.current_album = len(self.albums) - 1
            logger.info('previous album: ' + str(self.current_album))
        elif action == NEXT_ALBUM:
            self.current_album += 1
            if self.current_album >= len(self.albums):
                self.current_album = 0
            logger.info('next album: ' + str(self.current_album))
        elif action == QUIT:
            logger.info('quit')
            pygame.quit()
            import sys
            sys.exit()

        ui.scene.push(self.albums[self.current_album])


if __name__ == '__main__':
    ui.init('pikiddy', (320, 240))
    pikiddy = PikiddyScene('data')
    ui.scene.push(pikiddy)
    ui.run()

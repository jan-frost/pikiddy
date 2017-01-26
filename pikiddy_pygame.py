import pygameui as ui
import pygame
import os
import fnmatch

import logging

log_format = '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s'
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

class AlbumScene(ui.Scene):
    def __init__(self, folder):
        ui.Scene.__init__(self)

        self.last_action = "none"
        self.on_key_up.connect(self.key_pressed)

        files = os.listdir(folder)
        self.album_scenes = []
        for music_file in fnmatch.filter(os.listdir(folder), '*.mp3'):
            self.album_scenes.append(os.path.join(folder, music_file))

        cover_file = fnmatch.filter(os.listdir(folder), 'cover.*')[0]
        img = pygame.image.load(os.path.join(folder, cover_file))
        img_button = ui.ImageButton(ui.window.rect, img)
        img_button.on_clicked.connect(self.image_clicked)
        self.add_child(img_button)

    def key_pressed(self, sender, key):
        action = {
            pygame.K_LEFT: "previous song",
            pygame.K_RIGHT: "next song",
            pygame.K_UP: "previous album",
            pygame.K_DOWN: "next album",
            pygame.K_RETURN: "toggle pause",
            pygame.K_ESCAPE: "quit",
        }.get(key, "none")
        self.perform_action(action)

    def perform_action(self, action):
        self.last_action = action
        ui.scene.pop()

    def image_clicked(self, sender, button):
        logger.info('clicked')

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

        self.current_album = {
            "previous album": self.current_album - 1,
            "next album": self.current_album + 1
        }.get(self.albums[self.current_album].last_action, self.current_album)

        if self.current_album >= len(self.albums):
            self.current_album = 0
        if self.current_album < 0:
            self.current_album = len(self.albums) - 1

        logger.info('current album: ' + str(self.current_album + 1))
        ui.scene.push(self.albums[self.current_album])


    def start(self):
        ui.scene.push(self.albums[self.current_album])


if __name__ == '__main__':
    ui.init('pikiddy', (320, 240))
    pikiddy = PikiddyScene('data')
    ui.scene.push(pikiddy)
    pikiddy.start()
    ui.run()

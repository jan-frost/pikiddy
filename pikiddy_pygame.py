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

class AlbumScene(ui.Scene):
    def __init__(self, folder):
        ui.Scene.__init__(self)

        files = os.listdir(folder)
        self.album_scenes = []
        for music_file in fnmatch.filter(os.listdir(folder), '*.mp3'):
            self.album_scenes.append(os.path.join(folder, music_file))

        cover_file = fnmatch.filter(os.listdir(folder), 'cover.*')[0]
        img = pygame.image.load(os.path.join(folder, cover_file))
        img_view = ui.ImageView(ui.window.rect, img)
        self.add_child(img_view)

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

    def start(self):
        ui.scene.push(self.albums[self.current_album])


if __name__ == '__main__':
    ui.init('pikiddy', (320, 240))
    pikiddy = PikiddyScene('data')
    ui.scene.push(pikiddy)
    pikiddy.start()
    ui.run()

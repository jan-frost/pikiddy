import pygameui as ui
import fnmatch
from .AlbumScene import AlbumScene
import common
from common import *


class PikiddyScene(ui.Scene):
    def __init__(self, root_path):
        ui.Scene.__init__(self)

        # add all folders that have mp3 files
        music_folders = []
        for root, dirnames, filenames in os.walk(root_path):
            if fnmatch.filter(filenames, '*.mp3'):
                music_folders.append(root)

        albums = []
        for folder in music_folders:
            albums.append(AlbumScene(folder))
        self.albums = sorted(albums, key=lambda album: album.statistics.last_played, reverse=True)
        self.current_album = 0

    def layout(self):
        ui.Scene.layout(self)

    def update(self, dt):
        ui.Scene.update(self, dt)

    def entered(self):
        ui.Scene.entered(self)

        action = self.albums[self.current_album].last_action
        if action == Actions.PREVIOUS_ALBUM:
            self.current_album -= 1
            if self.current_album < 0:
                self.current_album = len(self.albums) - 1
            logger.info('previous album: ' + str(self.current_album))
        elif action == Actions.NEXT_ALBUM:
            self.current_album += 1
            if self.current_album >= len(self.albums):
                self.current_album = 0
            logger.info('next album: ' + str(self.current_album))
        elif action == Actions.QUIT:
            logger.info('quit')
            pygame.quit()
            import sys
            sys.exit()

        if not common.EXITED:
            ui.scene.push(self.albums[self.current_album])

    def on_pygame_event(self, e):
        pass
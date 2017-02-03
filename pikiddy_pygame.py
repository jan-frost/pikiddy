import pygameui as ui
import pygame
import os
import fnmatch
import logging
import eyed3
import uuid

PREVIOUS_SONG = "previous song"
NEXT_SONG = "next song"
PREVIOUS_ALBUM = "previous album"
NEXT_ALBUM = "next album"
TOGGLE_PAUSE = "toggle pause"
QUIT = "quit"

SONG_END = pygame.USEREVENT + 1

log_format = '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s'
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))
log_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log' + str(uuid.uuid1()) + '.txt')
print 'log file: %s' % log_file
file_handler = logging.FileHandler(log_file, 'w')
file_handler.setFormatter(logging.Formatter(log_format))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)


os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/event2')
touch_scale = 1


class AlbumScene(ui.Scene):
    def __init__(self, folder):
        ui.Scene.__init__(self)

        self.last_action = "none"
        self.on_key_up.connect(self.key_pressed)

        files = sorted(os.listdir(folder))

        logger.info('add folder: ' + folder)
        self.music_files = []
        self.album_description = None
        for music_file in files:
            if music_file.endswith('.mp3'):
                logger.info('add song: ' + music_file)
                music_path = os.path.join(folder, music_file)
                self.music_files.append(music_path)
                if self.album_description is None:
                    id3 = eyed3.load(music_path)
                    self.album_description = '%s: %s' % (id3.tag.album_artist, id3.tag.album)
        self.current_track = 0
        self.current_music = None
        self.paused = False

        cover = None
        for cover_file in files:
            if cover_file.lower().endswith(('.jpg', '.jpeg', '.gif', '.png')):
                cover = os.path.join(folder, cover_file)

        self.cover_button = None
        if cover is None:
            cover_rect = pygame.Rect(175, 105, 260, 260)
            logger.info('could not find image')
            self.cover_button = ui.Button(cover_rect, self.album_description)
            self.cover_button.on_clicked.connect(self.image_clicked)
            self.add_child(self.cover_button)
        else:
            cover_rect = pygame.Rect(185, 105, 260, 260)
            logger.info('add image: ' + cover)
            img = pygame.image.load(cover)
            img = pygame.transform.scale(img, (cover_rect.width, cover_rect.height))
            img_button = ui.ImageButton(cover_rect, img)
            img_button.on_clicked.connect(self.image_clicked)
            self.add_child(img_button)

        logger.info('initialize UI')
        left_rect = pygame.Rect(5, 105, 175, 270)
        left_button = ui.Button(left_rect, '<')
        left_button.on_clicked.connect(self.left_clicked)
        self.add_child(left_button)

        right_rect = pygame.Rect(460, 105, 175, 270)
        right_button = ui.Button(right_rect, '>')
        right_button.on_clicked.connect(self.right_clicked)
        self.add_child(right_button)

        up_rect = pygame.Rect(185, 5, 270, 95)
        up_button = ui.Button(up_rect, '-')
        up_button.on_clicked.connect(self.up_clicked)
        self.add_child(up_button)

        down_rect = pygame.Rect(185, 380, 270, 95)
        down_button = ui.Button(down_rect, '+')
        down_button.on_clicked.connect(self.down_clicked)
        self.add_child(down_button)

        title_rect = pygame.Rect(5, 380, 175, 95)
        self.title_label = ui.Label(title_rect, '1')
        self.add_child(self.title_label)

        total_title_rect = pygame.Rect(460, 380, 175, 95)
        total_title_label = ui.Label(total_title_rect, str(len(self.music_files)))
        self.add_child(total_title_label)

    def entered(self):
        ui.Scene.entered(self)
        self.play(self.current_track)

    def exited(self):
        ui.Scene.exited(self)
        self.stop()

    def play(self, index):
        if index < 0 or index >= len(self.music_files) or os.name == 'nt':
            return

        self.current_music = pygame.mixer.music.load(self.music_files[index])
        pygame.mixer.music.play()
        self.paused = False

    def stop(self):
        pygame.mixer.music.stop()
        self.paused = True

    def toggle_pause(self):
        if os.name == 'nt':
            return

        if self.paused:
            if pygame.mixer.get_busy():
                logger.info('unpause music: unpause')
                pygame.mixer.music.unpause()
            else:
                logger.info('unpause music: play')
                pygame.mixer.music.play()
            self.paused = False
        else:
            logger.info('pause music')
            pygame.mixer.music.pause()
            self.paused = True

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

        if self.cover_button is not None:
            import time
            millis = int(round(time.time() * 1000))
            start_index = (millis / 300) % len(self.album_description)
            length = min(18, len(self.album_description) - 1 - start_index)
            self.cover_button.text = self.album_description[start_index:start_index+length]

    def on_pygame_event(self, e):
        if e.type == SONG_END:
            self.perform_action(NEXT_SONG)
            if self.current_track == 0:
                self.stop()


class PikiddyScene(ui.Scene):
    def __init__(self, root_path):
        ui.Scene.__init__(self)

        # add all folders that have mp3 files
        music_folders = []
        for root, dirnames, filenames in os.walk(root_path):
            if fnmatch.filter(filenames, '*.mp3'):
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

    def on_pygame_event(self, e):
        pass


if __name__ == '__main__':
    try:
        ui.init('pikiddy', (640, 480))
        pygame.mixer.music.set_endevent(SONG_END)
        if os.name != 'nt':
            pygame.mouse.set_visible(False)
            touch_scale = 640.0 / 480.0
        pikiddy = PikiddyScene(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data'))
        ui.scene.push(pikiddy)
        # ui.run()

        custom_theme = ui.theme.light_theme
        custom_theme.set(class_name='Button',
                        state='normal',
                        key='font',
                        value=ui.resource.get_font(12))
        ui.theme.use_theme(custom_theme)

        assert len(ui.scene.stack) > 0

        clock = pygame.time.Clock()
        down_in_view = None

        elapsed = 0

        while True:
            dt = clock.tick(60)

            elapsed += dt
            if elapsed > 5000:
                elapsed = 0
                logger.debug('%d FPS', clock.get_fps())

            exited = False
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exited = True
                    break

                raw_mousepoint = pygame.mouse.get_pos()
                mousepoint = (raw_mousepoint[0] * touch_scale, raw_mousepoint[1] * touch_scale)

                if e.type == pygame.MOUSEBUTTONDOWN:
                    hit_view = ui.scene.current.hit(mousepoint)
                    logger.debug('hit %s' % hit_view)
                    if (hit_view is not None and
                        not isinstance(hit_view, ui.scene.Scene)):
                        ui.focus.set(hit_view)
                        down_in_view = hit_view
                        pt = hit_view.from_window(mousepoint)
                        hit_view.mouse_down(e.button, pt)
                    else:
                        ui.focus.set(None)
                elif e.type == pygame.MOUSEBUTTONUP:
                    hit_view = ui.scene.current.hit(mousepoint)
                    if hit_view is not None:
                        if down_in_view and hit_view != down_in_view:
                            down_in_view.blurred()
                            ui.focus.set(None)
                        pt = hit_view.from_window(mousepoint)
                        hit_view.mouse_up(e.button, pt)
                    down_in_view = None
                elif e.type == pygame.MOUSEMOTION:
                    if down_in_view and down_in_view.draggable:
                        pt = down_in_view.from_window(mousepoint)
                        down_in_view.mouse_drag(pt, e.rel)
                    else:
                        ui.scene.current.mouse_motion(mousepoint)
                elif e.type == pygame.KEYDOWN:
                    if ui.focus.view:
                        ui.focus.view.key_down(e.key, e.unicode)
                    else:
                        ui.scene.current.key_down(e.key, e.unicode)
                elif e.type == pygame.KEYUP:
                    if ui.focus.view:
                        ui.focus.view.key_up(e.key)
                    else:
                        ui.scene.current.key_up(e.key)
                else:
                    ui.scene.current.on_pygame_event(e)

            if exited:
                break

            ui.scene.current.update(dt / 1000.0)
            ui.scene.current.draw()
            ui.window_surface.blit(ui.scene.current.surface, (0, 0))
            pygame.display.flip()
    except:
        # see: http://stackoverflow.com/questions/3702675/how-to-print-the-full-traceback-without-halting-the-program#3702847
        import sys
        ex = sys.exc_info()
        logger.exception(ex)

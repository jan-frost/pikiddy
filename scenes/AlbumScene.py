import pygameui as ui
import eyed3
from threading import Timer
import json
from common import *


class Statistics:
    def __init__(self):
        self.current_song = 0
        self.current_song_position = 0.0
        self.last_played = 0.0

    @classmethod
    def fromjson(cls, json_string):
        statistics = cls()
        statistics.__dict__ = json.loads(json_string)
        return statistics


class AlbumScene(ui.Scene):
    def __init__(self, folder):
        ui.Scene.__init__(self)

        self.statistics = Statistics()
        self.statistics_file = os.path.join(folder, 'statistics.json')
        if os.path.exists(self.statistics_file):
            with open(self.statistics_file, 'r') as file_stream:
                statistics_json = file_stream.read()
                self.statistics = Statistics.fromjson(statistics_json)
        self.timer = None
        self.start_pos_sec = 0.0

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
        self.current_track = self.statistics.current_song
        self.current_music = None
        self.state = 'stopped'

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
        self.play(self.current_track, self.statistics.current_song_position / 1000.0)
        self.timer = Timer(5.0, self.write_statistics)
        self.timer.start()

    def exited(self):
        ui.Scene.exited(self)
        self.stop()
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None

    def write_statistics(self):
        logger.info('write statistics')
        self.statistics.current_song = self.current_track
        if os.name is not 'nt':
            self.statistics.current_song_position = 1000.0 * self.start_pos_sec + pygame.mixer.music.get_pos()
        else:
            self.statistics.current_song_position = 0.0
        self.statistics.last_played = utc_time()
        statistics_json = json.dumps(self.statistics, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        with open(self.statistics_file, 'w') as file_stream:
            file_stream.write(statistics_json)
        self.timer.run()

    def play(self, index, start_pos=0.0):
        self.state = 'playing'
        if index < 0 or index >= len(self.music_files) or os.name == 'nt':
            return

        self.current_music = pygame.mixer.music.load(self.music_files[index])
        self.start_pos_sec = start_pos
        pygame.mixer.music.play(start=start_pos)

    def stop(self):
        self.state = 'stopped'
        if os.name != 'nt':
            pygame.mixer.music.stop()

    def pause(self):
        self.state = 'paused'
        if os.name != 'nt':
            pygame.mixer.music.unpause()

    def unpause(self):
        self.state = 'playing'
        if os.name != 'nt':
            pygame.mixer.music.pause()

    def toggle_pause(self):
        if self.state == 'stopped':
            logger.info('toggle pause: play')
            self.play(self.current_track)
        elif self.state == 'paused':
            logger.info('toggle pause: unpause')
            self.unpause()
        elif self.state == 'playing':
            logger.info('toggle pause: pause')
            self.pause()

    def key_pressed(self, sender, key):
        action = {
            pygame.K_LEFT: Actions.PREVIOUS_SONG,
            pygame.K_RIGHT: Actions.NEXT_SONG,
            pygame.K_UP: Actions.PREVIOUS_ALBUM,
            pygame.K_DOWN: Actions.NEXT_ALBUM,
            pygame.K_RETURN: Actions.TOGGLE_PAUSE,
            pygame.K_ESCAPE: Actions.QUIT,
        }.get(key, 'none')
        self.perform_action(action)

    def perform_action(self, action):
        self.last_action = action
        if action == Actions.PREVIOUS_ALBUM or action == Actions.NEXT_ALBUM or action == Actions.QUIT:
            ui.scene.pop()
        elif action == Actions.NEXT_SONG:
            self.current_track += 1
            if self.current_track >= len(self.music_files):
                self.current_track = 0
            self.title_label.text = str(self.current_track + 1)
            self.play(self.current_track)
            logger.info('next song: ' + str(self.current_track))
        elif action == Actions.PREVIOUS_SONG:
            if os.name is 'nt' or pygame.mixer.music.get_pos() < 5000.0:
                self.current_track -= 1
                if self.current_track < 0:
                    self.current_track = len(self.music_files) - 1
                self.title_label.text = str(self.current_track + 1)
            self.play(self.current_track)
            logger.info('previous song: ' + str(self.current_track))
        elif action == Actions.TOGGLE_PAUSE:
            self.toggle_pause()

    def image_clicked(self, sender, button):
        self.perform_action(Actions.TOGGLE_PAUSE)

    def left_clicked(self, sender, button):
        self.perform_action(Actions.PREVIOUS_SONG)

    def right_clicked(self, sender, button):
        self.perform_action(Actions.NEXT_SONG)

    def up_clicked(self, sender, button):
        self.perform_action(Actions.PREVIOUS_ALBUM)

    def down_clicked(self, sender, button):
        self.perform_action(Actions.NEXT_ALBUM)

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
            self.perform_action(Actions.NEXT_SONG)
            if self.current_track == 0:
                self.stop()
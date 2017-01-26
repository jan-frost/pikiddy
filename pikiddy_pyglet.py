import os
import fnmatch
import pyglet
from pyglet.window import key


class Album:
    def __init__(self, folder, screen_width, screen_height, width, height):
        self.width = screen_width
        self.height = screen_height
        self.image = pyglet.image.load(os.path.join(folder, 'cover.jpg'))
        self.color_sprite = pyglet.sprite.Sprite(self.image, x=0, y=0)
        self.color_sprite.scale = min(width / self.image.width, height / self.image.height)
        self.color_sprite.set_position(0.5 * (screen_width - self.color_sprite.scale * self.image.width),
                                       0.5 * (screen_height - self.color_sprite.scale * self.image.height))

        files = os.listdir(folder)
        self.music_files = []
        for music_file in fnmatch.filter(os.listdir(folder), '*.mp3'):
            self.music_files.append(os.path.join(folder, music_file))

        self.player = pyglet.media.Player()
        self.current_track = 0

    def start(self):
        self.load(self.current_track)

    def pause(self):
        self.player.pause()

    def toggle_pause(self):
        if self.player.playing:
            self.player.pause()
        else:
            self.player.play()

    def load(self, index):
        self.player.delete()
        self.player = pyglet.media.Player()
        self.player.on_player_eos = self.on_player_eos

        music_file = self.music_files[index]
        source = pyglet.media.load(music_file)
        source_group = pyglet.media.SourceGroup(source.audio_format, None)
        source_group.queue(source)
        self.player.queue(source_group)
        self.player.play()

    def on_player_eos(self):
        self.current_track += 1
        if self.current_track >= len(self.music_files):
            self.current_track = 0
        else:
            self.load(self.current_track)

    def unload(self):
        self.player.delete()

    def skip_forward(self):
        self.current_track += 1
        if self.current_track >= len(self.music_files):
            self.current_track = 0
        self.load(self.current_track)

    def skip_backward(self):
        self.current_track -= 1
        if self.current_track < 0:
            self.current_track = len(self.music_files) - 1
        self.load(self.current_track)

    def render(self, album_index, total_albums):
        self.color_sprite.draw()
        pyglet.graphics.draw_indexed(3, pyglet.gl.GL_TRIANGLES, [0, 1, 2],
                                     ('v2f', (0.05 * self.width, 0.50 * self.height,
                                              0.15 * self.width, 0.20 * self.height,
                                              0.15 * self.width, 0.80 * self.height)),
                                     ('c3B', (0, 0, 255) * 3))
        pyglet.graphics.draw_indexed(3, pyglet.gl.GL_TRIANGLES, [0, 1, 2],
                                     ('v2f', (0.95 * self.width, 0.50 * self.height,
                                              0.85 * self.width, 0.20 * self.height,
                                              0.85 * self.width, 0.80 * self.height)),
                                     ('c3B', (0, 0, 255) * 3))
        pyglet.graphics.draw_indexed(3, pyglet.gl.GL_TRIANGLES, [0, 1, 2],
                                     ('v2f', (0.50 * self.width, 0.05 * self.height,
                                              0.20 * self.width, 0.15 * self.height,
                                              0.80 * self.width, 0.15 * self.height)),
                                     ('c3B', (0, 255, 0) * 3))
        pyglet.graphics.draw_indexed(3, pyglet.gl.GL_TRIANGLES, [0, 1, 2],
                                     ('v2f', (0.50 * self.width, 0.95 * self.height,
                                              0.20 * self.width, 0.85 * self.height,
                                              0.80 * self.width, 0.85 * self.height)),
                                     ('c3B', (0, 255, 0) * 3))
        label = pyglet.text.Label(str(self.current_track + 1),
                                  font_name='Arial',
                                  font_size=0.08*self.height,
                                  x=0.11*self.width, y=0.5*self.height,
                                  anchor_x='center', anchor_y='center')
        label.draw()
        label = pyglet.text.Label(str(len(self.music_files)),
                                  font_name='Arial',
                                  font_size=0.08*self.height,
                                  x=0.89*self.width, y=0.5*self.height,
                                  anchor_x='center', anchor_y='center')
        label.draw()
        label = pyglet.text.Label(str(album_index + 1),
                                  font_name='Arial',
                                  font_size=0.06*self.height,
                                  x=0.5*self.width, y=0.89*self.height,
                                  anchor_x='center', anchor_y='center')
        label.draw()
        label = pyglet.text.Label(str(total_albums),
                                  font_name='Arial',
                                  font_size=0.06*self.height,
                                  x=0.5*self.width, y=0.11*self.height,
                                  anchor_x='center', anchor_y='center')
        label.draw()


class Pikiddy:
    def __init__(self, path):
        music_folders = []
        for root, dirnames, filenames in os.walk(path):
            if fnmatch.filter(filenames, 'cover.jpg'):
                music_folders.append(root)

        self.window = pyglet.window.Window()
        width = self.window.screen.width
        height = self.window.screen.height
        self.window.set_size(width, height)
        self.window.set_fullscreen(True)
        self.window.set_mouse_visible(True)

        self.albums = []
        for folder in music_folders:
            self.albums.append(Album(folder, width, height, 0.6*width, 0.6*height))
        self.current_album = 0
        self.albums[self.current_album].start()

        pyglet.gl.glClearColor(0, 0, 0, 1)
        self.window.on_draw = self.on_draw
        self.window.on_key_press = self.on_key_press
        self.window.on_mouse_press = self.on_mouse_press

    def on_draw(self):
        self.window.clear()
        self.albums[self.current_album].render(self.current_album, len(self.albums))

    def on_key_press(self, symbol, modifiers):
        if symbol == key.LEFT:
            self.albums[self.current_album].skip_backward()
        if symbol == key.RIGHT:
            self.albums[self.current_album].skip_forward()
        if symbol == key.UP:
            self.albums[self.current_album].pause()
            self.current_album -= 1
            if self.current_album < 0:
                self.current_album = len(self.albums) - 1
            self.albums[self.current_album].start()
        if symbol == key.DOWN:
            self.albums[self.current_album].pause()
            self.current_album += 1
            if self.current_album >= len(self.albums):
                self.current_album = 0
            self.albums[self.current_album].start()
        if symbol == key.ENTER:
            self.albums[self.current_album].toggle_pause()
        if symbol == key.ESCAPE:
            self.window.close()

    def on_mouse_press(self, x, y, button, modifiers):
        # left/right will go to the next file
        # up/down will go to the next folder
        # top-right/top-left will change volume
        # bottom-right/bottom-left shows current/total tracks
        # click on the image will pause
        w = self.window.width
        h = self.window.height
        if x < 0.2*w and 0.2*h < y < 0.8*h:
            self.albums[self.current_album].skip_backward()
        if x > 0.8*w and 0.2*h < y < 0.8*h:
            self.albums[self.current_album].skip_forward()
        if 0.2*w < x < 0.8*w and y > 0.8*h:
            self.albums[self.current_album].pause()
            self.current_album -= 1
            if self.current_album < 0:
                self.current_album = len(self.albums) - 1
            self.albums[self.current_album].start()
        if 0.2*w < x < 0.8*w and y < 0.2*h:
            self.albums[self.current_album].pause()
            self.current_album += 1
            if self.current_album >= len(self.albums):
                self.current_album = 0
            self.albums[self.current_album].start()
        if 0.2*w < x < 0.8*w and 0.2*h < y < 0.8*h:
            self.albums[self.current_album].toggle_pause()
        if x > 0.9*w and y > 0.9*h:
            self.window.close()
        return True

if __name__ == '__main__':
    root_folder = 'data'
    pikiddy = Pikiddy(root_folder)
    pyglet.app.run()

    # last track for each album is stored on disk
    print "exit"

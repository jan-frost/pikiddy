import pygameui as ui
from scenes.PikiddyScene import PikiddyScene
import common
from common import *


os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
touch_scale_x = 1.0
touch_scale_y = 1.0


if __name__ == '__main__':
    window_size = (640, 480)
    name = 'pikiddy'
    logger.debug('pygame %s' % pygame.__version__)

    try:
        pygame.init()
        # pygame.key.set_repeat(200, 50)
        ui.window_surface = pygame.display.set_mode(window_size)
        pygame.display.set_caption(name)
        ui.window.rect = pygame.Rect((0, 0), window_size)
        ui.theme.init()

        pygame.mixer.music.set_endevent(SONG_END)
        if os.name != 'nt':
            pygame.mouse.set_visible(False)
            touch_scale_x = 640.0 / 480.0
            touch_scale_y = 480.0 / 320.0
        pikiddy = PikiddyScene(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data'))
        ui.scene.push(pikiddy)

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

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    common.EXITED = True
                    ui.scene.pop()
                    pygame.quit()
                    break

                raw_mousepoint = pygame.mouse.get_pos()
                mousepoint = (raw_mousepoint[0] * touch_scale_x, raw_mousepoint[1] * touch_scale_y)

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

            if common.EXITED:
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

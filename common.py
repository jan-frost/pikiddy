import pygame
import datetime
import logging
import os

def utc_time():
    epoch = datetime.datetime.utcfromtimestamp(0)
    now = datetime.datetime.utcnow()
    return int((now - epoch).total_seconds() * 1000.0)


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


Actions = enum(
    'PREVIOUS_SONG',
    'NEXT_SONG',
    'PREVIOUS_ALBUM',
    'NEXT_ALBUM',
    'TOGGLE_PAUSE',
    'QUIT'
)

SONG_END = pygame.USEREVENT + 1

log_format = '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s'
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))
log_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log.txt')
print 'log file: %s' % log_file
file_handler = logging.FileHandler(log_file, 'w')
file_handler.setFormatter(logging.Formatter(log_format))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

EXITED = False
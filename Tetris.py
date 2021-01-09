import subprocess
import sys


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


try:
    import pygame
    import random
except ImportError:
    install("pygame")
    install("random")
    import pygame
    import random

"""
Following this guide:
```youtube.com/watch?v=zfvxp7PgQ6c```

10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""

pygame.font.init()

SONG_END = pygame.USEREVENT + 1

s_width = 800
s_height = 700
game_width = 10
game_height = 20
block_size = 30
play_width = game_width*block_size
play_height = game_height*block_size
max_fall_rate = 8

def scale_arr(arr, scaling):
    return list(map(lambda x: int(x*scaling), arr))


image0 = pygame.image.load(r'Images/blackhole.png')
image0 = pygame.transform.scale(image0, scale_arr(image0.get_rect().size, 1.5))


image1 = pygame.image.load(r'Images/randomimage.webp')
image1 = pygame.transform.scale(image1, scale_arr(image1.get_rect().size, 1.6))


_images = [image0, image1]

_songs = [r"Songs/Tetris.mp3"]


def show_next_image():
    global _images
    if len(_images) <= 1:
        return
    _images = _images[1:] + [_images[0]]


def play_next_song():
    global _songs
    if len(_songs) > 1:
        _songs = _songs[1:] + [_songs[0]]
    pygame.mixer.music.load(_songs[0])
    pygame.mixer.music.play()


pygame.mixer.init()
pygame.mixer.music.set_endevent(SONG_END)

pygame.mixer.music.load(r"Songs/Tetris.mp3")
pygame.mixer.music.play()


top_left_x = (s_width-play_width)//2
top_left_y = s_height-play_height

# SHAPE FORMATS

S = [['.....',
      '......',
      '..00..',
      '.00...',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


# index 0 - 6 represent shape


class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_positions = {}):
    grid = [[(0, 0, 0) for i in range(game_width)] for j in range(game_height)]

    for i in range(game_height):
        for j in range(game_width):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c

    return grid


def convert_shape_format(shape):
    positions = []
    format_mod = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format_mod):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


def check_lost(locked_positions):
    for pos in locked_positions:
        x,y = pos
        if y < 0:
            print(x,y)
            return True

    return False


def get_shape():
    return Piece(game_width//2, 0, random.choice(shapes))


def draw_text_middle(text, size, color, surface):
    pass


def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128,128,128), (sx, sy + i*block_size), (sx + play_width, sy + i*block_size))
        for j in range(len(grid[0])):
            pygame.draw.line(surface, (128,128,128), (sx + j*block_size, sy), (sx + j*block_size, sy + play_height))


def draw_window(surface, grid, score=0):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render("Best Tetris Game", 1, (255, 255, 255))

    surface.blit(_images[0], (0, 0))
    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), 30))

    font = pygame.font.SysFont('comicsans', 50)
    label = font.render('Score: ' + str(score), 1, (255, 255, 255))

    sx = top_left_x+play_width+50
    sy = top_left_y+play_height/2-300

    surface.blit(label, (sx - 30, sy))

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == (0, 0, 0):
                continue
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 4)

    draw_grid(surface, grid)


def clear_rows(grid, locked):
    inc = 0
    flag = False
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if flag and (0, 0, 0) in row:
            break
        if (0, 0, 0) not in row:
            flag = True
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]

                except KeyError:
                    continue

    if inc > 0:
        for key in sorted(list(locked), key = lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape:', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 200
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + (i+1)*block_size, block_size, block_size), 0)

    surface.blit(label, (sx, sy))


def main(win):

    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    level_time = 0

    #in seconds
    fall_speed = 0.4

    score = 0
    score_dict = {0: 0, 1: 100, 2: 250, 3: 500, 4: 800}
    slowtick = 0



    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        slowtick = (slowtick+1) % 3

        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid) and current_piece.y > 0):
                current_piece.y -= 1
                change_piece = True

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_DOWN] and slowtick == 0:
            current_piece.y += 1
            if not (valid_space(current_piece, grid)):
                current_piece.y -= 1

        for event in pygame.event.get():

            if event.type == SONG_END:
                print("the song ended!")
                play_next_song()

            if event.type == pygame.QUIT:
                print("YOU QUIT")
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1

                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x -= 1

                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.rotation -= 1




        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:

            show_next_image()
            change_piece = False
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            for _ in range(4):
                score += score_dict[clear_rows(grid, locked_positions)]
                grid = create_grid(locked_positions)

            if fall_speed > 1.0/max_fall_rate:
                fall_speed *= 0.90

        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            print("YOU LOST")
            run = False
            pygame.display.quit()


def main_menu(win):
    main(win)


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')
main_menu(win)

import pygame
import sys
from random import randrange as rand

# Score- und Name-Variablen hinzufügen
score = 0
player_name = ""
last_highscore_name = ""

# Score erhöhen
def increase_score():
    global score
    score += 1

# Funktion zum Speichern und Anzeigen des Highscores
def update_highscore():
    highscore_file = "highscore.txt"
    highscore = 0

    # Highscore aus der Datei lesen
    try:
        with open(highscore_file, 'r') as file:
            highscore = int(file.read())
    except FileNotFoundError:
        pass

    # Aktuellen Score mit Highscore vergleichen und ggf. aktualisieren
    if score > highscore:
        highscore = score
        with open(highscore_file, 'w') as file:
            file.write(str(highscore))
        global last_highscore_name
        last_highscore_name = player_name

    # Highscore im Spiel anzeigen
    font = pygame.font.Font(None, 36)
    text = font.render("Highscore: " + str(highscore), True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20))
    screen.blit(text, text_rect)

# Funktion zur Namenseingabe
def enter_name():
    global player_name
    player_name = input("Bitte geben Sie Ihren Namen ein: ")

# Konfiguration
config = {
    'cell_size': 40,  # Größe
    'cols': 8,
    'rows': 16,
    'delay': 750,
    'maxfps': 30
}

colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 150, 0),
    (0, 0, 255),
    (255, 120, 0),
    (255, 255, 0),
    (180, 0, 255),
    (0, 220, 220)
]

# Define the shapes of the single parts
tetris_shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]


def rotate_clockwise(shape):
    return [[shape[y][x]
             for y in range(len(shape))]
            for x in range(len(shape[0]) - 1, -1, -1)]


def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            if cell:
                try:
                    if board[cy + off_y][cx + off_x]:
                        return True
                except IndexError:
                    return True
    return False


def remove_row(board, row):
    del board[row]
    return [[0 for i in range(config['cols'])]] + board


def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1


def new_board():
    board = [[0 for x in range(config['cols'])]
             for y in range(config['rows'])]
    board += [[1 for x in range(config['cols'])]]
    return board


class TetrisApp(object):
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(250, 25)
        self.width = config['cell_size'] * config['cols']
        self.height = config['cell_size'] * config['rows']

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.event.set_blocked(pygame.MOUSEMOTION)  # We do not need
        # mouse movement
        # events, so we
        # block them.
        self.init_game()

    def new_stone(self):
        self.stone = tetris_shapes[rand(len(tetris_shapes))]
        self.stone_x = int(config['cols'] / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0

        if check_collision(self.board,
                           self.stone,
                           (self.stone_x, self.stone_y)):
            self.gameover = True

    def init_game(self):
        self.board = new_board()
        self.new_stone()

    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image = pygame.font.Font(
                pygame.font.get_default_font(), 12).render(
                line, False, (255, 255, 255), (0, 0, 0))

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(msg_image, (
                self.width // 2 - msgim_center_x,
                self.height // 2 - msgim_center_y + i * 22))

    def draw_matrix(self, matrix, offset):
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        self.screen,
                        colors[val],
                        pygame.Rect(
                            (off_x + x) *
                            config['cell_size'],
                            (off_y + y) *
                            config['cell_size'],
                            config['cell_size'],
                            config['cell_size']), 0)

    def move(self, delta_x):
        if not self.gameover and not self.paused:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > config['cols'] - len(self.stone[0]):
                new_x = config['cols'] - len(self.stone[0])
            if not check_collision(self.board,
                                   self.stone,
                                   (new_x, self.stone_y)):
                self.stone_x = new_x

    def quit(self):
        self.center_msg("Exiting...")
        pygame.display.update()
        sys.exit()

    def drop(self):
        if not self.gameover and not self.paused:
            self.stone_y += 1
            if check_collision(self.board,
                               self.stone,
                               (self.stone_x, self.stone_y)):
                self.board = join_matrixes(
                    self.board,
                    self.stone,
                    (self.stone_x, self.stone_y))
                self.new_stone()
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = remove_row(
                                self.board, i)
                            increase_score()  # Score erhöhen
                            break
                    else:
                        break

    def rotate_stone(self):
        if not self.gameover and not self.paused:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board,
                                   new_stone,
                                   (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def toggle_pause(self):
        self.paused = not self.paused

    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def run(self):
        key_actions = {
            'ESCAPE': self.quit,
            'LEFT': lambda: self.move(-1),
            'RIGHT': lambda: self.move(+1),
            'DOWN': self.drop,
            'UP': self.rotate_stone,
            'p': self.toggle_pause,
            'SPACE': self.start_game
        }

        self.gameover = False
        self.paused = False

        pygame.time.set_timer(pygame.USEREVENT + 1, config['delay'])
        dont_burn_my_cpu = pygame.time.Clock()
        while 1:
            self.screen.fill((0, 0, 0))
            if self.gameover:
                self.center_msg("""Game Over!
Press space to continue""")
                update_highscore()  # Highscore aktualisieren und im Spiel anzeigen

                # Punktestand mit Name speichern
                score_file = "scores.txt"
                with open(score_file, 'a') as file:
                    file.write(f"{player_name}: {score}\n")

                pygame.display.update()
                pygame.time.wait(1000)  # 1 Sekunde warten

                enter_name()  # Namenseingabe

                self.init_game()  # Neues Spiel starten

            else:
                if self.paused:
                    self.center_msg("Paused")
                else:
                    self.draw_matrix(self.board, (0, 0))
                    self.draw_matrix(self.stone,
                                     (self.stone_x,
                                      self.stone_y))
                    update_highscore()  # Highscore anzeigen

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.drop()
                elif event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_"
                                             + key):
                            key_actions[key]()

            dont_burn_my_cpu.tick(config['maxfps'])


# Starten des Spiels
if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Tetris')
    screen = pygame.display.set_mode((1000, 800)) # fenstergröße
    clock = pygame.time.Clock()

    enter_name()  # Namenseingabe

    App = TetrisApp()
    App.run()

    pygame.quit()

print("Der letzte Spieler mit dem höchsten Highscore ist:", last_highscore_name)

import pygame
import random
from queue import PriorityQueue

WIDTH = 800
ROWS = 10
BLOCK_SIZE = WIDTH // ROWS

SPEED = 10
BODY_PARTS = 3

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (1, 50, 32)
BLACK = (0, 0, 0)

pygame.init()
WIN = pygame.display.set_mode((WIDTH, WIDTH))


class Spot:
    def __init__(self, row, col, block_size, total_rows):
        self.row = row
        self.col = col
        self.x = row * block_size
        self.y = col * block_size
        self.color = BLACK
        self.neighbors = []
        self.block_size = block_size
        self.width = WIDTH
        self.total_rows = total_rows
        self.g_score = float('inf')
        self.f_score = float('inf')

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.block_size, self.block_size))

    def make_grid(self, rows, width):
        grid = []
        for i in range(rows):
            grid.append([])
            for j in range(rows):
                spot = Spot(i, j, self.block_size, rows)
                grid[i].append(spot)

        return grid

    def draw_grid(self, win, rows, width):
        gap = width // rows
        for i in range(rows):
            pygame.draw.line(win, BLACK, (0, i * gap), (width, i * gap))
            for j in range(rows):
                pygame.draw.line(win, BLACK, (j * gap, 0), (j * gap, width))

    def update_ui(self, win, grid, rows, width):
        win.fill(BLACK)

        for row in grid:
            for spot in row:
                spot.draw(win)

        self.draw_grid(win, rows, width)

    def get_neighbors(self, grid, snake_coordinates):
        self.neighbors = []
        for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:  # Down, Up, Right, Left
            row, col = self.row + direction[0], self.col + direction[1]
            if 0 <= row < self.total_rows and 0 <= col < self.total_rows:
                if [row, col] not in snake_coordinates:
                    self.neighbors.append(grid[row][col])
        return self.neighbors

    def get_spot(self, grid, coordinates):
        x, y = coordinates
        row = x // self.block_size
        col = y // self.block_size
        return grid[row][col]

    def __lt__(self, other):
        return self.f_score < other.f_score


class Algorithm(Spot):
    def __init__(self, row, col, block_size, total_rows):
        super().__init__(row, col, block_size, total_rows)
        self.grid = self.make_grid(ROWS, BLOCK_SIZE)

    def h(self, p1, p2):
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        return abs(x1 - x2) + abs(y1 - y2)

    def astar(self):
        open = PriorityQueue()

        end = self.get_spot(self.grid, snake.food)

        for row in self.grid:
            for spot in row:
                spot.g_score = float('inf')
        start = self.get_spot(self.grid, snake.coordinates[0])
        start.g_score = 0

        for row in self.grid:
            for spot in row:
                spot.f_score = float('inf')
        start.f_score = self.h(start, end)

        open.put((self.grid[0][0].f_score, self.h(start, end), start))

        aPath = {(start.row, start.col): None}

        while not open.empty():
            curr_cell = open.get()[2]
            if curr_cell == end:
                break

            curr_cell.get_neighbors(self.grid, snake.coordinates)
            print(curr_cell.get_neighbors(self.grid, snake.coordinates))
            for neighbor in curr_cell.neighbors:
                temp_g_score = curr_cell.g_score + 1
                temp_f_score = temp_g_score + self.h(neighbor, end)

                if temp_f_score < neighbor.f_score:
                    neighbor.g_score = temp_g_score
                    neighbor.f_score = temp_f_score
                    open.put((neighbor.f_score, self.h(neighbor, end), neighbor))
                    aPath[(neighbor.row, neighbor.col)] = curr_cell

        fwd_path = {}
        while end != start:
            if (end.row, end.col) in aPath:
                fwd_path[aPath[(end.row, end.col)]] = end
                end = aPath[(end.row, end.col)]
            else:
                break
        return fwd_path


class SnakeGame:
    def __init__(self, WIN):
        self.body_size = BODY_PARTS
        self.coordinates = []
        self.head = [0, 0]
        self.squares = []
        self.color = GREEN
        self.win = WIN
        self.food = None

        for i in range(BODY_PARTS - 1, -1, -1):
            self.coordinates.append([i * BLOCK_SIZE, 0])
        self.place_food()

    def draw_snake(self):
        self.squares = []
        for coord in self.coordinates:
            snake_x, snake_y = coord
            if coord == self.head:
                square = pygame.draw.rect(self.win, WHITE, (snake_x, snake_y, BLOCK_SIZE, BLOCK_SIZE))
            else:
                square = pygame.draw.rect(self.win, self.color, (snake_x, snake_y, BLOCK_SIZE, BLOCK_SIZE))
            self.squares.append(square)

    def place_food(self):
        while True:
            food_x = random.randint(0, ROWS - 1) * BLOCK_SIZE
            food_y = random.randint(0, ROWS - 1) * BLOCK_SIZE
            if (food_x, food_y) not in self.coordinates:
                self.food = (food_x, food_y)
                break

    def draw_food(self):
        if self.food:
            pygame.draw.rect(self.win, RED, (self.food[0], self.food[1], BLOCK_SIZE, BLOCK_SIZE))

    def move(self, fwd_path):
        if not fwd_path:
            return
        first_key, next_spot = next(iter(fwd_path.items()))
        self.head = self.coordinates[0][:]

        if next_spot.col > first_key.col:  # LEFT
            self.head[1] += BLOCK_SIZE
        elif next_spot.col < first_key.col:  # RIGHT
            self.head[1] -= BLOCK_SIZE
        elif next_spot.row > first_key.row:  # DOWN
            self.head[0] += BLOCK_SIZE
        elif next_spot.row < first_key.row:  # UP
            self.head[0] -= BLOCK_SIZE

        self.coordinates.insert(0, self.head[:])
        del fwd_path[first_key]
        self.draw_snake()


snake = SnakeGame(WIN)
algorithm = Algorithm(0, 0, BLOCK_SIZE, ROWS)
spot = Spot(0, 0, BLOCK_SIZE, ROWS)
grid = spot.make_grid(ROWS, WIDTH)
spot.update_ui(WIN, grid, ROWS, WIDTH)
pygame.display.update()
fwd_path = algorithm.astar()
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    if snake.head == list(snake.food):
        snake.place_food()
        fwd_path = algorithm.astar()
        snake.move(fwd_path)
    else:
        del snake.coordinates[-1]

    spot.update_ui(WIN, grid, ROWS, WIDTH)
    snake.draw_food()
    snake.draw_snake() #tteste23
    pygame.display.update()
    snake.move(fwd_path)
    clock.tick(SPEED)
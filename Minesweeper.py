import pygame as pg
import random as rd
import numpy as np

pg.init()

# GAME CONSTANTS
FRAMERATE = 60
SCALE = 40
WIDTH = 10
HEIGHT = 10
N = WIDTH * HEIGHT // 10

COLORS = {
	"BL": (48, 123, 242),  # blue
	"GR": (51, 150, 36),   # green
	"RD": (217, 7, 35),    # red
	"DB": (0, 9, 128),     # dark blue
	"DR": (97, 0, 6),      # dark red
	"CY": (22, 224, 221),  # cyan
	"BK": (0, 0, 0),       # black
	"YL": (229, 232, 37),  # yellow
	"LG": (250, 250, 250), # light grey
	"GY": (200, 200, 200), # grey
	"DG": (130, 130, 130), # dark grey
}

# MOUSE CONSTANTS
LEFT_CLICK = 1
RIGHT_CLICK = 3

# STATE CONSTANTS
HIDDEN = 0
REVEALED_NOT_DRAWN = 1
REVEALED = 2
FLAG_NOT_DRAWN = 3
FLAG = 4

MINE = 9

class MinesweeperGame:

	def __init__(self, w, h, s, n):
		self.dw = w * s
		self.dh = h * s
		self.gw = w
		self.gh = h
		self.gs = s
		self.nm = n
		self.map = np.zeros((w, h))
		self.revealed = np.zeros((w, h))
	
	def play(self):
		self.Main()

	def Main(self):
		window = pg.display.set_mode((self.dw, self.dh))
		windowclock = pg.time.Clock()

		running = True

		window.fill(self.get_color("DG"))
		self.init_map()

		while running:
			
			for event in pg.event.get():
				if event.type == pg.MOUSEBUTTONDOWN:
					mouse_d = pg.mouse.get_pos()
				elif event.type == pg.MOUSEBUTTONUP:
					mouse_u = pg.mouse.get_pos()
					clicked_cell = self.is_same_cell(mouse_d, mouse_u)
					if clicked_cell:
						if event.button == LEFT_CLICK:
							self.reveal_cell(clicked_cell, True)
						if event.button == RIGHT_CLICK:
							self.flag_cell(clicked_cell)

				if event.type == pg.QUIT:
					running = False

			self.draw_board(window)

			pg.display.flip()
			windowclock.tick(FRAMERATE)
		pg.quit()

	def draw_board(self, window):
		for i in range(self.gw):
			for j in range(self.gh):
				if self.revealed[i, j] == REVEALED_NOT_DRAWN:
					self.draw_uncovered_cell(window, i, j, self.gs)
					self.revealed[i, j] = REVEALED
				elif self.revealed[i, j] == FLAG_NOT_DRAWN:
					self.draw_flagged_cell(window, i, j, self.gs)
					self.revealed[i, j] = FLAG
				elif self.revealed[i, j] == HIDDEN:	
					self.draw_covered_cell(window, i, j, self.gs)

	def draw_uncovered_cell(self, window, i, j, l):
		x = i * l
		y = j * l

		pg.draw.polygon(surface = window, color = self.get_color("DG"), points = ((x, y),
																																							(x + l, y),
																																							(x + l, y + l),
																																							(x, y + l)))

		pg.draw.polygon(surface = window, color = self.get_color("GY"), points = ((x + l / 20, y + l / 20),
																																							(x + l, y + l / 20),
																																							(x + l, y + l),
																																							(x + l / 20, y + l)))

		self.draw_hint(window, i, j, l, self.map[i, j])

	def draw_hint(self, window, i, j, l, n):
		x = i * l
		y = j * l

		if n:
			font = pg.font.SysFont('arial', self.gs // 4 * 3)
			text = font.render(f'{int(n)}', True, self.get_color(int(n)))
			text_rect = text.get_rect()
			window.blit(text, text_rect.move(x + (l - text_rect.width) / 2, y + (l - text_rect.height) / 2))

	def draw_flagged_cell(self, window, i, j, l):
		x = i * l
		y = j * l

		font = pg.font.SysFont('arial', self.gs // 4 * 3)
		text = font.render('F', True, self.get_color("RD"))
		text_rect = text.get_rect()
		window.blit(text, text_rect.move(x + (l - text_rect.width) / 2, y + (l - text_rect.height) / 2))

	def draw_covered_cell(self, window, i, j, l):
		x = i * l
		y = j * l

		pg.draw.polygon(surface = window, color = self.get_color("LG"), points = ((x, y), (x + l, y), (x, y + l)))
		pg.draw.polygon(surface = window, color = self.get_color("GY"), points = ((x + l / 8, y + l / 8),
																																							(x + 7 * l / 8, y + l / 8),
																																							(x + 7 * l / 8, y + 7 * l / 8),
																																							(x + l / 8, y + 7 * l / 8)))

	def init_map(self):
		mines = self.init_mines()
		self.map = self.init_hints(mines) + mines

	def init_mines(self):
		mines = np.zeros((self.gw, self.gh))
		mines_list = rd.sample(range(self.gw * self.gh), self.nm)
		x = [m % self.gw for m in mines_list]
		y = [m // self.gw for m in mines_list]
		mines[(x, y)] = MINE
		return mines

	def init_hints(self, mines):
		hints = np.zeros((self.gw, self.gh))
		for i in range(len(mines)):
			for j in range(len(mines[0])):
				if mines[i, j] == 0:
					for x in range(-1, 2):
						for y in range(-1, 2):
							if (i + x >= 0 and j + y >= 0 and
									i + x < self.gw and y + j < self.gh and
									not (x == 0 and y == 0)):
								if mines[i + x, j + y] == 9:
									hints[i, j] += 1

		return hints

	def is_same_cell(self, p1, p2):
		x1 = p1[0] // self.gs
		y1 = p1[1] // self.gs
		x2 = p2[0] // self.gs
		y2 = p2[1] // self.gs

		if x1 == x2 and y1 == y2:
			return((x1, y1))
		return False

	def reveal_cell(self, c, clicked = False):
		i = c[0]
		j = c[1]

		if self.revealed[c] == FLAG:
			self.revealed[c] = HIDDEN
			return

		if self.map[c] == MINE:
			print("YOU LOSE!!!")
			self.reveal_all()

		elif self.map[c] > 0 and self.revealed[c] == REVEALED and self.count_surr_flags(c) == self.map[c] and clicked:
			for x in range(-1, 2):
				for y in range(-1, 2):
					if (i + x >= 0 and j + y >= 0 and
							i + x < self.gw and y + j < self.gh and
							self.revealed[i + x, j + y] == HIDDEN):
						self.reveal_cell((i + x, j + y))

		self.revealed[c] = REVEALED_NOT_DRAWN

		if self.map[c] == 0:
			for x in range(-1, 2):
				for y in range(-1, 2):
					if (i + x >= 0 and j + y >= 0 and
							i + x < self.gw and y + j < self.gh):
						if self.revealed[i + x, j + y] == HIDDEN:
							self.reveal_cell((i + x, j + y))

		self.check_victory()

	def count_surr_flags(self, c):
		i = c[0]
		j = c[1]
		n_flags = 0
		for x in range(-1, 2):
			for y in range(-1, 2):
				if (i + x >= 0 and j + y >= 0 and
						i + x < self.gw and y + j < self.gh):
					if self.revealed[i + x, j + y] == 4:
						n_flags += 1

		return n_flags

	def flag_cell(self, c):
		if self.revealed[c] == HIDDEN:
			self.revealed[c] = FLAG_NOT_DRAWN
		elif self.revealed[c] == FLAG:
			self.revealed[c] = HIDDEN

	def check_victory(self):
		n_uncovered = 0

		for i in range(self.gw):
			for j in range(self.gh):
				if self.revealed[i, j] == REVEALED or self.revealed[i, j] == REVEALED_NOT_DRAWN:
					n_uncovered += 1

		if n_uncovered == self.gw * self.gh - self.nm:
			print("YOU WIN!!!")


	def reveal_all(self):
		self.revealed = np.ones((self.gw, self.gh))

	def get_color(self, c):
		if isinstance(c, str):
			return COLORS[c]
		else:
			return list(COLORS.values())[c - 1]

def main():
	g = MinesweeperGame(WIDTH, HEIGHT, SCALE, N)
	g.play()

if __name__ == '__main__':
	main()
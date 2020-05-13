from PIL import Image, ImageTk

class SpriteSheetLoader:
	
	def __init__(self):
		self._images = {}

	def load_all(self):
		for i in self.load_player():
			name, image = i
			self._images[name] = ImageTk.PhotoImage(image)

		for i in self.load_mushroom():
			name, image = i
			self._images[name] = ImageTk.PhotoImage(image)

		for i in self.load_coin():
			name, image = i
			self._images[name] = ImageTk.PhotoImage(image)

		for i in self.load_bounce():
			name, image = i
			self._images[name] = ImageTk.PhotoImage(image)
		return self._images


	def load_player(self):
		imgs = []
		sheet = Image.open("spritesheets/characters.png")
		size = 16
		init_x, init_y = 80, 34
		imgs.append(["spr_mario_standing_right", sheet.crop((init_x, init_y, init_x + size, init_y + size))])
		imgs.append(["spr_mario_standing_left", sheet.crop((init_x, init_y, init_x + size, init_y + size)).transpose(Image.FLIP_LEFT_RIGHT)])

		for i in range(1, 4):
			imgs.append(["spr_mario_running{}_right".format(i-1), sheet.crop((init_x + i * (size+1), init_y, init_x + size + i * (size+1), init_y + size))])
			imgs.append(["spr_mario_running{}_left".format(i-1), sheet.crop((init_x + i * (size+1), init_y, init_x + size + i * (size+1), init_y + size)).transpose(Image.FLIP_LEFT_RIGHT)])
		
		imgs.append(["spr_mario_jumping_right", sheet.crop((init_x + 5 * (size+1), init_y, init_x + size + 5 * (size+1), init_y + size))])
		imgs.append(["spr_mario_jumping_left", sheet.crop((init_x + 5 * (size+1), init_y, init_x + size + 5 * (size+1), init_y + size)).transpose(Image.FLIP_LEFT_RIGHT)])
		
		return imgs

	def load_mushroom(self):
		imgs = []
		sheet = Image.open("spritesheets/enemies.png")
		size = 16
		init_x, init_y = 0, 16

		for i in range(2):
			imgs.append(["spr_mushroom_walking{}".format(i), sheet.crop((init_x + i * size, init_y, init_x + size + i * size, init_y + size))])

		imgs.append(["spr_mushroom_dead", sheet.crop((init_x + 2 * size, init_y, init_x + size + 2 * size, init_y + size))])

		return imgs

	def load_coin(self):
		imgs = []
		sheet = Image.open("spritesheets/items.png")
		size = 16
		init_x, init_y = 0, 96

		for i in range(2):
			imgs.append(["spr_coin{}".format(i), sheet.crop((init_x, init_y + i * size, init_x + size, init_y + size + i * size))])
		return imgs

	def load_bounce(self):
		imgs = []
		sheet = Image.open("spritesheets/items.png")
		size_x, size_y = 16, 32
		init_x, init_y = 80, 0
		for i in range(3):
			imgs.append(["spr_bounce{}".format(2-i), sheet.crop((init_x + i * size_x, init_y, init_x + size_x + i * size_x, init_y + size_y))])
		return imgs


if __name__ == "__main__":
	s = SpriteSheetLoader()
	s.load_all()





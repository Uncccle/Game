"""
Simple 2d world where the player can interact with the items in the world.
"""

__author__ = ""
__date__ = ""
__version__ = "1.0.0"
__copyright__ = "The University of Queensland, 2019"

import math
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter.filedialog import askopenfilename
import tkinter.ttk as ttk
from typing import Tuple, List
import time

import pymunk

from game.block import Block, MysteryBlock
from game.item import DroppedItem
from game.entity import Entity, BoundaryWall
from game.mob import Mob, CloudMob, Fireball
from game.view import GameView, ViewRenderer
from game.util import get_collision_direction
from game.item import Coin
from game.world import World

from player import Player
from level import load_world, WorldBuilder

from SpriteSheetLoader import SpriteSheetLoader
from highscore import HighScores
import loader

BLOCK_SIZE = 2 ** 4
GRID_WIDTH = 2 ** 4
GRID_HEIGHT = 2 ** 4
SCROLL_RADIUS = 50
MAX_WINDOW_SIZE = (1080, math.inf)

GOAL_SIZES = {
    "flag": (0.2, 9),
    "tunnel": (2, 2)
}


BLOCKS = {
    '#': 'brick',
    '%': 'brick_base',
    '?': 'mystery_empty',
    '$': 'mystery_coin',
    '^': 'cube',
    'b': 'bouncy',
    'S': 'switch',
    'I': 'flagpole',
    '=': 'tunnel',
}


ITEMS = {
    'C': 'coin',
    '*': 'star',
}

MOBS = {
    '&': "cloud",
    "@": "mushroom",
}


def create_block(world: World, block_id: str, x: int, y: int, *args):
    """Create a new block instance and add it to the world based on the block_id.

    Parameters:
        world (World): The world where the block should be added to.
        block_id (str): The block identifier of the block to create.
        x (int): The x coordinate of the block.
        y (int): The y coordinate of the block.
    """
    block_id = BLOCKS[block_id]
    if block_id == "mystery_empty":
        block = MysteryBlock()
    elif block_id == "mystery_coin":
        block = MysteryBlock(drop="coin", drop_range=(3, 6))
    elif block_id == "bouncy":
        block = BouncyBlock()
    elif block_id == "switch":
        block = SwitchBlock()
    elif block_id == "flagpole":
        block = Flagpole()
    elif block_id == "tunnel":
        block = Tunnel()
    else:
        block = Block(block_id)

    world.add_block(block, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_item(world: World, item_id: str, x: int, y: int, *args):
    """Create a new item instance and add it to the world based on the item_id.

    Parameters:
        world (World): The world where the item should be added to.
        item_id (str): The item identifier of the item to create.
        x (int): The x coordinate of the item.
        y (int): The y coordinate of the item.
    """
    item_id = ITEMS[item_id]
    if item_id == "coin":
        item = Coin()
    elif item_id == "star":
        item = Star()
    else:
        item = DroppedItem(item_id)

    world.add_item(item, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_mob(world: World, mob_id: str, x: int, y: int, *args):
    """Create a new mob instance and add it to the world based on the mob_id.

    Parameters:
        world (World): The world where the mob should be added to.
        mob_id (str): The mob identifier of the mob to create.
        x (int): The x coordinate of the mob.
        y (int): The y coordinate of the mob.
    """
    mob_id = MOBS[mob_id]
    if mob_id == "cloud":
        mob = CloudMob()
    elif mob_id == "fireball":
        mob = Fireball()
    elif mob_id == "mushroom":
        mob = MushroomMob()
    else:
        mob = Mob(mob_id, size=(1, 1))

    world.add_mob(mob, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_unknown(world: World, entity_id: str, x: int, y: int, *args):
    """Create an unknown entity."""
    world.add_thing(Entity(), x * BLOCK_SIZE, y * BLOCK_SIZE,
                    size=(BLOCK_SIZE, BLOCK_SIZE))




BLOCK_IMAGES = {
    "brick": "brick",
    "brick_base": "brick_base",
    "cube": "cube",
    "bouncy": "bounce_block",
    "switch": "switch",
    "flagpole": "flag",
    "tunnel": "tunnel",
}

ITEM_IMAGES = {
    "coin": "coin_item",
    "star": "star",
}

MOB_IMAGES = {
    "cloud": "floaty",
    "fireball": "fireball_down",
    "mushroom": "mushroom",
}


class SwitchBlock(Block):

    _id = "switch"

    def __init__(self):
        super().__init__()
        self._activated = False
        self._start_time = 0
        self._duration = 10
        self._destroyed_blocks = []

    def on_hit(self, event, data):
        world, player = data
        self._world = world
        if get_collision_direction(player, self) != "A":
            return
        if not self._activated:
            self._activated = True
            self._start_time = time.time()

            # Destroy blocks within radius
            radius = 35 # pixels
            x, y = self.get_position()
            queries = world._space.point_query((x, y), radius,
                   pymunk.ShapeFilter(mask=world._thing_categories["block"]))

            for i in queries:
                if i.shape.object._id == "brick":
                    pos = i.shape.object.get_position()
                    self._destroyed_blocks.append([i.shape.object, pos[0], pos[1]])
                    world.remove_block(i.shape.object)
            print(self._destroyed_blocks)

    def tick(self):
        if time.time() >= (self._start_time + self._duration) and self._activated:
            self._activated = False
            for i in self._destroyed_blocks:
                self._world.add_block(i[0],i[1],i[2])


    def activated(self):
        return self._activated


class MarioViewRenderer(ViewRenderer):
    """A customised view renderer for a game of mario."""

    @ViewRenderer.draw.register(Player)
    def _draw_player(self, instance: Player, shape: pymunk.Shape,
                     view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if shape.body.velocity.x >= 0:
            image = self.load_image("mario_right")
        else:
            image = self.load_image("mario_left")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="player")]


    @ViewRenderer.draw.register(MysteryBlock)
    def _draw_mystery_block(self, instance: MysteryBlock, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if instance.is_active():
            image = self.load_image("coin")
        else:
            image = self.load_image("coin_used")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]

    @ViewRenderer.draw.register(SwitchBlock)
    def _draw_switch_block(self, instance: SwitchBlock, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if instance.activated():
            image = self.load_image("switch_pressed")
        else:
            image = self.load_image("switch")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]



class StatusView(tk.Frame):
    def __init__(self, master, max_health, score):
        super().__init__(master)
        self.pack()
        self._health = 5
        self._score = score;

        self._master = master

        s = ttk.Style()
        s.theme_use("clam")
        s.configure("greenBar.Horizontal.TProgressbar", foreground='green', background='green')
        s.configure("orangeBar.Horizontal.TProgressbar", foreground='orange', background='orange')
        s.configure("redBar.Horizontal.TProgressbar", foreground='red', background='red')
        s.configure("yellowBar.Horizontal.TProgressbar", foreground='yellow', background='yellow')
        self._progress = ttk.Progressbar(self._master, style = "redBar.Horizontal.TProgressbar", orient = "horizontal", length = 1080, mode = 'determinate')
        self._progress.pack()
        self._progress["maximum"] = max_health
        self.set_health(self._health)
        self._score_w = tk.Label(self._master, text="Score: {}".format(self._score))
        self._score_w.pack()

    def set_health(self, currentValue):
        self._progress['value'] = currentValue
        if currentValue >= self._progress["maximum"]/2.0:
            self.set_health_colour("green")
        elif currentValue > self._progress["maximum"]/4.0:
            self.set_health_colour("orange")
        else:
            self.set_health_colour("red")

    def set_health_colour(self, colour):
        if colour == "green":
            self._progress.config(style = "greenBar.Horizontal.TProgressbar")
        elif colour == "orange":
            self._progress.config(style = "orangeBar.Horizontal.TProgressbar")
        elif colour == "red":
            self._progress.config(style = "redBar.Horizontal.TProgressbar")
        elif colour == "yellow":
            self._progress.config(style = "yellowBar.Horizontal.TProgressbar")

    def set_score(self, currentScore):
        self._score = currentScore
        self._score_w.config(text="Score: {}".format(self._score))

    def unpack(self):
        self._score_w.pack_forget()
        self._progress.pack_forget()
        self.pack_forget()

class BouncyBlock(Block):

    _id = "bouncy"

    def __init__(self):
        super().__init__()

    def on_hit(self, event, data):
        """Callback collision with player event handler."""
        world, player = data
        # Ensure the bottom of the block is being hit
        if get_collision_direction(player, self) != "A":
            return

        velocity = player.get_velocity()
        player.set_velocity((velocity.x * 0.8, -300))


class MushroomMob(Mob):

    _id = "mushroom"

    def __init__(self):
        super().__init__(self._id, size=(16, 16), weight=100, tempo=30)
        self.direction = 1
        self.dead = False


    def on_hit(self, event: pymunk.Arbiter, data):
        world, player = data
        if get_collision_direction(player, self) == "A":
            # kill mob
            world.remove_mob(self)
            velocity = player.get_velocity()
            player.set_velocity((velocity.x * 0.8, -100))
            return

        player.change_health(-1)
        # velocity = player.get_velocity()
        mob_x, mob_y = self.get_position()
        player_x, player_y = player.get_position()
        if player_x < mob_x:
            player.set_velocity((-50, -100))
        elif player_x > mob_x:
            player.set_velocity((50, -100))

    def freeze(self):
        self.set_tempo(0)
        self.dead = True

    def step(self, time_delta, game_data):
        vx = self.get_tempo() * self.direction
        self.set_velocity((vx, self.get_velocity()[1]))


class AnimatedMarioViewRenderer(ViewRenderer):

    def __init__(self, block_images, item_images, mob_images):
        """
        Construct a new ViewRouter with appropriate entity id to image file mappings.

        Parameters:
             block_images (dict<str: str>): A mapping of block ids to their respective images
             item_images (dict<str: str>): A mapping of item ids to their respective images
             mob_images (dict<str: str>): A mapping of mob ids to their respective images
        """
        super().__init__(block_images, item_images, mob_images)

        loader = SpriteSheetLoader()
        self._images = loader.load_all()

        self._mario_count = 0
        self._mario_speed = 8
        self._player_facing = 1

        self._mob_count = {}
        self._mob_speed = {}
        self._mob_death = {}

        self._bouncy_count = {}
        self._bouncy_speed = {}
        self._bouncy_activated = {}

        self._coin_count = {}
        self._coin_speed = {}

        

    def set_player_facing(self, facing):
        self._player_facing = facing


    @ViewRenderer.draw.register(Player)
    def _draw_player(self, instance: Player, shape: pymunk.Shape,
                     view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:

        direction = "right" if self._player_facing == 1 else "left"
        if int(shape.body.velocity.y) == float(shape.body.velocity.y) and shape.body.velocity.y != 0:
            image = self.load_image("spr_mario_jumping_{}".format(direction))
        elif abs(shape.body.velocity.x) > 10:
            if self._mario_count <= self._mario_speed:
                image = self.load_image("spr_mario_running0_{}".format(direction))
                self._mario_count += 1
            elif self._mario_count <= self._mario_speed * 2:
                image = self.load_image("spr_mario_running1_{}".format(direction))
                self._mario_count += 1
            elif self._mario_count <= self._mario_speed * 3:
                image = self.load_image("spr_mario_running2_{}".format(direction))
                self._mario_count += 1
            else:
                image = self.load_image("spr_mario_running0_{}".format(direction))
                self._mario_count = 0
        else:
            image = self.load_image("spr_mario_standing_{}".format(direction))

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="player")]

    def kill_mushroom(self, shape):
        self._mob_death[shape] = True

    @ViewRenderer.draw.register(MushroomMob)
    def _draw_mushroommob(self, instance: Player, shape: pymunk.Shape,
                     view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if self._mob_count.get(shape, None) == None:
            self._mob_count[shape] = 0
            self._mob_speed[shape] = 15
            self._mob_death[shape] = False

        if self._mob_death[shape]:
            image = self.load_image("spr_mushroom_dead")

        elif shape.body.velocity.x != 0:
            if self._mob_count[shape] <= self._mob_speed[shape]:
                image = self.load_image("spr_mushroom_walking0")
                self._mob_count[shape] += 1
            elif self._mob_count[shape] <= self._mob_speed[shape] * 2:
                image = self.load_image("spr_mushroom_walking1")
                self._mob_count[shape] += 1
            else:
                image = self.load_image("spr_mushroom_walking0")
                self._mob_count[shape] = 0
        else:
            image = self.load_image("spr_mushroom_walking0")
        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="mob")]


    def activate_bouncy(self, shape):
        self._bouncy_activated[shape] = True

    @ViewRenderer.draw.register(BouncyBlock)
    def _draw_bouncyblock(self, instance: Player, shape: pymunk.Shape,
                     view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if self._bouncy_count.get(shape, None) == None:
            self._bouncy_count[shape] = 0
            self._bouncy_speed[shape] = 3
            self._bouncy_activated[shape] = False


        if not self._bouncy_activated[shape]:
            image = self.load_image("spr_bounce0")
        elif self._bouncy_count[shape] <= self._bouncy_speed[shape]:
            image = self.load_image("spr_bounce0")
            self._bouncy_count[shape] += 1
        elif self._bouncy_count[shape] <= self._bouncy_speed[shape] * 2:
            image = self.load_image("spr_bounce1")
            self._bouncy_count[shape] += 1
        elif self._bouncy_count[shape] <= self._bouncy_speed[shape] * 3:
            image = self.load_image("spr_bounce2")
            self._bouncy_count[shape] += 1
        else:
            image = self.load_image("spr_bounce0")
            self._bouncy_count[shape] = 0
            self._bouncy_activated[shape] = False

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y-8,
                                  image=image, tags="block")]

    @ViewRenderer.draw.register(Coin)
    def _draw_coin(self, instance: Player, shape: pymunk.Shape,
                     view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if self._coin_count.get(shape, None) == None:
            self._coin_count[shape] = 0
            self._coin_speed[shape] = 5
        if self._coin_count[shape] <= self._coin_speed[shape]:
            image = self.load_image("spr_coin0")
            self._coin_count[shape] += 1
        elif self._coin_count[shape] <= self._coin_speed[shape] * 2:
            image = self.load_image("spr_coin1")
            self._coin_count[shape] += 1
        else:
            image = self.load_image("spr_coin0")
            self._coin_count[shape] = 0
        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="item")]

    @ViewRenderer.draw.register(MysteryBlock)
    def _draw_mystery_block(self, instance: MysteryBlock, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if instance.is_active():
            image = self.load_image("coin")
        else:
            image = self.load_image("coin_used")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]

    @ViewRenderer.draw.register(SwitchBlock)
    def _draw_switch_block(self, instance: SwitchBlock, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if instance.activated():
            image = self.load_image("switch_pressed")
        else:
            image = self.load_image("switch")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]

class Star(DroppedItem):
    
    _id = "star"

    def collect(self, player):
        player.set_jumping(True)

class PlayerStar(object):
    def __init__(self):
        self._activated = True
        self._start_time = 0
        self._duration = 0

    def activated(self):
        return self._activated

    def activate(self, duration = 10):
        self._start_time = time.time()
        self._duration = duration
        self._activated = True

    def tick(self):
        if time.time() >= (self._start_time + self._duration):
            self._activated = False


class Flagpole(Block):

    _id = "flagpole"
    _cell_size = GOAL_SIZES["flag"]
    _next_level = None

    def on_hit(self, event, data):
        world, player = data

        if get_collision_direction(player, self) == "A":
            player.change_health(5)

        

class Tunnel(Block):

    _id = "tunnel"
    _cell_size = GOAL_SIZES["tunnel"]
    _next_level = None


class MarioApp:
    """High-level app class for Mario, a 2d platformer"""

    def __init__(self, master):
        """Construct a new game of a MarioApp game.

        Parameters:
            master (tk.Tk): tkinter root widget
        """
        self._master = master

        self._start_game()


        def donothing():
            filewin = tk.Toplevel(self._master)
            button = tk.Button(filewin, text="Do nothing button")
            button.pack()

        menubar = tk.Menu(self._master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load Level", command=self._retrieve_input)
        filemenu.add_command(label="Reset Level", command=lambda: self.reset_world(full=True))
        filemenu.add_command(label="High Scores", command=self.display_high_scores)
        filemenu.add_command(label="Exit", command=self._ask_quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self._master.config(menu=menubar)

        # Special Item: Star
        self._player_star = PlayerStar()

        # Special Block: switch
        self._switches = []
        for i in self._world.get_all_things():
            try:
                if i._id == "switch":
                    self._switches.append(i)
            except:
                pass

        self._can_jump = False

        # Score
        self._scores = HighScores()

        # Wait for window to update before continuing
        master.update_idletasks()
        self.step()

    def _start_game(self):
        path = tk.simpledialog.askstring("Mario", "Configuration file:")
        self._game = loader.load_level(path)
        if self._game == None:
            tk.messagebox.showerror("Error", "Configuration file wrong.")
            self._master.destroy()
       

        # World builder
        world_builder = WorldBuilder(BLOCK_SIZE, gravity=(0, int(self._game["==World=="]["gravity"])), fallback=create_unknown)
        world_builder.register_builders(BLOCKS.keys(), create_block)
        world_builder.register_builders(ITEMS.keys(), create_item)
        world_builder.register_builders(MOBS.keys(), create_mob)
        self._builder = world_builder

        self._current_level = self._game["==World=="]['start']
        self._world = load_world(self._builder, self._current_level)

        # Set tunnel/goal
        Flagpole._next_level = self._game[("=="+self._current_level+"==")]["goal"]
        Tunnel._next_level = self._game[("=="+self._current_level+"==")].get("tunnel", None)

        self._player = Player(max_health=int(self._game["==Player=="]["health"]))
        print(self._player.get_shape())
        self._world.add_player(self._player, int(self._game["==Player=="]["x"]), int(self._game["==Player=="]["y"]), int(self._game["==Player=="]["mass"]))

        self._max_speed = int(self._game["==Player=="]["max_velocity"])

        self._setup_collision_handlers()

        self._renderer = AnimatedMarioViewRenderer(BLOCK_IMAGES, ITEM_IMAGES, MOB_IMAGES) # Into Animated

        size = tuple(map(min, zip(MAX_WINDOW_SIZE, self._world.get_pixel_size())))
        self._view = GameView(self._master, size, self._renderer)
        self._view.pack()

        self._status_view = StatusView(self._master, int(self._game["==Player=="]['health']), 0)


        self.bind()


    def reset_world(self, new_level=None, full=False):
        if new_level == None:
            new_level = self._current_level
        else:
            self._current_level = new_level
            self._scores = HighScores()
        world_builder = WorldBuilder(BLOCK_SIZE, gravity=(0, 500), fallback=create_unknown)
        world_builder.register_builders(BLOCKS.keys(), create_block)
        world_builder.register_builders(ITEMS.keys(), create_item)
        world_builder.register_builders(MOBS.keys(), create_mob)
        self._builder = world_builder
        self._world = load_world(self._builder, new_level)

        Flagpole._next_level = self._game[("=="+self._current_level+"==")]["goal"]
        Tunnel._next_level = self._game[("=="+self._current_level+"==")].get("tunnel", None)

        if full: # full reset player stats
            self._player = Player(max_health=int(self._game["==Player=="]["health"]))
        self._world.add_player(self._player, int(self._game["==Player=="]["x"]), int(self._game["==Player=="]["y"]), int(self._game["==Player=="]["mass"]))

        self._setup_collision_handlers()

        self._view.pack_forget()
        size = tuple(map(min, zip(MAX_WINDOW_SIZE, self._world.get_pixel_size())))
        self._view = GameView(self._master, size, self._renderer)
        self._view.pack()

        self._status_view.unpack()
        self._status_view = StatusView(self._master, int(self._game["==Player=="]['health']), self._player._score)

    def display_high_scores(self):
        print(self._current_level, self._current_level.replace(".txt","_score.txt"))
        top = tk.Toplevel()
        top.geometry("240x260")

        label = tk.Label(top, text="High Scores:")
        label.pack()

        if self._scores.load_scores(self._current_level.replace(".txt","_score.txt")) == None:
            tk.Label(top, text="No high scores yet").pack()
            return
        for i in range(len(self._scores.get_top_10())):
            top10 = self._scores.get_top_10()
            tk.Label(top, text=(str(i+1)+': '+str(top10[i][0])+'\t\t'+str(top10[i][1]))).pack()



    def bind(self):
        """Bind all the keyboard events to their event handlers."""
        self._master.bind("a", lambda e: self._move(-1, 0))
        self._master.bind("<Left>", lambda e: self._move(-1, 0))
        self._master.bind("d", lambda e: self._move(1, 0))
        self._master.bind("<Right>", lambda e: self._move(1, 0))
        self._master.bind("w", lambda e: self._jump())
        self._master.bind("<Up>" , lambda e: self._jump())
        self._master.bind("<space>" , lambda e: self._jump())
        self._master.bind("s", lambda e: self._duck())
        self._master.bind("<Down>", lambda e: self._duck())


    def redraw(self):
        """Redraw all the entities in the game canvas."""
        self._view.delete(tk.ALL)
        self._view.draw_entities(self._world.get_all_things())

    def scroll(self):
        """Scroll the view along if the player is within SCROLL_RADIUS
        from the edge of the screen.
        """
        # calculate the x distance from the right edge
        x_position = self._player.get_position()[0]
        x_offset = self._view.get_offset()[0]
        screen_size = self._master.winfo_width()
        edge_distance = screen_size - (x_position + x_offset)

        if edge_distance < SCROLL_RADIUS:
            x_position -= 5

            # place a backstop boundary wall on the left side of the screen
            # to prevent the player from going backwards in the game
            world_space = self._world.get_space()
            wall = BoundaryWall("backstop", world_space.static_body,
                                (x_position, 0),
                                (x_position, self._world.get_pixel_size()[1]), 5)
            world_space.add(wall.get_shape())

            # shift the view offset by the screen size
            self._view.shift((-(screen_size - SCROLL_RADIUS), 0))

    def step(self):
        """Step the world physics and redraw the canvas."""
        data = (self._world, self._player)
        self._world.step(data)

        self.scroll()
        self.redraw()

        self._player_star.tick()
        if not self._player_star.activated():
            self._status_view.set_health(self._player.get_health())
        for i in self._switches:
            i.tick()
        self._master.after(10, self.step)

    def _move(self, dx, dy):
        if dx < 0:
            self._renderer.set_player_facing(-1)
        elif dx > 0:
            self._renderer.set_player_facing(1)
        velocity = self._player.get_velocity()
        sign = lambda x: 1 if x >= 0 else -1
        self._player.set_velocity((self._max_speed * sign(dx), velocity.y))

    def _jump(self):
        x, y = self._player.get_position()
        y += BLOCK_SIZE
        if self._world.get_block(x, y) != None:
            self._can_jump = True

        if self._can_jump:
            velocity = self._player.get_velocity()
            self._player.set_velocity((velocity.x * 0.8, -200))
            self._can_jump = False

    def _duck(self):
        x, y = self._player.get_position()
        y += BLOCK_SIZE
        if self._world.get_block(x, y) != None:
            if self._world.get_block(x, y)._id == "tunnel":
                if self._world.get_block(x, y)._next_level != None:
                    self.reset_world(self._world.get_block(x, y)._next_level)

    def _setup_collision_handlers(self):
        self._world.add_collision_handler("player", "item", on_begin=self._handle_player_collide_item)
        self._world.add_collision_handler("player", "block", on_begin=self._handle_player_collide_block,
                                          on_separate=self._handle_player_separate_block)
        self._world.add_collision_handler("player", "mob", on_begin=self._handle_player_collide_mob)
        self._world.add_collision_handler("mob", "block", on_begin=self._handle_mob_collide_block)
        self._world.add_collision_handler("mob", "mob", on_begin=self._handle_mob_collide_mob)
        self._world.add_collision_handler("mob", "item", on_begin=self._handle_mob_collide_item)

    def _handle_mob_collide_block(self, mob: Mob, block: Block, data,
                                  arbiter: pymunk.Arbiter) -> bool:
        if mob.get_id() == "fireball":
            if block.get_id() == "brick":
                self._world.remove_block(block)
            self._world.remove_mob(mob)
        if mob.get_id() == "mushroom":
            if get_collision_direction(block, mob) in ("L", "R"):
                mob.direction *= -1
        return True

    def _handle_mob_collide_item(self, mob: Mob, block: Block, data,
                                 arbiter: pymunk.Arbiter) -> bool:
        return False

    def _handle_mob_collide_mob(self, mob1: Mob, mob2: Mob, data,
                                arbiter: pymunk.Arbiter) -> bool:
        if mob1.get_id() == "fireball" or mob2.get_id() == "fireball":
            self._world.remove_mob(mob1)
            self._world.remove_mob(mob2)

        return False

    def _handle_player_collide_item(self, player: Player, dropped_item: DroppedItem,
                                    data, arbiter: pymunk.Arbiter) -> bool:
        """Callback to handle collision between the player and a (dropped) item. If the player has sufficient space in
        their to pick up the item, the item will be removed from the game world.

        Parameters:
            player (Player): The player that was involved in the collision
            dropped_item (DroppedItem): The (dropped) item that the player collided with
            data (dict): data that was added with this collision handler (see data parameter in
                         World.add_collision_handler)
            arbiter (pymunk.Arbiter): Data about a collision
                                      (see http://www.pymunk.org/en/latest/pymunk.html#pymunk.Arbiter)
                                      NOTE: you probably won't need this
        Return:
             bool: False (always ignore this type of collision)
                   (more generally, collision callbacks return True iff the collision should be considered valid; i.e.
                   returning False makes the world ignore the collision)
        """
        dropped_item.collect(self._player)

        if dropped_item.get_id() == "star":
            self._player_star.activate()
            self._status_view.set_health_colour("yellow")

        self._world.remove_item(dropped_item)
        self._status_view.set_score(self._player.get_score())
        return False

    def _handle_player_collide_block(self, player: Player, block: Block, data,
                                     arbiter: pymunk.Arbiter) -> bool:
        if get_collision_direction(player, block) == "A":
            self._can_jump = True

        if block._id == "bouncy":
            if get_collision_direction(player, block) == "A":
                self._renderer.activate_bouncy(block.get_shape())
        elif block._id == "switch":
            if block.activated():
                return False
        elif block._id == "flagpole":
            name = self._ask_name()
            score_name = self._current_level.replace(".txt","_score.txt")
            self._scores.load_scores(score_name)
            self._scores.add_score(name, self._player.get_score())
            self._scores.save_scores(score_name)
            self.reset_world(block._next_level)
        block.on_hit(arbiter, (self._world, player))
        return True

    def _handle_player_collide_mob(self, player: Player, mob: Mob, data,
                                   arbiter: pymunk.Arbiter) -> bool:

        if self._player_star.activated():
            self._world.remove_mob(mob)
            return False
        else:
            if mob._id == "mushroom":
                if mob.dead:
                    return False
                if get_collision_direction(player, mob) == "A":
                    self._renderer.kill_mushroom(mob.get_shape())
                    mob.freeze()
                    self._master.after(500, lambda: self._world.remove_mob(mob))
                    self._can_jump = True
                    self._jump()
                    return True

            mob.on_hit(arbiter, (self._world, player))
            self._status_view.set_health(self._player.get_health())
            self._status_view.set_score(self._player.get_score())

            if self._player.get_health() == 0:
                tk.messagebox.showinfo("Gameover", "You died.")
                self._master.quit()
            return True

    def _handle_player_separate_block(self, player: Player, block: Block, data,
                                      arbiter: pymunk.Arbiter) -> bool:
        return True

    def _retrieve_input(self):
        level = tk.simpledialog.askstring("Load Level", "Please input the level name:")
        if level:
            self.reset_world(new_level=level, full=True)

    def _ask_quit(self):
        if tk.messagebox.askokcancel("Quit", "You want to quit now?"):
            self._master.destroy()

    def _ask_name(self):
        name = tk.simpledialog.askstring("Good Job!", "Please enter your name:")
        return name

class Inputbox():
    def __init__(self, text=""):
        self.root = tk.Tk()
        self.get = ""
        self.root.geometry("300x100")
        self.root.title("Inputbox")
        self.label_file_name = tk.Label(self.root, text=text)
        self.label_file_name.pack()
        self.entry = tk.Entry(self.root)
        self.entry.pack()
        self.entry.focus()
        self.entry.bind("<Return>", lambda x: self.getinput(self.entry.get()))
        self.root.mainloop()
 
    def getinput(self, value):
        self.get = value
        self.root.destroy()

def main():
    root = tk.Tk()
    root.title("Mario")
    app = MarioApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


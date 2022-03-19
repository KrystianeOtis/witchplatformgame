import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Potion Grab")

#define font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)

#define colors
BLACK = (0,0,0)
WHITE = (255, 255, 255)
PINK = (255, 210, 210)

# load images
restart_button = pygame.image.load("Assets/restartbutton.png")
restart_img = pygame.transform.scale(restart_button, (400, 200))
start_button = pygame.image.load("Assets/startwitchy.png")
start_img = pygame.transform.scale(start_button, (400, 200))
quit_button = pygame.image.load("Assets/quitbutton.png")
quit_img = pygame.transform.scale(quit_button, (400, 200))
background_img = pygame.image.load("Assets/creepyforest.png")



# load sounds
item_collect_sound = pygame.mixer.Sound("Assets/sounds/itemcollect.wav")
item_collect_sound.set_volume(0.5)
dying_sound = pygame.mixer.Sound("Assets/sounds/curse.wav")
dying_sound.set_volume(0.5)
jumping_sound = pygame.mixer.Sound("Assets/sounds/jump3.wav")
jumping_sound.set_volume(0.5)
restart_sound = pygame.mixer.Sound("Assets/sounds/catmeow.mp3")
restart_sound.set_volume(0.5)
quit_sound = pygame.mixer.Sound("Assets/sounds/meowquit.wav")
quit_sound.set_volume(0.5)
win_sound = pygame.mixer.Sound("Assets/sounds/youwon.wav")
win_sound.set_volume(0.5)
reached_door_sound = pygame.mixer.Sound("Assets/sounds/reachedDoor.wav")
reached_door_sound.set_volume(0.5)
pygame.mixer.music.load("Assets/sounds/my_love_piano.mp3")
pygame.mixer.music.play(-1, 0.0, 5000)

# define game variables
tile_size = 50
game_over = 0
main_menu = True
level = 3
max_levels = 3
score = 0


#function to draw text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

# function to reset level
def reset_level(level):
    player.reset(100, screen_height - 130)
    # blob_group.empty()
    water_group.empty()
    level_door_group.empty()
    if path.exists(f"level{level}_data"):
        pickle_in = open(f"level{level}_data", "rb")
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):

        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            # left mouse clicked
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:  # left mouse button released
            self.clicked = False

        # draw button
        screen.blit(self.image, self.rect)

        return action


class Player:
    def __init__(self, x, y):
        self.reset(x, y)  # creates player from scratch

    def update(self, game_over):
        # delta variables
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:
            # get keypresses
            key = pygame.key.get_pressed()
            if (
                key[pygame.K_SPACE] and self.jumped == False and self.in_air == False
            ):  # jump
                jumping_sound.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:  # move left
                dx -= 5
                self.counter += 1  # when pressing left the image walks left
                self.direction = -1
            if key[pygame.K_RIGHT]:  # move right
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                # when index is 0 player image stops walking (even if in mid step)
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # handle animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            # delta y will increase everytime the player jumps
            dy += self.vel_y

            # check for collision
            self.in_air = True  # player is in mid-air
            for tile in world.tile_list:
                # Check for collision in x direction
                if tile[1].colliderect(
                    self.rect.x + dx, self.rect.y, self.width, self.height
                ):
                    dx = 0  # cant walk through block
                # check for collision in y direction before making updates
                if tile[1].colliderect(
                    self.rect.x, self.rect.y + dy, self.width, self.height
                ):
                    # Check if below the ground (jumping and hitting head)
                    if self.vel_y < 0:
                        # distance between bottom of block and top of player
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # Check if above the ground (Falling)
                    elif self.vel_y >= 0:
                        # top of block and bottom of player(feet)
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False  # player landed on something


            # Check for collision with water
            if pygame.sprite.spritecollide(self, water_group, False):
                game_over = -1
                # print(game_over)
                dying_sound.play()

            # Check for collision with level_door
            if pygame.sprite.spritecollide(self, level_door_group, False):
                game_over = 1
                # print(game_over)
                reached_door_sound.play()

            # update player coordinates
            self.rect.x += dx
            self.rect.y += dy



        # if player dies show ghost image
        elif game_over == -1:
            self.image = self.dead_image
            draw_text("Game Over!", font, PINK, (screen_width // 2) - 200, screen_height // 4)
            if self.rect.y > 200:
                self.rect.y -= 5  # floats up
        # draw player onto the screen
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    # copied all of the self variables from player __init__ so that they reset when the game restarts. Deleted them and then called the reset function there instead
    # creates player from scratch
    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f"Assets/witch/move{num}.png")
            img_right = pygame.transform.scale(img_right, (49, 99))
            # flip image vertically so player image walks left
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load("Assets/witch/dedwitch.png")
        self.dead_image = pygame.transform.scale(self.dead_image, (50, 100))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True  # player is in midair


class World:
    def __init__(self, data):
        self.tile_list = []
        dirt_img = pygame.image.load("Assets/dirt.png")
        grass_img = pygame.image.load("Assets/grass.png")

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 3:
                    water = Water(
                        col_count * tile_size, row_count * tile_size + (tile_size // 2)
                    )
                    water_group.add(water)
                if tile == 4:
                    potion = Potion(
                        col_count * tile_size, row_count * tile_size + (tile_size // 2)
                    )
                    potion_group.add(potion)
                if tile == 5:
                    level_door = LevelDoor(
                        col_count * tile_size, row_count * tile_size - (tile_size // 1)
                    )
                    level_door_group.add(level_door)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])






class Water(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("Assets/liquidWaterTop.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Potion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("Assets/potion.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class LevelDoor(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("Assets/cauldron.png")
        self.image = pygame.transform.scale(img, (100,100))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


player = Player(100, screen_height - 130)

# blob_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
potion_group = pygame.sprite.Group()
level_door_group = pygame.sprite.Group()

#create potion for score
score_potion = Potion(tile_size //2, tile_size // 2)
potion_group.add(score_potion)

# load in level data and create world
if path.exists(f"level{level}_data"):
    pickle_in = open(f"level{level}_data", "rb")
    world_data = pickle.load(pickle_in)
world = World(world_data)

# create buttons
restart_button = Button(screen_width // 2 - 250, screen_height // 2 - 200, restart_img)
start_button = Button(screen_width // 2 - 450, screen_height // 4, start_img)
quit_button = Button(screen_width // 2 + 50, screen_height // 3, quit_img)

run = True
while run:

    clock.tick(fps)
    screen.fill((BLACK))
    screen.blit(background_img, (0, 0))
    # screen.blit(sun_img, (100, 100))

    if main_menu == True:
        if quit_button.draw():
            quit_sound.play()
            run = False
        if start_button.draw():
            restart_sound.play()
            main_menu = False
    else:

        world.draw()

        if game_over == 0:
        #check if a potion has been collected
            if pygame.sprite.spritecollide(player, potion_group, True): #set to true so that potions disapear off screen
                score += 1
                item_collect_sound.play()
            draw_text('X ' + str(score), font_score, BLACK, tile_size + 20, 10)


        water_group.draw(screen)
        potion_group.draw(screen)
        level_door_group.draw(screen)

        game_over = player.update(game_over)

        # if player has died
        if game_over == -1:
            if restart_button.draw():
                # resets player to beginning
                # player.reset(100, screen_height - 130)
                quit_sound.play()
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        # if player completed level
        if game_over == 1:
            # reset game and go to next level
            level += 1
            if level <= max_levels:
                # reset level
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('You Win!', font, BLACK,(screen_width // 2) - 200, screen_height // 4)
                # win_sound.play()
                # restart game
                if restart_button.draw():
                    level = 1
                    # reset level
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()

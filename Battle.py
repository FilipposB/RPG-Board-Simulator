import pygame
import pygame.camera
import random
import sys
import os

from multiprocessing import Process
import threading
from pygame.locals import (
    KEYDOWN, K_ESCAPE, QUIT,
    DOUBLEBUF, FULLSCREEN, MOUSEBUTTONDOWN, KEYUP)


class PaintMove:
    def __init__(self):
        self.paint = list()

    def add_spot(self, x, y, color):
        self.paint.append((x, y, color))


class Icon(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.surf = pygame.Surface((width, height))
        self.surf.fill((0, 0, 0))
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True


class TextIcon(Icon):
    def __init__(self, x, y, width, height, name):
        Icon.__init__(self, x, y, width, height)
        self.surf.fill((100, 0, 200))
        self.name = name
        nameSur = font.render(str(name), True, icon_text_color)
        nameRect = nameSur.get_rect()
        self.surf.blit(nameSur, nameRect.move(0, height / 2))


class ImageIcon(Icon):
    def __init__(self, x, y, width, height, name, number, img):
        Icon.__init__(self, x, y, width, height)
        self.surf = pygame.transform.scale(img, (width, height))
        self.name = name
        nameSur = font.render(str(name), True, icon_text_color)
        nameRect = nameSur.get_rect()
        name_surf = pygame.Surface((nameRect.width, nameRect.height))
        name_surf.fill((0, 0, 0))
        self.surf.blit(name_surf, nameRect.move(0, height - 20))
        self.surf.blit(nameSur, nameRect.move(0, height - 20))
        if number != "":
            nameSur = font.render(str(number), True, icon_text_color)
            nameRect = nameSur.get_rect()
            name_surf = pygame.Surface((nameRect.width, nameRect.height))
            name_surf.fill((0, 0, 0))
            self.surf.blit(name_surf, nameRect.move(0, 0))
            self.surf.blit(nameSur, nameRect.move(0, 0))


class Panel(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, img):
        pygame.sprite.Sprite.__init__(self)
        self.surf = pygame.transform.scale(
            pygame.image.load("Assets/" + img), (width, height))
        self.rect = pygame.Rect(x, y, width, height)


# This thread captures the camera as long as webcam is active
class WebcamCapture(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        cameras = pygame.camera.list_cameras()
        self.camera_size = (256, 256)
        self.webcam_is_visible = False
        self.working = False
        self.webcam = pygame.camera.Camera(cameras[0], self.camera_size)
        self.webcam_image = pygame.Surface(self.camera_size)
        self.camera_pos = (0, 0)
        self.camera_is_movable = False
        self.camera_available = False
        self.running = False
        self.turning_camera = False
        # moves the overlay bottom right
        self.move_camera((100000, 100000))

    def run(self):
        self.running = True
        while self.running:
            if self.webcam_is_visible and self.camera_available and not self.turning_camera:
                # print("d")
                self.working = True
                try:
                    if self.camera_available:
                        self.webcam_image = self.webcam.get_image()
                        pygame.draw.rect(self.webcam_image, (0, 0, 0), [
                                        0, 0, self.camera_size[0], self.camera_size[1]-17], 2)
                except:
                    print("error")
                    pass
                self.working = False

            self.working = False

    def turn_camera(self):
        self.webcam_is_visible = (not self.webcam_is_visible)
        self.turning_camera = True
        if self.webcam_is_visible:
            cameras = pygame.camera.list_cameras()
            try:
                self.webcam = pygame.camera.Camera(
                    cameras[0], self.camera_size)
                self.webcam.start()
                self.camera_available = True
            except:
                self.webcam_is_visible = False
                self.camera_available = False
        else:
            try:
                self.camera_available = False
                self.webcam.stop()
                self.turning_camera = False
            except:
                pass
        self.turning_camera = False

    def move_camera(self, new_pos):
        x = new_pos[0]
        y = new_pos[1]
        if (new_pos[0] + self.camera_size[0] > pygame.display.get_surface().get_size()[0]):
            x = pygame.display.get_surface().get_size()[
                0] - self.camera_size[0]
        if (new_pos[1] + self.camera_size[1] > pygame.display.get_surface().get_size()[1]):
            y = pygame.display.get_surface().get_size()[
                1] - self.camera_size[1]
        self.camera_pos = (x, y)


class AddPanel(Panel):
    def __init__(self, x, y, width, height, img):
        Panel.__init__(self, x, y, width, height, img)
        self.top = 0
        self.max = len(monster_names)
        self.sorted_names = list()
        self.sorted_ids = list()
        self.word = ""
        self.pre_word = ""
        self.update_text()
        self.update_quantity()
        self.button_up = pygame.rect.Rect(1260, 441, 100, 100)
        self.button_down = pygame.rect.Rect(1260, 586, 100, 100)
        rectan = pygame.rect.Rect(x+25, y+122, 644, 115)
        self.button_tokens = (rectan, rectan.move(
            0, 115), rectan.move(0, 230), rectan.move(0, 345))

    def sort_names(self, monster_names):
        word = self.word

        def word_similarity(test):
            return test[0].lower() .find(word.lower())
        id = 0
        if len(self.word) == 0 or len(self.word) < len(self.pre_word):
            self.sorted_names.clear()
            self.sorted_ids.clear()
            for mn in monster_names:
                if self.word.lower() in mn.lower() or self.word == "":
                    self.sorted_names.append(mn)
                    self.sorted_ids.append(id)
                id += 1
        elif self.pre_word != self.word:
            to_remove = list()
            for mn in self.sorted_names:
                if not self.word.lower() in mn.lower():
                    to_remove.append(id)

                id += 1
            for i in range(len(to_remove)-1, -1, -1):
                self.sorted_names.pop(to_remove[i])
                self.sorted_ids.pop(to_remove[i])

        if len(self.sorted_names) > 0 and len(self.word) > 0:
            self.sorted_names, self.sorted_ids = (list(t) for t in zip(
                *sorted(zip(self.sorted_names, self.sorted_ids), key=word_similarity)))
        self.pre_word = self.word

    def update_text(self):
        self.top = 0
        self.sort_names(monster_names)
        name = font_search.render(str(self.word), True, (0, 0, 0))
        nameRect = name.get_rect()
        nameRect.move_ip(30, 76)
        pygame.draw.rect(self.surf, (255, 255, 255),
                         (nameRect.x, nameRect.y, 635, 27))
        self.surf.blit(name, nameRect)
        pygame.draw.rect(self.surf, (0, 0, 0), (nameRect.right +
                                                3, nameRect.y, 3, nameRect.height - 3))
        self.update_images()

    def update_images(self):
        size = 110
        rect = pygame.rect.Rect((25, 122, 664, 460))
        pygame.draw.rect(self.surf, (255, 255, 255), rect)
        # Draw tokens
        for i in range(self.top, 4 + self.top):
            if i >= len(self.sorted_names):
                break
            j = i - self.top
            self.surf.blit(pygame.transform.scale(monster_icons[self.sorted_ids[i]], (size, size)),
                           rect.move(0, j * (size + 5) + 2))
            name = font_search.render(
                str(self.sorted_names[i]), True, icon_text_color)
            self.surf.blit(name, rect.move(
                size + 20, j * (size + 5) + size / 3 + 2))

        for i in range(0, 5):
            pygame.draw.line(self.surf, (0, 0, 0), (rect.x, rect.y + i * (size + 5)),
                             (rect.right, rect.y + i * (size + 5)))

    def check_mouse_click(self, mouse):
        if self.button_up.collidepoint(mouse) and self.top > 0:
            self.top -= 1
        elif self.button_down.collidepoint(mouse) and self.top < len(self.sorted_names) - 1:
            self.top += 1
        else:
            for i in range(0, 4):
                if self.button_tokens[i].collidepoint(mouse):
                    if i + self.top >= len(self.sorted_names):
                        break
                    index = i + self.top
                    add_token(self.sorted_names[index],
                              self.sorted_ids[index], quantity)
            return
        self.update_images()

    def update_quantity(self):
        rect = pygame.rect.Rect((699, 516, 93, 43))
        pygame.draw.rect(self.surf, (255, 255, 255), rect)
        name = font_search.render(str(quantity), True, (0, 0, 0))
        nameRect = name.get_rect()
        nameRect.move_ip(705, 524)
        self.surf.blit(name, nameRect)


# Loads for the campaign
def load_player_data(file_name, names, pc_images):
    try:
        file = open("Campaigns/"+file_name+"/Player_Names")
        for line in file:
            if line[-1] == '\n':
                line = line[:-1]
            names.append(line.split('.')[0])
            pc_images.append(pygame.image.load(
                "Campaigns/"+file_name+"/Player_Icons/" + line))
        return True
    except OSError:
        print("File doesn't exist !")
        return False


def load_monster_data(names, icons):
    file = open("Monster_Info")
    total_monsters = sys.argv[2]
    loaded_files = 0
    for line in file:
        loaded_files += 1
        print(loaded_files, " / ", total_monsters, end="\r")
        if line[-1] == '\n':
            line = line[:-1]
        names.append(line.split('.')[0])
        icons.append(pygame.image.load("Monster_Database/" + line))


def produce_empty_greed(width, height, grid_len):
    surf = pygame.Surface((width, height))
    surf.fill((123, 255, 90))
    surf.set_colorkey((123, 255, 90))
    for y in range(0, height, grid_len):
        pygame.draw.line(surf, grid_color, (0, y), (width, y))

    for x in range(0, width, grid_len):
        pygame.draw.line(surf, grid_color, (x, 0), (x, height))

    return surf


def swap_pen_color():
    if pen_color == (0, 0, 0):
        return empty_board_color
    return 0, 0, 0


def move_grid(grid_x, grid_y):
    grid_x += old_pos[0] - new_pos[0]
    grid_y += old_pos[1] - new_pos[1]
    if grid_x < 0:
        grid_x = 0
    elif grid_x + SCREEN_WIDTH > grid_width:
        grid_x = grid_width - SCREEN_WIDTH
    if grid_y < 0:
        grid_y = 0
    elif grid_y + SCREEN_HEIGHT > grid_height:
        grid_y = grid_height - SCREEN_HEIGHT
    return grid_x, grid_y


def add_token(monster_names, id, count):
    monster_size = GRID_SIZE
    for i in range(1, count+1):
        pc.add(ImageIcon(int(grid_x / monster_size + 1) * monster_size,
                         int((monster_size + grid_y) / monster_size) *
                         monster_size, monster_size,
                         monster_size,
                         monster_names,  str(monster_counter[id]), monster_icons[id]))
        monster_counter[id] += 1
        monster_counter_alive[id] += 1


pygame.init()
pygame.display.set_caption('D&D Board Simulator V0.1')

# Fonts
font = pygame.font.Font('freesansbold.ttf', 14)
font_search = pygame.font.Font('freesansbold.ttf', 26)

# Colors
icon_text_color = (0, 255, 0)
empty_board_color = (224, 211, 175)

success = False
while not success:
    # Load Player data from file
    player_icons = list()
    player_names = list()
    # campaign_name = input("Choose campaign : ")

    campaign_name = sys.argv[1]
    success = load_player_data(campaign_name, player_names, player_icons)

# Load monster data
monster_names = list()
monster_icons = list()
load_monster_data(monster_names, monster_icons)
monster_counter_alive = [0] * len(monster_names)
monster_counter = [1] * len(monster_names)

# Init Screen
if sys.argv[4] == "fullscreen":
    flags = pygame.NOFRAME | DOUBLEBUF
else:
    flags = DOUBLEBUF

os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
info = pygame.display.Info()
# and create a borderless window that's as big as the entire screen
screen = pygame.display.set_mode((info.current_w, info.current_h), flags)

screen = pygame.display.set_mode((0, 0), flags)
image_ico = pygame.image.load("Assets/DnD Logo.png")
pygame.display.set_icon(image_ico)


# Final variables
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.get_surface().get_size()
GRID_SIZE = int(sys.argv[3])

# Init grid system
grid_color = (0, 0, 0)
grid_cooldown = 60
grid_cooldown_timer = 0
grid_width = SCREEN_WIDTH * 5
grid_height = SCREEN_HEIGHT * 5
grid_x = grid_width / 2
grid_y = grid_height / 2
grid = produce_empty_greed(grid_width, grid_height, GRID_SIZE)
grid_values = [[0] * int(grid_width / GRID_SIZE + 0.5)] * \
    int(grid_height / GRID_SIZE + 0.5)

# Drawing Canvas
canvas = pygame.Surface((grid_width, grid_height))
canvas.fill(empty_board_color)
circle_size = 13
pen_color = (0, 0, 0)

# Load Player Characters
pc = pygame.sprite.Group()
for i in range(0, len(player_names)):
    pc.add(
        ImageIcon(int(grid_x / GRID_SIZE) * GRID_SIZE, int((i * GRID_SIZE + grid_y) / GRID_SIZE) * GRID_SIZE, GRID_SIZE,
                  GRID_SIZE, player_names[i], "", player_icons[i]))

# While this is true the game runs
running = True

old_pos = pygame.mouse.get_pos()
old_adjusted_pos = pygame.mouse.get_pos()
pc_count = len(pc)
focused_icon = -1

# Quantity
quantity = 1

add_panel_active = False
random_grid_color = False
add_panel_width, add_panel_height = 800, 600
add_panel = AddPanel(SCREEN_WIDTH / 2 - add_panel_width / 2, SCREEN_HEIGHT / 2 - add_panel_height / 2, add_panel_width,
                     add_panel_height, "Add Panel.png")
add_panel.sort_names(monster_names)

# Add camera to panel
pygame.camera.init()
capture_camera_thread = WebcamCapture()
capture_camera_thread.start()

# Undo Redo
paint_history = list()
while running:
    grid_cooldown_timer += 1
    new_pos = pygame.mouse.get_pos()
    adjust_pos = (new_pos[0] + grid_x, new_pos[1] + grid_y)

    if capture_camera_thread.camera_is_movable:
        capture_camera_thread.move_camera(new_pos)

    # For loop through the event queue
    for event in pygame.event.get():
        # Check for KEYDOWN event
        if event.type == KEYDOWN:
            # If the Esc key is pressed, then exit the main loop

            if event.key == pygame.K_DELETE:
                new_grid_col = (0, 0, 0)
                if not random_grid_color:
                    new_grid_col = (random.randrange(100, 255), random.randrange(
                        100, 255), random.randrange(100, 255))
                pygame.transform.threshold(grid.subsurface(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - 100),
                                           grid.subsurface(
                                               0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - 100), new_grid_col,
                                           (10, 10, 1), grid_color,
                                           1, None, True)
                grid_color = new_grid_col
                grid = produce_empty_greed(grid_width, grid_height, GRID_SIZE)
                random_grid_color = not random_grid_color
            elif event.key == K_ESCAPE:
                if not add_panel_active:
                    capture_camera_thread.running = False
                    running = False
                    exit(0)
                else:
                    add_panel_active = False
                    quantity = 1
                    add_panel.update_text()
                    # close panel
            elif add_panel_active:
                if event.key == pygame.K_RETURN:
                    add_panel.word = ""
                    quantity = 1
                elif event.key == pygame.K_BACKSPACE:
                    add_panel.word = add_panel.word[:-1]
                elif event.key == pygame.K_LEFTBRACKET:
                    if quantity > 1:
                        quantity -= 1
                        add_panel.update_quantity()
                elif event.key == pygame.K_RIGHTBRACKET:
                    if quantity < 10:
                        quantity += 1
                        add_panel.update_quantity()
                elif ('Z' >= event.unicode >= 'A' or 'z' >= event.unicode >= 'a' or event.unicode == ' ' or event.unicode == '-' or '9' >= event.unicode >= '0') and len(
                        add_panel.word) < 30:
                    add_panel.word += event.unicode
                add_panel.update_text()
            elif event.key == pygame.K_z and not add_panel_active:
                print("d")
            elif event.key == pygame.K_a and not add_panel_active:
                add_panel_active = True
                quantity = 1
                add_panel.word = ""
                add_panel.update_quantity()
                add_panel.update_text()
            elif event.key == pygame.K_d and not add_panel_active:
                count = 0
                for ic in pc:
                    if ic.rect.collidepoint(adjust_pos) and count > pc_count - 1:
                        for i in range(0, len(monster_names)):
                            if ic.name == monster_names[i]:
                                monster_counter_alive[i] -= 1
                                if monster_counter_alive[i] == 0:
                                    monster_counter[i] = 1

                        pc.remove(ic)
                        break
                    count += 1
            elif event.key == pygame.K_c and not add_panel_active:
                canvas.fill(empty_board_color)
            elif event.key == pygame.K_l and not add_panel_active:
                pen_color = swap_pen_color()
            elif event.key == pygame.K_i and not add_panel_active:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    capture_camera_thread.camera_is_movable = True
                else:
                    capture_camera_thread.turn_camera()
        elif event.type == KEYUP:
            if event.key == pygame.K_i:
                capture_camera_thread.camera_is_movable = False
        # Check for QUIT event. If QUIT, then set running to false.
        elif event.type == QUIT:
            capture_camera_thread.running = False
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 5:
                if add_panel.top < len(add_panel.sorted_names) - 1:
                    add_panel.top += 1
                    add_panel.update_images()
            elif event.button == 4:
                if add_panel.top > 0:
                    add_panel.top -= 1
                    add_panel.update_images()

            if event.button == 1:
                if not add_panel_active:
                    count = 0
                    for ic in pc:
                        if ic.rect.collidepoint(adjust_pos):
                            focused_icon = count
                            break
                        count += 1
                elif add_panel_active and not add_panel.rect.collidepoint(new_pos):
                    add_panel_active = False
                    quantity = 1
                    add_panel.update_text()
                elif event.button == 1 and add_panel_active:
                    add_panel.check_mouse_click(new_pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if focused_icon != -1 and not add_panel_active:
                count = 0
                for ic in pc:
                    if count == focused_icon:
                        ic.rect.x = int(ic.rect.centerx /
                                        GRID_SIZE) * GRID_SIZE
                        ic.rect.y = int(ic.rect.centery /
                                        GRID_SIZE) * GRID_SIZE
                        break
                    count += 1
            focused_icon = -1

    # Move grid
    pressed = pygame.mouse.get_pressed()
    if not add_panel_active:
        if pressed[1]:
            grid_x, grid_y = move_grid(grid_x, grid_y)
        if pressed[0] and focused_icon != -1:
            count = 0
            for ic in pc:
                if count == focused_icon:
                    ic.rect.x -= old_pos[0] - new_pos[0]
                    ic.rect.y -= old_pos[1] - new_pos[1]
                    if ic.rect.x < 0:
                        ic.rect.x = 0
                    elif ic.rect.x + ic.rect.width > grid_width:
                        ic.rect.x = grid_width - ic.rect.width
                    if ic.rect.y < 0:
                        ic.rect.y = 0
                    elif ic.rect.y + ic.rect.height > grid_height:
                        ic.rect.y = grid_height - ic.rect.height
                    break
                count += 1
        if pressed[2]:
            steps = max(abs(adjust_pos[0] - old_adjusted_pos[0]),
                        abs(adjust_pos[1] - old_adjusted_pos[1]))
            if steps < 1:
                steps = 1
            dx = (adjust_pos[0] - old_adjusted_pos[0]) / steps
            dy = (adjust_pos[1] - old_adjusted_pos[1]) / steps
            xPos = old_adjusted_pos[0]
            yPos = old_adjusted_pos[1]
            new_move = PaintMove()
            for _ in range(int(steps)):
                xPos += dx
                yPos += dy
                new_move.add_spot(round(xPos - circle_size / 5),
                                  round(yPos - circle_size / 5), pen_color == empty_board_color)
                pygame.draw.circle(canvas, pen_color, (round(xPos - circle_size / 5), round(yPos - circle_size / 5)),
                                   circle_size)
    old_pos = new_pos
    old_adjusted_pos = adjust_pos

    # Clear board
    screen.blit(canvas, grid.get_rect().move(-grid_x, -grid_y))

    # Draw Icons
    count = 0
    for ic in pc:
        if ic.visible:
            if focused_icon != count:
                screen.blit(ic.surf, ic.rect.move(-grid_x, -grid_y))
        count += 1

    # Draws Grid
    screen.blit(grid, grid.get_rect().move(-grid_x, -grid_y))

    count = 0
    for ic in pc:
        if ic.visible:
            if focused_icon == count:
                screen.blit(ic.surf, ic.rect.move(-grid_x, -grid_y))
                break
        count += 1

    if add_panel_active:
        screen.blit(add_panel.surf, add_panel.rect)

    # draw camera input
    if capture_camera_thread.webcam_is_visible:
        screen.blit(capture_camera_thread.webcam_image, capture_camera_thread.camera_pos,
                    (0, 0, capture_camera_thread.camera_size[0], capture_camera_thread.camera_size[1]))
        #webcam_image = webcam.get_image()

    # Update the display
    pygame.display.flip()

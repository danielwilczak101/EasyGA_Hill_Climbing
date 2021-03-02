"""
--HOW IT WORKS--
left click to add a point
right click to remove the last point
press ENTER to print all the points

You have to move the window to see the end of the circuit

copy and past the points list into the cimb racing game

(you can change the variable should_import to false to not import points)
"""

# Setup Python ----------------------------------------------- #
import pygame
import sys
import os
import random



# Setup pygame/window ---------------------------------------- #
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,32) # windows position
pygame.init()
pygame.display.set_caption('Circuit maker for Climb racing')
SCREEN_WIDTH = 1200 * 5
SCREEN_HEIGHT = 680
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),0,32)

mainClock = pygame.time.Clock()

# Fonts ------------------------------------------------------- #
main_font = pygame.font.SysFont("coopbl", 22)


# Variables ------------------------------------------------------- #
should_import = True

if should_import:
    all_points = [[-20, SCREEN_HEIGHT], [-20, 30], [26, 30], [26, 470], [152, 470], [254, 494], [352, 517], [450, 531], [521, 523],
                [581, 506], [634, 481], [682, 456], [736, 427], [813, 422], [908, 430], [992, 461], [1037, 494],
                [1115, 530], [1187, 529], [1250, 503], [1275, 490], [1339, 478], [1437, 480], [1513, 504], [1578, 540],
                [1638, 570], [1721, 563], [1801, 544], [1849, 509], [1889, 457], [1923, 432], [2011, 412], [2093, 434],
                [2173, 466], [2192, 507], [2259, 552], [2331, 568], [2413, 572], [2475, 559], [2574, 486], [2594, 444],
                [2601, 418], [2646, 389], [2707, 383], [2797, 395], [2873, 421], [2902, 464], [2933, 510], [2979, 548],
                [3026, 540], [3091, 513], [3128, 471], [3192, 446], [3283, 455], [3329, 484], [3348, 538], [3382, 591],
                [3442, 598], [3512, 588], [3563, 564], [3631, 522], [3683, 474], [3745, 419], [3784, 358], [3806, 307],
                [3825, 258], [3858, 213], [3887, 192], [3918, 180], [3956, 179], [4014, 173], [4073, 174], [4171, 180],
                [4236, 185], [4236, SCREEN_HEIGHT]]
else:
    all_points = []
    # Constantes -------------------------------------------------------#
START_TIME = pygame.time.get_ticks()

# Classes --------------------------------------------------------- #


# Creation ---------------------------------------------------------#


# Functions ------------------------------------------------------- #
def draw_points():
    if len(all_points) >= 2:
        pygame.draw.lines(SCREEN, (21,144,124), False, all_points)

def redraw():
    SCREEN.fill((22,22,22))
    fps_label = main_font.render(f"FPS: {int(mainClock.get_fps())}", 1, (255,200,20))
    SCREEN.blit(fps_label, (5,5))

    # draw all the points from the all_points list (and make lines)
    draw_points()


def buttons():
    global all_points
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_RETURN:
                print(all_points)
            if event.key == pygame.K_r:
                if len(all_points) > 0:
                    all_points.pop(-1)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                all_points.append(list(pygame.mouse.get_pos()))
            elif event.button == 3:
                if len(all_points) > 0:
                    all_points.pop(-1)


def update():
    pygame.display.update()
    mainClock.tick(90)


# Loop ------------------------------------------------------- #
while True:
    # mouse_x, mouse_y = pygame.mouse.get_pos()
    # pygame.mouse.get_pressed()

    time = (pygame.time.get_ticks() - START_TIME)/1000

    # draw --------------------------------------------- #
    redraw()

    # Buttons ------------------------------------------------ #
    buttons()

    # Update ------------------------------------------------- #
    update()

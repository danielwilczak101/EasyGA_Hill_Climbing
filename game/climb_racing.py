# Setup Python ----------------------------------------------- #
import pygame
import pymunk
import pymunk.pygame_util
import sys
import os
import random
import time
import math

# Setup pygame/window ---------------------------------------- #
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,32) # windows position
pygame.init()
pygame.display.set_caption('Climb racing')
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 680
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),0,32)
mainClock = pygame.time.Clock()


# Fonts ------------------------------------------------------- #
SMALL_FONT = pygame.font.SysFont("coopbl", 32)
BIG_FONT = pygame.font.SysFont("coopbl", 60)


# Variables ------------------------------------------------------- #
draw_fps = True # if true will show the frame / sec
sf = pymunk.ShapeFilter(group=1) # all object in this group will not collide together
draw_options = pymunk.pygame_util.DrawOptions(SCREEN)
draw_options.flags ^= draw_options.DRAW_CONSTRAINTS
draw_options.flags ^= draw_options.DRAW_COLLISION_POINTS


# Constantes -------------------------------------------------------#
NB_CARS = 10 # the number of cars for one generation
CHASSI_SIZE = (64*2, 39*2) # size of the chassi car size
SKY_COLOR = (66, 227, 245) # color of the background
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]


# Load Sprites-----------------------------------------------------#
file_path = os.path.join(MAIN_DIR, 'Assets')
wheel_sprite = pygame.image.load(f"{file_path}/Wheel.png").convert_alpha()
chassi_sprite = pygame.image.load(f"{file_path}/Body.png").convert_alpha()
chassi_sprite = pygame.transform.smoothscale(chassi_sprite, (CHASSI_SIZE))
    # load and make the dirt surface
dirt_sprite = pygame.image.load(f"{file_path}/dirt.png").convert_alpha()
dirt_sprite = pygame.transform.smoothscale(dirt_sprite, (SCREEN_WIDTH//2, SCREEN_WIDTH//2))
dirt_surface = pygame.Surface((SCREEN_WIDTH, dirt_sprite.get_height()))
dirt_surface.blit(dirt_sprite, (0,0))
dirt_surface.blit(dirt_sprite, (dirt_sprite.get_width(),0))

# Classes --------------------------------------------------------- #
class World:
    """This class create a World with a circuit."""

    def __init__(self):
        self.dirt_pos = 0


    def reset(self):
        """reset the world"""
        global space

        space = pymunk.Space()
        space.gravity = (0, 100)
        space.sleep_time_threshold = 1 # The time a body must remain idle in order to fall asleep

        self.total_offset = 0
        self.create_level()


    def create_level(self):
        """Convert a list of points to a the level circuit"""
        thickness = 10 # thickness of the grass
        friction = 2 # friction of the grass

        # Points to create the map.
        self.points = [[-20,SCREEN_HEIGHT]]
        for x in range(400):
            self.points.append([(x-1)*20,55*math.sin(x/6)+470])

        self.points[-1][1] = SCREEN_HEIGHT


        # create the circuit
        for i in range(1, len(self.points)):
            body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
            floor = pymunk.Segment(body, (self.points[i-1][0], self.points[i-1][1]), (self.points[i][0], self.points[i][1]), thickness)
            #floor = pymunk.Segment(body, (x+points[i-1][0]*2, y+points[i-1][1]), (x+points[i][0]*2, y+points[i][1]), thickness)
            floor.friction = friction
            floor.elasticity = 0.5
            space.add(body, floor)

        # create the points for the sky
        self.sky_points = self.points
        self.sky_points.insert(0, ([0,0]))
        self.sky_points.append([self.points[-1][0]+SCREEN_WIDTH,SCREEN_HEIGHT])
        self.sky_points.append([self.sky_points[-1][0],0])



    def draw_ground(self, offset):
        """draw the dirt ground"""
        self.dirt_pos -= offset
        if self.dirt_pos < -dirt_surface.get_width():
            self.dirt_pos += dirt_surface.get_width()
        SCREEN.blit(dirt_surface, (self.dirt_pos, SCREEN_HEIGHT-dirt_surface.get_height())) #draw the first dirt image
        SCREEN.blit(dirt_surface, (self.dirt_pos+dirt_surface.get_width(), SCREEN_HEIGHT-dirt_surface.get_height())) #draw the second dirt image



    def draw_sky(self):
        """draw the sky"""
        pygame.draw.polygon(SCREEN, SKY_COLOR, self.sky_points)



    def screen_scroll(self, cars): # center the level on the best car
        """Make the screen scroll to allways have the first car center"""
        offset = 0
        for car in cars:
            if car.chassi.body.position.x > offset  + SCREEN_WIDTH//2:
                offset = car.chassi.body.position.x - SCREEN_WIDTH//2
        for el in space.bodies:
            el.position = (el.position.x-offset, el.position.y)

        self.total_offset += offset
        return  offset



class Generation:
    """Handle the current generation of cars"""

    def __init__(self, cars_nb):
        # list with all the cars
        self.cars = [self.create_car() for i in range(cars_nb)]


    def create_car(self):
        """Create a car with random wheel size"""
        wheel_size = (random.randint(20, 50), random.randint(20, 50))
        return Car(wheel_size)


    def draw_cars(self):
        """Draw all the cars"""
        for car in self.cars:
            car.draw()


    def draw_best_score(self, offset):
        """Draw the best score (distance)"""
        best_score = float("-inf")
        for car in generation.cars:
            if car.score > best_score:
                best_score = int(car.score)

        score_label = BIG_FONT.render(f"Best score : {best_score}", 1, (131,140,140))
        SCREEN.blit(score_label, (5,5))



class Chassi:
    """Create the chassi of the car"""

    def __init__(self, pos):
        self.sprite = chassi_sprite
        self.width = chassi_sprite.get_width()-4 # width of the chassi
        self.height = chassi_sprite.get_height()-30 # height of the chassi
        mass = 120 # mass of the chassi
        moment = pymunk.moment_for_box(mass, ( self.width, self.height))

        self.body = pymunk.Body(mass, moment) # mass, inertia
        self.body.position = pos

        shape = pymunk.Poly.create_box(self.body, ( self.width, self.height)) # Create a box shape and attach to body
        shape.color = (SKY_COLOR[0], SKY_COLOR[1], SKY_COLOR[2], 0)
        shape.filter = sf # to not collide with other cars
        shape.friction = 0.3
        # add the chassi to the space
        space.add(self.body, shape)


    def draw(self):
        """Draw the chassi on the screen"""
        img = rot_center(self.sprite, self.body.angle)
        SCREEN.blit(img, (self.body.position.x-img.get_width()//2, self.body.position.y-img.get_height()//2))



class Wheel:
    """Create a wheel that get connected with the chassi"""
    def __init__(self, radius, chassi, direction):
        self.color = (100,220,123)

        self.radius = radius
        self.sprite = pygame.transform.smoothscale(wheel_sprite, (radius*2, radius*2))

        mass = 30
        moment = pymunk.moment_for_circle(mass, radius//2, radius)

        self.body = pymunk.Body(mass, moment) # mass, inertia

        if direction == "left": # for the left wheel
            pos = (-chassi.width/2 + chassi.body.position[0], chassi.height/2 + chassi.body.position[1])
        elif direction == "right": # for the right wheel
            pos = (chassi.width/2 + chassi.body.position[0], chassi.height/2 + chassi.body.position[1])
        self.body.position = pos

        shape = pymunk.Circle(self.body, self.radius)
        shape.elasticity = 0.8
        shape.friction = 1.5
        shape.color = (SKY_COLOR[0], SKY_COLOR[1], SKY_COLOR[2], 0)

        shape.filter = sf # to not collide with other cars

        space.add(self.body, shape)


    def draw(self):
        """Draw the wheel image at the wheel position on the screen"""
        img = rot_center(self.sprite, self.body.angle)
        SCREEN.blit(img, (self.body.position.x-img.get_width()//2, self.body.position.y-img.get_height()//2))



class Joint:
    """Create a joint to conect the wheel and the chassi of the car"""

    def __init__(self, wheel, chassi, direction):
        self.wheel = wheel
        if direction == "left":
            pos = (-chassi.width/2, chassi.height/2)
        if direction == "right":
            pos = (chassi.width/2, chassi.height/2)

        joint =  pymunk.PivotJoint(chassi.body, self.wheel.body, pos, (0,0))

        space.add(joint)



class Car:
    """Create a car"""
    def __init__(self, wheel_size):
        self.max_speed = 8
        self.start_pos = (200, 100)
        speed = random.randint(-3, 5) # default speed of the car
        self.score = 0

        self.brake_speed = 1 # the speed of the car will decrease of the brake_speed evry time the car brake
        self.accelerate_speed = 1 # the speed of the car will increase of the accelerate_speed evry time the car accelerate
        # create the chassi
        self.chassi = Chassi(self.start_pos)
        # create the 2 wheels
        self.wheels = [
        Wheel(wheel_size[0], self.chassi, "left"),
        Wheel(wheel_size[1], self.chassi, "right")
            ]
        # create the joints between the chassi and the 2 wheels
        Joint(self.wheels[0], self.chassi, "left")
        Joint(self.wheels[1], self.chassi, "right")
        # make the left wheel motorize
        self.motorJoint = pymunk.SimpleMotor(self.wheels[0].body, self.chassi.body, speed)
        space.add(self.motorJoint)


    def brake(self):
        """Make the car brake"""
        self.motorJoint.rate -= self.brake_speed
        if float(self.motorJoint.rate) < -self.max_speed: # if already at min speed
            self.motorJoint.rate = -self.max_speed

    def accelerate(self):
        """Make the car accelerate"""
        self.motorJoint.rate += self.accelerate_speed
        if float(self.motorJoint.rate) > self.max_speed: # if already at max speed
            self.motorJoint.rate = self.max_speed


    def draw(self):
        """Draw the car"""
        self.chassi.draw()
        for wheel in self.wheels:
            wheel.draw()



    def update_score(self, offset):
        """Update the score of the car"""
        self.score = world.total_offset + self.chassi.body.position.x- self.start_pos[0]



# Functions ------------------------------------------------------- #
def create_generation(NB_CARS):
    """Create a new generation of cars"""
    global generation
    world.reset()
    generation = Generation(NB_CARS)


def rot_center(image, angle, angle_type="radian"):
    """make an image rotate around his center point"""

    if angle_type == "radian": # convert the angle in degree
        angle = -angle * 360 / (2*3.1)

    loc = image.get_rect().center
    rot_image = pygame.transform.rotate(image, angle)
    rot_image.get_rect().center = loc
    return rot_image


def redraw():
    """draw all the stuff on the screen"""

    SCREEN.fill(SKY_COLOR)


    offset = world.screen_scroll(generation.cars)

    for car in generation.cars:
        car.update_score(offset)

    # make the move the ground
    for pt in world.points:
        pt[0] -= offset

    world.draw_ground(offset)
    world.draw_sky()
    space.debug_draw(draw_options)

    # draw the cars
    generation.draw_cars()

    # draw the best score
    generation.draw_best_score(offset)

    # drawt the number of Frame/sec
    if draw_fps:
        fps_label = SMALL_FONT.render(f"FPS: {int(mainClock.get_fps())}", 1, (22,22,22))
        SCREEN.blit(fps_label, (SCREEN_WIDTH-fps_label.get_width(), 5))


def buttons():
    """check for user key / button input"""
    global generation

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key == pygame.K_UP:
                for car in generation.cars:
                    car.accelerate()

            if event.key == pygame.K_DOWN:
                for car in generation.cars:
                    car.brake()

            if event.key == pygame.K_SPACE: # create a new generation if user press on "Space"
                create_generation(NB_CARS)


def update():
    """update all the screen"""
    space.step(1/32)
    pygame.display.update()
    mainClock.tick(60)



# Creation ---------------------------------------------------------#
world = World()
# create the first generation
create_generation(NB_CARS)


# Loop ------------------------------------------------------- #
while True:

    # draw --------------------------------------------- #
    redraw()

    # Buttons ------------------------------------------------ #
    buttons()

    # Update ------------------------------------------------- #
    update()

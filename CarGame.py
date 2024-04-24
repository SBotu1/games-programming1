import pygame
from pygame.locals import *
import random
import time

pygame.init()
pygame.mixer.init()

# window creation
width = 500
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Road Rage')

# colours
gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)

# New colors
bg_color = (0, 102, 204)  # Background color
car_color = (255, 255, 0)  # Car color
crash_color = (255, 0, 0)  # Crash color
text_color = (255, 255, 255)  # Text color

# road plus marker sizes
road_width = 300
marker_width = 10
marker_height = 50

# lane coordinates
left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

# road and edge markers
road = (100, 0, road_width, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)

# for animating movement of the lane markers
lane_marker_move_y = 0

# player's starting coordinates
player_x = 250
player_y = 400

# frame settings
clock = pygame.time.Clock()
fps = 60

# game settings
game_over = False
speed = 2
score = 0

# Timer
start_time = 0
elapsed_time = 0

# Load background music
pygame.mixer.music.load('Assets/backgroundMusic.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # -1 means loop indefinitely

# Load sound effects
collision_sound = pygame.mixer.Sound('Assets/explosion.wav')
collision_sound.set_volume(0.5)
overtake_sound = pygame.mixer.Sound('Assets/carOvertake.wav')
overtake_sound.set_volume(0.5)

# Car asset classes
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, images, x, y):
        pygame.sprite.Sprite.__init__(self)
        # scale the image down, so it's not wider than the lane
        image_scale = 45 / images.get_rect().width
        new_width = images.get_rect().width * image_scale
        new_height = images.get_rect().height * image_scale
        self.image = pygame.transform.scale(images, (int(new_width), int(new_height)))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        images = pygame.image.load('Assets/mainCar.png')
        super().__init__(images, x, y)

# sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# create the player's car
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

# load the vehicle images
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = [pygame.image.load('Assets/' + image_filename) for image_filename in image_filenames]

# load the crash image
crash = pygame.image.load('Assets/crash.png')
crash_rect = crash.get_rect()

# game loop
running = True
while running:

    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        # move the player's car using the left/right arrow keys
        if event.type == KEYDOWN:

            if event.key == K_LEFT and player.rect.center[0] > left_lane:
                player.rect.x -= 100
                overtake_sound.play()
            elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
                player.rect.x += 100
                overtake_sound.play()

            # restart game
            if game_over and event.key == K_y:
                game_over = False
                score = 0
                speed = 2
                start_time = time.time()
                elapsed_time = 0
                vehicle_group.empty()
                player.rect.center = [player_x, player_y]

    # check for collisions
    if not game_over:
        for vehicle in vehicle_group:
            if pygame.sprite.collide_rect(player, vehicle):
                game_over = True
                elapsed_time = time.time() - start_time
                crash_rect.center = [player.rect.center[0], (player.rect.top + vehicle.rect.bottom) / 2]
                collision_sound.play()
                break

    # draw the background
    screen.fill(bg_color)

    # draw the road
    pygame.draw.rect(screen, gray, road)

    # draw the edge markers
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)

    # draw the lane markers
    lane_marker_move_y += speed * 2
    if lane_marker_move_y >= marker_height * 2:
        lane_marker_move_y = 0
    for y in range(marker_height * -2, height, marker_height * 2):
        pygame.draw.rect(screen, white,
                         (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white,
                         (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

    # draw the player's car
    player_group.draw(screen)

    # add a vehicle
    if len(vehicle_group) < 2:

        # ensure there's enough gap between vehicles
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height * 1.5:
                add_vehicle = False

        if add_vehicle:
            # select a random lane
            lane = random.choice(lanes)

            # select a random vehicle image
            image = random.choice(vehicle_images)
            vehicle = Vehicle(image, lane, height / -2)
            vehicle_group.add(vehicle)

    # make the vehicles move
    for vehicle in vehicle_group:
        vehicle.rect.y += speed

        # remove vehicle once it goes off-screen
        if vehicle.rect.top >= height:
            vehicle.kill()

            # add to score
            score += 1

            # speed up the game after passing 5 vehicles
            if score > 0 and score % 5 == 0:
                speed += 1

    # draw the vehicles
    vehicle_group.draw(screen)

    # display the score
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render('Score: ' + str(score), True, text_color)
    text_rect = text.get_rect()
    text_rect.center = (50, 400)
    screen.blit(text, text_rect)

    # display game over
    if game_over:
        screen.blit(crash, crash_rect)

        pygame.draw.rect(screen, crash_color, (0, 50, width, 100))

        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Game over. Play again? (Press Y)', True, text_color)
        text_rect = text.get_rect()
        text_rect.center = (width / 2, 100)
        screen.blit(text, text_rect)

        # display elapsed time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_str = '{:02}:{:02}'.format(minutes, seconds)
        elapsed_text = font.render('Time: {}'.format(time_str), True, text_color)
        elapsed_rect = elapsed_text.get_rect(center=(width / 2, 150))
        screen.blit(elapsed_text, elapsed_rect)

    # Update the display
    pygame.display.update()

pygame.quit()

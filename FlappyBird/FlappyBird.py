import pygame
import os
import random
import time

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
GROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
BIRD_IMAGES = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]

pygame.font.init()
SCORE_FONT = pygame.font.SysFont('arial', 50)

class Bird:
    IMGS = BIRD_IMAGES
    # rotation animations
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.angle = 0
        self.velocity = 0
        self.height = self.y
        self.time = 0
        self.image_count = 0
        self.image = self.IMGS[0]

    def jump(self) -> None:
        self.velocity = -10.5
        self.time = 0
        self.height = self.y

    def move(self) -> None:
        # calculate the displacement
        self.time += 1
        displacement = 1.5 * (self.time**2) + self.velocity * self.time

        # restrict the displacement
        if displacement > 16:
            displacement = 16
        elif displacement < 0:
            displacement -= 2

        self.y += displacement

        # bird angle
        if displacement < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.ROTATION_VELOCITY

    def draw_bird(self, screen) -> None:
        # define which bird image will be used
        self.image_count += 1

        if self.image_count < self.ANIMATION_TIME:
            self.image = self.IMGS[0]
        elif self.image_count < (self.ANIMATION_TIME * 2):
            self.image = self.IMGS[1]
        elif self.image_count < (self.ANIMATION_TIME * 3):
            self.image = self.IMGS[2]
        elif self.image_count < (self.ANIMATION_TIME * 4):
            self.image = self.IMGS[1]
        elif self.image_count < (self.ANIMATION_TIME * 4) + 1:
            self.image = self.IMGS[0]
            self.image_count = 0

        # detect if the bird is falling
        if self.angle <= -80:
            self.image = self.IMGS[1]
            self.image_count = self.ANIMATION_TIME * 2

        # draw the image
        rotate_img = pygame.transform.rotate(self.image, self.angle)
        center_img_position = self.image.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotate_img.get_rect(center=center_img_position)
        screen.blit(rotate_img, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    DISTANCE = 200
    VELOCITY = 5

    def __init__(self, x: int) -> None:
        self.x = x
        self.height = 0
        self.top_position = 0
        self.base_position = 0
        self.TOP_PIPE = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.BASE_PIPE = PIPE_IMAGE
        self.passed = False
        self.set_height()

    def set_height(self) -> None:
        self.height = random.randrange(50, 450)
        self.top_position = self.height - self.TOP_PIPE.get_height()
        self.base_position = self.height + self.DISTANCE

    def move_pipe(self) -> None:
        self.x -= self.VELOCITY

    def draw_pipe(self, screen) -> None:
        screen.blit(self.TOP_PIPE, (self.x, self.top_position))
        screen.blit(self.BASE_PIPE, (self.x, self.base_position))

    def collide(self, bird) -> bool:
        bird_mask = bird.get_mask()
        top_pipe_mask = pygame.mask.from_surface(self.TOP_PIPE)
        base_pipe_mask = pygame.mask.from_surface(self.BASE_PIPE)

        top_distance = (self.x - bird.x, self.top_position - round(bird.y))
        base_distance = (self.x - bird.x, self.base_position - round(bird.y))

        top_point = bird_mask.overlap(top_pipe_mask, top_distance)
        base_point = bird_mask.overlap(base_pipe_mask, base_distance)

        if top_point or base_point:
            return True
        else:
            return False


class Ground:
    VELOCITY = 5
    WIDTH = GROUND_IMAGE.get_width()
    IMG = GROUND_IMAGE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.x1 + self.WIDTH

    def move_ground(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        elif self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw_ground(self, screen):
        screen.blit(self.IMG, (self.x1, self.y))
        screen.blit(self.IMG, (self.x2, self.y))


def draw_screen(screen, birds, pipes, ground, score):
    screen.blit(BACKGROUND_IMAGE, (0, 0))
    for bird in birds:
        bird.draw_bird(screen)
    for pipe in pipes:
        pipe.draw_pipe(screen)

    score_text = SCORE_FONT.render(f"Score: {score}", 1, (255, 255, 255))
    screen.blit(score_text, (SCREEN_WIDTH - 10 - score_text.get_width(), 10))
    ground.draw_ground(screen)
    pygame.display.update()


def main():
    birds = [Bird(230, 350)]
    ground = Ground(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    score = 0
    clock = pygame.time.Clock()

    while True:
        clock.tick(30)

        # user interaction
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for bird in birds:
                        bird.jump()

        # move game objects
        for bird in birds:
            bird.move()
        ground.move_ground()

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                    time.sleep(0.3)
                    quit()
                elif not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    add_pipe = True

            pipe.move_pipe()
            if pipe.x + pipe.TOP_PIPE.get_width() < 0:
                remove_pipes.append(pipe)

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))
        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > ground.y or bird.y < 0:
                birds.pop(i)
                time.sleep(0.3)
                quit()

        draw_screen(screen, birds, pipes, ground, score)


if __name__ == '__main__':
    main()
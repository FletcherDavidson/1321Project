import pygame
from constants import *
from level import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacleSprites, wallMask):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)  # Shrinks hitbox vertically
        self.mask = pygame.mask.from_surface(self.image)

        self.direction = pygame.math.Vector2()
        self.speed = 4
        self.obstacleSprites = obstacleSprites
        self.wallMask = wallMask  # Pass the wall mask from the camera group

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0
        if keys[pygame.K_a]:
            self.direction.x = -1
        elif keys[pygame.K_d]:
            self.direction.x = 1
        else:
            self.direction.x = 0

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

            # Move horizontally
            self.hitbox.x += self.direction.x * speed
            self.rect.x = self.hitbox.x
            self.collision("horizontal")

            # Move vertically
            self.hitbox.y += self.direction.y * speed
            self.rect.y = self.hitbox.y
            self.collision("vertical")

    def collision(self, direction):
        MAX_ATTEMPTS = 10  # Safety limit to prevent infinite loops
        playerMask = pygame.mask.from_surface(self.image)

        # Check for collision
        collisionPoint = self.wallMask.overlap(playerMask, (self.rect.x, self.rect.y))

        if collisionPoint:
            attempts = 0
            if direction == "horizontal":
                if self.direction.x > 0:  # Moving right
                    # Move player to the left of the wall
                    while (self.wallMask.overlap(playerMask, (self.rect.x, self.rect.y))
                           and attempts < MAX_ATTEMPTS):
                        self.hitbox.x -= 1
                        self.rect.x -= 1
                        attempts += 1
                elif self.direction.x < 0:  # Moving left
                    # Move player to the right of the wall
                    while (self.wallMask.overlap(playerMask, (self.rect.x, self.rect.y))
                           and attempts < MAX_ATTEMPTS):
                        self.hitbox.x += 1
                        self.rect.x += 1
                        attempts += 1

            if direction == "vertical":
                if self.direction.y > 0:  # Moving down
                    # Move player up
                    while (self.wallMask.overlap(playerMask, (self.rect.x, self.rect.y))
                           and attempts < MAX_ATTEMPTS):
                        self.hitbox.y -= 1
                        self.rect.y -= 1
                        attempts += 1
                elif self.direction.y < 0:  # Moving up
                    # Move player down
                    while (self.wallMask.overlap(playerMask, (self.rect.x, self.rect.y))
                           and attempts < MAX_ATTEMPTS):
                        self.hitbox.y += 1
                        self.rect.y += 1
                        attempts += 1

            # If we hit the max attempts, reset to previous position
            if attempts >= MAX_ATTEMPTS:
                if direction == "horizontal":
                    self.hitbox.x -= self.direction.x * self.speed
                    self.rect.x = self.hitbox.x
                else:
                    self.hitbox.y -= self.direction.y * self.speed
                    self.rect.y = self.hitbox.y

    def update(self):
        self.input()
        self.move(self.speed)
import pygame
from constants import *
from level import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacleSprites, wallMask, level):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, 0)  # Shrinks hitbox vertically
        self.mask = pygame.mask.from_surface(self.image)

        self.direction = pygame.math.Vector2()
        self.speed = 10
        self.obstacleSprites = obstacleSprites
        self.wallMask = wallMask  # Pass the wall mask from the camera group
        self.level = level

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
        self.checkCameraBoundaries()

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

    def checkCameraBoundaries(self):
        # Get the camera offset from the YSortCameraGroup
        camera_offset = self.level.visibleSprites.offset

        # Get the screen dimensions
        screen_width = self.level.visibleSprites.screenWidth
        screen_height = self.level.visibleSprites.screenHeight

        # Get the original map dimensions
        original_width = self.level.visibleSprites.originalWidth
        original_height = self.level.visibleSprites.originalHeight

        # Calculate the minimum and maximum positions based on the camera offset and screen dimensions
        min_x = camera_offset.x
        max_x = min_x + original_width - screen_width
        min_y = camera_offset.y
        max_y = min_y + original_height - screen_height

        # Clamp the player's position within the boundaries
        self.hitbox.clamp_ip(pygame.Rect(min_x, min_y, screen_width, screen_height))
        self.rect.topleft = self.hitbox.topleft

    def update(self):
        self.input()
        self.move(self.speed)
import pygame
from constants import *
from tile import Tile
from player import Player
from helpful import *
from random import choice
from dialog import Dialog, NPC


class Level:
    def __init__(self):
        # Get the display surface
        self.displaySurface = pygame.display.get_surface()

        # Sprite group setup
        self.visibleSprites = YSortCameraGroup()
        self.obstacleSprites = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()

        # Initialize dialog system before creating the player
        self.dialogSystem = Dialog()

        # Create player after dialog system
        self.player = Player((1000, 1000), [self.visibleSprites],
                             self.obstacleSprites,
                             self.visibleSprites.wallMask)

        # Create map and NPCs
        self.createNpcs()

        # Debug font
        self.debugFont = pygame.font.Font(None, 36)

    def checkDialogDistance(self):
        #Check if player has moved too far from NPC during dialog
        if self.dialogSystem.active and self.dialogSystem.currentNpc:
            if not self.dialogSystem.currentNpc.canInteract(self.player, self.visibleSprites.offset):
                self.dialogSystem.closeDialog()
                print("Dialog closed: Player moved too far from NPC") # Debug info

    def processDialogChoice(self, choice):
        # Handle dialog choices here
        print(f"Processing dialog choice: {choice}")
        # Add dialog choice handling logic here

    def createNpcs(self):
        # Create NPCs closer to starting position for testing
        npc1 = NPC((1100, 1000), [self.visibleSprites, self.npcs], "Artist")
        npc2 = NPC((900, 1000), [self.visibleSprites, self.npcs], "Marcus")
        npc3 = NPC((1500, 1000), [self.visibleSprites, self.npcs], "Lucius")
        print(f"Created NPCs. Total NPCs: {len(self.npcs)}")

    def checkNpcInteraction(self):
        keys = pygame.key.get_pressed()

        # Debug info
        debugY = 10
        debugTexts = [
            f"Player world pos: {self.player.rect.center}",
            f"NPCs in world: {len(self.npcs)}",
            f"Press E status: {keys[pygame.K_e]}"
        ]

        for text in debugTexts:
            debugSurf = self.debugFont.render(text, True, (255, 255, 0))
            self.displaySurface.blit(debugSurf, (10, debugY))
            debugY += 30

        for npc in self.npcs:
            if npc.canInteract(self.player, self.visibleSprites.offset):
                npc.drawInteractionPrompt(self.displaySurface, self.visibleSprites.offset)
                if keys[pygame.K_e]:
                    npc.startDialog(self.dialogSystem)

    def run(self):
        # Update and draw the game
        self.visibleSprites.customDraw(self.player)
        self.visibleSprites.update()

        # Check distance from NPC if in dialog
        if self.dialogSystem.active:
            self.checkDialogDistance()
        else:
            self.checkNpcInteraction()

        # Draw dialog on top of everything
        self.dialogSystem.draw(self.displaySurface)

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        # General set up
        super().__init__()
        self.displaySurface = pygame.display.get_surface()
        self.halfWidth = self.displaySurface.get_size()[0] // 2
        self.halfHeight = self.displaySurface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # Creating the ground
        self.floorSurf = pygame.image.load('../graphics/maps/CryptTest.png').convert_alpha()
        self.wallSurf = pygame.image.load('../graphics/maps/CryptCollideables.png').convert_alpha()
        self.propSurf = pygame.image.load('../graphics/maps/SolidProps.png').convert_alpha()
        self.interactableSurf = pygame.image.load('../graphics/maps/Interactables.png').convert_alpha()
        self.floorRect = self.floorSurf.get_rect(topleft=(0, 0))
        self.wallRect = self.wallSurf.get_rect(topleft=(0, 0))
        self.propRect = self.propSurf.get_rect(topleft=(0, 0))
        self.interactableRect = self.interactableSurf.get_rect(topleft=(0, 0))

        # Scale by 2x, 3x, etc.
        self.scaleFactor = 2
        originalSize = self.floorSurf.get_size()
        self.originalWidth = originalSize[0]  # Store original dimensions
        self.originalHeight = originalSize[1]  # Store original dimensions
        newSize = (originalSize[0] * self.scaleFactor, originalSize[1] * self.scaleFactor)
        self.floorSurf = pygame.transform.scale(self.floorSurf, newSize)
        self.floorRect = self.floorSurf.get_rect(topleft=(0, 0))
        self.wallSurf = pygame.transform.scale(self.wallSurf, newSize)
        self.wallRect = self.wallSurf.get_rect(topleft=(0, 0))
        self.wallMask = pygame.mask.from_surface(self.wallSurf)
        self.interactableSurf = pygame.transform.scale(self.interactableSurf, newSize)
        self.interactableRect = self.interactableSurf.get_rect(topleft=(0, 0))
        #self.interactableMask = pygame.mask.from_surface(self.interactableSurf)
        #self.propSurf = pygame.transform.scale(self.propSurf, newSize)
        #self.propRect = self.propSurf.get_rect(topleft=(0, 0))
        #self.propMask = pygame.mask.from_surface(self.propSurf)

        # Store screen dimensions
        self.screen_width = self.displaySurface.get_width()
        self.screen_height = self.displaySurface.get_height()


    def customDraw(self, player):
        # Calculate the ideal camera position (centered on player)
        self.offset.x = player.rect.centerx - self.halfWidth
        self.offset.y = player.rect.centery - self.halfHeight

        # Calculate boundaries using original (unscaled) dimensions
        left_boundary = 0
        right_boundary = self.originalWidth - (self.screen_width / self.scaleFactor) - TILESIZE * 14
        top_boundary = 0
        bottom_boundary = self.originalHeight - (self.screen_height / self.scaleFactor) - TILESIZE * 10.5

        # Apply boundaries
        if self.offset.x < left_boundary:
            self.offset.x = left_boundary
        if self.offset.x > right_boundary:
            self.offset.x = right_boundary
        if self.offset.y < top_boundary:
            self.offset.y = top_boundary
        if self.offset.y > bottom_boundary:
            self.offset.y = bottom_boundary

        # Drawing the floor
        floorOffsetPos = self.floorRect.topleft - self.offset
        self.displaySurface.blit(self.floorSurf, floorOffsetPos)

        # Drawing sprites
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offsetPos = sprite.rect.topleft - self.offset
            self.displaySurface.blit(sprite.image, offsetPos)
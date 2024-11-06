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
        # self.createNpcs()

        # Debug font
        self.debugFont = pygame.font.Font(None, 36)

        self.currentMap = 'crypt'  # Starting map
        self.mapData = {
            'crypt': {
                'floor': '../graphics/maps/CryptTest.png',
                'walls': '../graphics/maps/CryptCollideables.png',
                'props': '../graphics/maps/SolidProps.png',
                'playerSpawn': (1000, 1000),
                'connections': {
                    # Define map connections and their trigger zones
                    'town': {'zone': pygame.Rect(0, 500, 50, 200), 'spawn': (1900, 1000)},
                }
            },
            'town': {
                'floor': '../graphics/maps/Outside/outsideMap.png',  # need to create these map assets
                'walls': '../graphics/maps/Outside/outsideWalls.png',
                'props': '../graphics/maps/Outside/outsideHouses.png',
                'playerSpawn': (1000, 1000),
                'connections': {
                    'crypt': {'zone': pygame.Rect(1950, 500, 50, 200), 'spawn': (50, 1000)},
                }
            }
        }

        # Load initial map
        self.loadMap(self.currentMap)

    def loadMap(self, mapName):
        """Load a new map and set up all necessary sprites and objects."""
        # Clear existing sprites
        self.visibleSprites.empty()
        self.obstacleSprites.empty()
        self.npcs.empty()

        # Get map data
        mapInfo = self.mapData[mapName]

        # Update camera group with new map
        self.visibleSprites.loadMapSurfaces(
            mapInfo['floor'],
            mapInfo['walls'],
            mapInfo['props'],
        )

        # Create player at spawn position
        self.player = Player(mapInfo['playerSpawn'],
                             [self.visibleSprites],
                             self.obstacleSprites,
                             self.visibleSprites.wallMask)

        # Create NPCs specific to this map
        self.createNpcs(mapName)

        self.current_map = mapName

    def checkMapTransitions(self):
        # Check if player has entered a map transition zone.
        currentConnections = self.mapData[self.currentMap]['connections']

        for targetMap, connection in currentConnections.items():
            # Adjust zone position based on camera offset
            adjustedZone = connection['zone'].copy()
            adjustedZone.x *= self.visibleSprites.scaleFactor
            adjustedZone.y *= self.visibleSprites.scaleFactor

            if self.player.hitbox.colliderect(adjustedZone):
                self.transitionToMap(targetMap, connection['spawn'])
                break

    def transitionToMap(self, targetMap, spawnPosition):
        # Handle the transition to a new map.
        # could add transition effects here
        self.loadMap(targetMap)
        self.player.rect.topleft = spawnPosition
        self.player.hitbox.topleft = spawnPosition

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

    def createNpcs(self, mapName):
        # Create NPCs closer to starting position for testing
        npc1 = NPC((1100, 1000), [self.visibleSprites, self.npcs], "Artist")
        npc2 = NPC((900, 1000), [self.visibleSprites, self.npcs], "Marcus")
        npc3 = NPC((1500, 1000), [self.visibleSprites, self.npcs], "Lucius")

        npc4 = NPC((1250, 175), [self.visibleSprites, self.npcs], "outside")
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
        self.checkMapTransitions()

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

        # Scale factor setup
        self.scaleFactor = 2

        # Store screen dimensions
        self.screen_width = self.displaySurface.get_width()
        self.screen_height = self.displaySurface.get_height()

        # Initialize with default map
        self.loadMapSurfaces(
            floorPath='../graphics/maps/CryptTest.png',
            wallsPath='../graphics/maps/CryptCollideables.png',
            propsPath='../graphics/maps/SolidProps.png',
        )

    def loadMapSurfaces(self, floorPath, wallsPath, propsPath):
        # Load and scale new map surfaces
        # Load base surfaces
        self.floorSurf = pygame.image.load(floorPath).convert_alpha()
        self.wallSurf = pygame.image.load(wallsPath).convert_alpha()
        self.propSurf = pygame.image.load(propsPath).convert_alpha()

        # Get and store original dimensions
        originalSize = self.floorSurf.get_size()
        self.originalWidth = originalSize[0]
        self.originalHeight = originalSize[1]
        newSize = (originalSize[0] * self.scaleFactor, originalSize[1] * self.scaleFactor)

        # Scale all surfaces
        self.floorSurf = pygame.transform.scale(self.floorSurf, newSize)
        self.wallSurf = pygame.transform.scale(self.wallSurf, newSize)
        self.propSurf = pygame.transform.scale(self.propSurf, newSize)

        # Set up rects
        self.floorRect = self.floorSurf.get_rect(topleft=(0, 0))
        self.wallRect = self.wallSurf.get_rect(topleft=(0, 0))
        self.propRect = self.propSurf.get_rect(topleft=(0, 0))

        # Create masks
        self.wallMask = pygame.mask.from_surface(self.wallSurf)
        # self.propMask = pygame.mask.from_surface(self.propSurf)  # Uncomment if needed

    def customDraw(self, player):
        # Calculate the ideal camera position (centered on player)
        self.offset.x = player.rect.centerx - self.halfWidth
        self.offset.y = player.rect.centery - self.halfHeight

        # Calculate boundaries using original (unscaled) dimensions
        left_boundary = 0
        right_boundary = (self.originalWidth * self.scaleFactor - self.screen_width * 2) - TILESIZE * 18
        top_boundary = 0
        bottom_boundary = (self.originalHeight * self.scaleFactor - self.screen_height * 2) - TILESIZE * 21.5

        # Apply boundaries
        self.offset.x = max(left_boundary, min(self.offset.x, right_boundary))
        self.offset.y = max(top_boundary, min(self.offset.y, bottom_boundary))

        # Drawing the floor
        floorOffsetPos = self.floorRect.topleft - self.offset
        self.displaySurface.blit(self.floorSurf, floorOffsetPos)

        # Drawing sprites
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offsetPos = sprite.rect.topleft - self.offset
            self.displaySurface.blit(sprite.image, offsetPos)
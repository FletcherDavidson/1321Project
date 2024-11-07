import pygame
from constants import *
from tile import Tile
from player import Player
from helpful import *
from random import choice
from dialog import Dialog, NPC
from soundManager import *


class Level:
    def __init__(self):
        # Get the display surface
        self.displaySurface = pygame.display.get_surface()

        # Sprite group setup
        self.visibleSprites = YSortCameraGroup()
        self.obstacleSprites = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()

        # Debug font
        self.debugFont = pygame.font.Font(None, 36)

        # Initialize dialog system
        self.dialogSystem = Dialog()
        self.dialogSystem.setLevelReference(self)

        # Map management
        self.currentMap = 'crypt'  # Starting map

        # Add transition state management
        self.inTransition = False
        self.transitionTimer = 0
        self.transitionDuration = 4000  # milliseconds
        self.transitionAlpha = 0
        self.fadeOut = True

        # Create fade surface for transitions
        self.fadeSurface = pygame.Surface((WIDTH, HEIGTH))
        self.fadeSurface.fill((0, 0, 0))

        # Create map and load initial map
        self.createMapData()
        self.loadMap(self.currentMap)

        # Initialize sound manager
        self.soundManager = SoundManager()
        # Start ambient sound for initial map
        self.soundManager.startAmbient(self.currentMap)

    def createMapData(self):
        self.mapData = {
            'crypt': {
                'floor': '../graphics/maps/CryptTest.png',
                'walls': '../graphics/maps/CryptCollideables.png',
                'props': '../graphics/maps/SolidProps.png',
                'playerSpawn': (800, 1330),
                'connections': {
                    'town': {
                        'zone': pygame.Rect(0, 0, 0, 0), # Zone that sends player to town, not using currently
                        'spawn': (2650, 600)
                    }
                },
                'npcs': [
                    {'type': 'Artist', 'pos': (1100, 1000)},
                    {'type': 'Marcus', 'pos': (900, 1000)},
                    {'type': 'Lucius', 'pos': (1500, 1000)},
                    {'type': 'outside', 'pos': (1247, 173)}
                ]
            },
            'town': {
                'floor': '../graphics/maps/Outside/Map2.png',
                'walls': '../graphics/maps/Outside/Map2Walls.png',
                'props': '../graphics/maps/Outside/outsideHouses.png',
                'playerSpawn': (4000, 1000),
                'connections': {
                    'crypt': {
                        'zone': pygame.Rect(0, 0, 0, 0), # Zone that sends player to crypt, not using currently
                        'spawn': (3000, 1000)
                    }
                },
                'npcs': [
                    {'type': 'crypt', 'pos': (1000, 1000)}
                ]
            }
        }

    def startTransition(self, targetMap, spawnPosition):
        if not self.inTransition:
            print(f"Starting transition to {targetMap} with spawn position {spawnPosition}")
            self.inTransition = True
            self.transitionTimer = pygame.time.get_ticks()
            self.fadeOut = True
            self.targetMap = targetMap
            self.targetSpawn = spawnPosition
            self.soundManager.playSound('transition')

            # Close any active dialog
            if self.dialogSystem.active:
                self.dialogSystem.closeDialog()

    def updateTransition(self):
        if not self.inTransition:
            return

        currentTime = pygame.time.get_ticks()
        elapsedTime = currentTime - self.transitionTimer

        if self.fadeOut:
            self.transitionAlpha = min(255, (elapsedTime / (self.transitionDuration / 2)) * 255)
            if elapsedTime >= self.transitionDuration / 2:
                self.currentMap = self.targetMap  # Update current map
                self.loadMap(self.targetMap)
                self.player.rect.topleft = self.targetSpawn
                self.player.hitbox.topleft = self.targetSpawn
                self.fadeOut = False
                self.transitionTimer = currentTime
        else:
            self.transitionAlpha = max(0, 255 - (elapsedTime / (self.transitionDuration / 2)) * 255)
            if elapsedTime >= self.transitionDuration / 2:
                self.inTransition = False
                # Start new ambient sound
                self.soundManager.startAmbient(self.currentMap)

    def drawTransition(self):
        #Draw the transition effect.
        if self.inTransition:
            self.fadeSurface.set_alpha(self.transitionAlpha)
            self.displaySurface.blit(self.fadeSurface, (0, 0))

    def loadMap(self, mapName):
        # Load a new map and set up all necessary sprites and objects.
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
        self.player = Player(mapInfo['playerSpawn'],[self.visibleSprites],self.obstacleSprites, self.visibleSprites.wallMask, self)
        '''
        # Manually set the player's position
        if mapName == 'town':
            self.player.rect.topleft = (2000, 1000)  # Set spawn position here
            self.player.hitbox.topleft = (2000, 1000)
        elif mapName == 'crypt':
            self.player.rect.topleft = (1000, 1000)  # Set spawn position here
            self.player.hitbox.topleft = (1000, 1000)
        '''
        # Create NPCs specific to this map
        self.createNpcs(mapName)

        self.current_map = mapName

    def checkMapTransitions(self):
        if self.inTransition or self.dialogSystem.active:
            return  # Don't check for transitions if we're already transitioning or in dialog

        currentConnections = self.mapData[self.currentMap]['connections']

        for targetMap, connection in currentConnections.items():
            adjustedZone = connection['zone'].copy()
            adjustedZone.x *= self.visibleSprites.scaleFactor
            adjustedZone.y *= self.visibleSprites.scaleFactor

            if self.player.hitbox.colliderect(adjustedZone):
                self.startTransition(targetMap, connection['spawn'])
                return  # Exit after starting transition

    def transitionToMap(self, targetMap, spawnPosition):
        # Handle the transition to a new map.
        print(f"Transitioning to {targetMap} with spawn position {spawnPosition}")
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
        if mapName == "crypt":
            # Create NPCs closer to starting position for testing
            npc1 = NPC((1100, 1000), [self.visibleSprites, self.npcs], "Artist")
            npc2 = NPC((900, 1000), [self.visibleSprites, self.npcs], "Marcus")
            npc3 = NPC((1500, 1000), [self.visibleSprites, self.npcs], "Lucius")

            npc4 = NPC((1220, 175), [self.visibleSprites, self.npcs], "outside")
            print(f"Created NPCs. Total NPCs: {len(self.npcs)}") # Debug statement
        elif mapName == "town":
            # Add any town-specific NPCs here
            npc5 = NPC((2650, 540), [self.visibleSprites, self.npcs], "crypt")
            print(f"Created Town NPCs. Total NPCs: {len(self.npcs)}") # Debug statement

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
        # Check for map transitions first
        if not self.dialogSystem.active:
            self.checkMapTransitions()

        # Update transition if active
        if self.inTransition:
            self.updateTransition()

        # Update and draw the game
        self.visibleSprites.customDraw(self.player)
        self.visibleSprites.update()

        # Only check for NPC interaction if we're not transitioning or in dialog
        if not self.inTransition and not self.dialogSystem.active:
            self.checkNpcInteraction()
        elif self.dialogSystem.active:
            self.checkDialogDistance()

        # Draw dialog and transition effect
        self.dialogSystem.draw(self.displaySurface)
        self.drawTransition()

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
        self.screenWidth = self.displaySurface.get_width()
        self.screenHeight = self.displaySurface.get_height()

        # Initialize with default map
        self.loadMapSurfaces(
            floorPath='../graphics/maps/CryptTest.png',
            wallsPath='../graphics/maps/CryptCollideables.png',
            propsPath='../graphics/maps/SolidProps.png',
        )

        # Track current map
        self.currentMap = 'crypt'  # Default map

    def loadMapSurfaces(self, floorPath, wallsPath, propsPath):
        # Update current map based on the path
        self.currentMap = 'town' if 'outside' in floorPath.lower() else 'crypt'

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

        # Set boundaries based on current map
        if self.currentMap == 'town':
            # Town/outside map boundaries
            rightOffset = -40  # Adjust this value for town
            bottomOffset = -25  # Adjust this value for town
            topOffset = 0
        else:  # crypt
            # Crypt map boundaries
            rightOffset = 18
            bottomOffset = 21.5
            topOffset = 0

        # Calculate the ideal camera position (centered on player)
        self.offset.x = player.rect.centerx - self.halfWidth
        self.offset.y = player.rect.centery - self.halfHeight

        # Calculate boundaries
        leftBoundary = 0
        rightBoundary = (self.originalWidth * self.scaleFactor - self.screenWidth * 2) - TILESIZE * rightOffset
        topBoundary = 0 - topOffset
        bottomBoundary = (self.originalHeight * self.scaleFactor - self.screenHeight * 2) - TILESIZE * bottomOffset

        # Apply boundaries
        self.offset.x = max(leftBoundary, min(self.offset.x, rightBoundary))
        self.offset.y = max(topBoundary, min(self.offset.y, bottomBoundary))

        # Drawing the floor
        floorOffsetPos = self.floorRect.topleft - self.offset
        self.displaySurface.blit(self.floorSurf, floorOffsetPos)

        # Drawing sprites
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offsetPos = sprite.rect.topleft - self.offset
            self.displaySurface.blit(sprite.image, offsetPos)
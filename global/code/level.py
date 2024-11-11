import pygame
import math
import random
from constants import *
from player import Player
from random import choice
from dialog import Dialog, NPC
from soundManager import *



class Level:
    def __init__(self):
        self.dialog = Dialog()

        # Get the display surface
        self.displaySurface = pygame.display.get_surface()

        # Sprite group setup
        self.visibleSprites = cameraGroup()
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

        # Add win animation state
        self.inWinAnimation = False
        self.winAnimationStart = 0
        self.winAnimationDuration = 10000
        self.messageDuration = 5000
        self.particles = []
        self.portalSize = 0
        self.done = False

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



    def run(self):
        # Check for map transitions first
        if not self.dialogSystem.active:
            self.checkMapTransitions()

        # Update transition if active
        if self.inTransition:
            self.updateTransition()

        if self.inWinAnimation:
            self.updateWinAnimation()
            self.visibleSprites.customDraw(self.player)
            self.drawWinAnimation()
            return

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

    def startTransition(self, targetMap, spawnPosition):
        if not self.inTransition:
            # print(f"Starting transition to {targetMap} with spawn position {spawnPosition}")
            self.inTransition = True
            self.transitionTimer = pygame.time.get_ticks()
            self.fadeOut = True
            self.targetMap = targetMap
            self.targetSpawn = spawnPosition
            self.soundManager.playSound('transition')

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
        # print(f"Transitioning to {targetMap} with spawn position {spawnPosition}")
        # could add transition effects here
        self.loadMap(targetMap)
        self.player.rect.topleft = spawnPosition
        self.player.hitbox.topleft = spawnPosition

    def checkDialogDistance(self):
        #Check if player has moved too far from NPC during dialog
        if self.dialogSystem.active and self.dialogSystem.currentNpc:
            if not self.dialogSystem.currentNpc.canInteract(self.player, self.visibleSprites.offset):
                self.dialogSystem.closeDialog()
                # print("Dialog closed: Player moved too far from NPC") # Debug info

    def processDialogChoice(self, choice):
        # Handle dialog choices here
        # print(f"Processing dialog choice: {choice}")
        # Add dialog choice handling logic here
        pass

    def createNpcs(self, mapName):
        if mapName == "crypt":
            luciusImage = pygame.image.load("../graphics/Characters/Sprite2.png"),
            # marcusImage = pygame.image.load("../graphics/Characters/Sprite3.png"),
            # dudeImage = pygame.image.load("../graphics/Characters/Sprite4.png"),
            # Add more NPC sprites as needed

            # Create NPCs closer to starting position for testing
            # npc1 = NPC((1100, 1000), [self.visibleSprites, self.npcs], "Camilla", None)
            # npc2 = NPC((2000, 1000), [self.visibleSprites, self.npcs], "Marcus", marcusImage)
            npc3 = NPC((1700, 300), [self.visibleSprites, self.npcs], "Lucius", luciusImage)

            npc4 = NPC((1245, 215), [self.visibleSprites, self.npcs], "outside", None)
            npc9 = NPC((1220, 1500), [self.visibleSprites, self.npcs], "codex", None)
            print(f"Created NPCs. Total NPCs: {len(self.npcs)}") # Debug statement
        elif mapName == "town":
            artistImage = pygame.image.load("../graphics/Characters/Sprite1.png"),

            # Add any town-specific NPCs here
            npc5 = NPC((2695, 580), [self.visibleSprites, self.npcs], "crypt", None)
            npc6 = NPC((1462, 530), [self.visibleSprites, self.npcs], "Camilla", artistImage)
            if self.done == False:
                npc7 = NPC((2350, 550), [self.visibleSprites, self.npcs], "portal", None)
            else:
                npc8 = NPC((2350, 550), [self.visibleSprites, self.npcs], "portalwon", None)

            print(f"Created Town NPCs. Total NPCs: {len(self.npcs)}") # Debug statement

    def checkNpcInteraction(self):
        keys = pygame.key.get_pressed()

        '''
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
        '''

        for npc in self.npcs:
            if npc.canInteract(self.player, self.visibleSprites.offset):
                npc.drawInteractionPrompt(self.displaySurface, self.visibleSprites.offset)
                if keys[pygame.K_e]:
                    npc.startDialog(self.dialogSystem)

    def createMapData(self):
        self.mapData = {
            'crypt': {
                'floor': '../graphics/maps/CryptTest.png',
                'walls': '../graphics/maps/CryptCollideables.png',
                'props': '../graphics/maps/SolidProps.png',
                'playerSpawn': (2000, 600),
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

    def startWinAnimation(self):
        self.inWinAnimation = True
        self.winAnimationStart = pygame.time.get_ticks()
        self.winAnimationDuration = 3000  # 3 seconds
        self.particles = []
        self.portalSize = 0
        self.maxPortalSize = 200

        self.messageStartTime = pygame.time.get_ticks()


        # Create initial particles
        for _ in range(20):
            self.particles.append({
                'x': self.player.rect.centerx,
                'y': self.player.rect.centery,
                'speed': random.random() * 2 + 1,
                'angle': random.random() * math.pi * 2,
                'size': random.random() * 4 + 2,
                'alpha': 255  # Add alpha for fade out
            })

        # Play portal sound
        self.soundManager.playSound('portalOpen')

    def updateWinAnimation(self):
        if not self.inWinAnimation:
            return

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.winAnimationStart
        progress = elapsed / self.winAnimationDuration  # normalized time (0 to 1)


        # Check if animation should end
        if elapsed >= self.winAnimationDuration:
            self.inWinAnimation = False
            print("Victory Dialog triggered")  # Debug line
            # self.dialog.startVictoryDialog()
            return

        # Update portal size with easing
        self.portalSize = min(self.maxPortalSize,
                              self.maxPortalSize * self.easeOutQuad(progress))

        # Update particles with fade out
        for particle in self.particles:
            # Update position
            particle['x'] += math.cos(particle['angle']) * particle['speed']
            particle['y'] += math.sin(particle['angle']) * particle['speed']
            particle['angle'] += 0.02

            # Fade out particles
            particle['alpha'] = max(0, 255 * (1 - progress))

    def drawWinAnimation(self):
        if not self.inWinAnimation:
            return

        # Draw portal with alpha
        portal_surface = pygame.Surface((self.portalSize * 2, self.portalSize * 2), pygame.SRCALPHA)
        portal_alpha = max(0, 255 * (1 - (self.portalSize / self.maxPortalSize)))
        pygame.draw.circle(portal_surface, (135, 206, 235, portal_alpha),
                           (self.portalSize, self.portalSize), self.portalSize)

        # Draw particles with fade
        for particle in self.particles:
            color = (135, 206, 235, particle['alpha'])
            particle_surface = pygame.Surface((int(particle['size'] * 2),
                                               int(particle['size'] * 2)),
                                              pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color,
                               (int(particle['size']), int(particle['size'])),
                               int(particle['size']))

            # Calculate screen position
            screen_x = int(particle['x'] - self.visibleSprites.offset.x - particle['size'])
            screen_y = int(particle['y'] - self.visibleSprites.offset.y - particle['size'])
            self.displaySurface.blit(particle_surface, (screen_x, screen_y))

        # Draw portal at player position
        portal_pos = (self.player.rect.centerx - self.portalSize - self.visibleSprites.offset.x,
                      self.player.rect.centery - self.portalSize - self.visibleSprites.offset.y)
        self.displaySurface.blit(portal_surface, portal_pos)

        # Display "You have won" message
        if pygame.time.get_ticks() - self.messageStartTime <= self.messageDuration:
            font = pygame.font.SysFont("Arial", 48)
            text = font.render("You have won!", True, (255, 255, 255))  # White text
            text_rect = text.get_rect(center=(self.displaySurface.get_width() // 2, 50))  # Centered at the top
            self.displaySurface.blit(text, text_rect)

    def easeOutQuad(self, t):
        # Quadratic easing function for smoother animation
        return t * (2 - t)

class cameraGroup(pygame.sprite.Group):
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
        self.roofSurf = pygame.image.load("../graphics/maps/Outside/Plants/HouseRoofs.png").convert_alpha()
        self.ballisterSurf = pygame.image.load("../graphics/maps/CryptBallister.png").convert_alpha()

        # Get and store original dimensions
        originalSize = self.floorSurf.get_size()
        self.originalWidth = originalSize[0]
        self.originalHeight = originalSize[1]
        newSize = (originalSize[0] * self.scaleFactor, originalSize[1] * self.scaleFactor)

        # Scale all surfaces
        self.floorSurf = pygame.transform.scale(self.floorSurf, newSize)
        self.wallSurf = pygame.transform.scale(self.wallSurf, newSize)
        self.propSurf = pygame.transform.scale(self.propSurf, newSize)
        self.roofSurf = pygame.transform.scale(self.roofSurf, newSize)
        self.ballisterSurf = pygame.transform.scale(self.ballisterSurf, newSize)

        # Set up rects
        self.floorRect = self.floorSurf.get_rect(topleft=(0, 0))
        self.wallRect = self.wallSurf.get_rect(topleft=(0, 0))
        self.propRect = self.propSurf.get_rect(topleft=(0, 0))
        self.roofRect = self.roofSurf.get_rect(topleft=(0, 0))
        self.ballisterRect = self.ballisterSurf.get_rect(topleft=(0, 0))

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
            if sprite.image is not None:
                offsetPos = sprite.rect.topleft - self.offset
                self.displaySurface.blit(sprite.image, offsetPos)

        if self.currentMap == "town":
            if player.rect.centery <= self.roofRect.centery:
                self.displaySurface.blit(self.roofSurf, floorOffsetPos)

        #elif self.currentMap == "crypt":
            #if player.rect.centery <= self.ballisterRect.centery:
                #self.displaySurface.blit(self.ballisterSurf, ballisterOffsetPos)
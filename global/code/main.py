import pygame, sys
from constants import *
from level import Level
from dialog import *
from soundManager import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption('1321 Project')
        self.clock = pygame.time.Clock()
        self.level = Level()
        pygame.mouse.set_visible(False)
        self.soundManager = SoundManager()
        self.played_intro_sound = False  # Flag to track if the intro sound has been played
        self.u = 0

    def run(self):
        while True:
            # Play the intro sound only once at the start
            if not self.played_intro_sound:
                self.soundManager.playSound('intro')
                self.played_intro_sound = True

            if self.u >= 1100:  # Intro sound finished
                self.level.player.speed = 5  # Resume normal movement speed
            else:
                self.u += 1
                self.level.player.speed = 0  # Stop player movement while sound is playing

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE] and keys[pygame.K_LSHIFT]:
                    # print(self.u)
                    pygame.quit()
                    sys.exit()
                # Only handle dialog input if dialog is active
                if self.level.dialogSystem.active:
                    result = self.level.dialogSystem.handleInput(event)
                    if result is not None:
                        self.level.processDialogChoice(result)
            self.screen.fill('black')
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()
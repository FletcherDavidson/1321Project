import pygame
from level import *
from player import *

class Dialog:
    def __init__(self):
        self.active = False
        self.currentOptions = []
        self.currentResponse = ""
        self.font = pygame.font.Font(None, 32)
        self.dialogBoxColor = (0, 0, 0)
        self.textColor = (255, 255, 255)
        self.selectedOption = 0
        self.currentNpc = None  # Keep track of which NPC we're talking to

    def setDialog(self, options, response=""):
        self.active = True
        self.currentOptions = options
        self.currentResponse = response
        self.selectedOption = 0

    def draw(self, surface):
        if not self.active:
            return

        # Draw dialog box background
        dialogHeight = 200
        dialogRect = pygame.Rect(50, surface.get_height() - dialogHeight - 50,
                                surface.get_width() - 100, dialogHeight)
        pygame.draw.rect(surface, self.dialogBoxColor, dialogRect)
        pygame.draw.rect(surface, self.textColor, dialogRect, 2)

        # Draw response if there is one
        if self.currentResponse:
            responseSurf = self.font.render(self.currentResponse, True, self.textColor)
            surface.blit(responseSurf, (dialogRect.x + 20, dialogRect.y + 20))

        # Draw options
        for i, option in enumerate(self.currentOptions):
            color = (255, 255, 0) if i == self.selectedOption else self.textColor
            optionSurf = self.font.render(option, True, color)
            surface.blit(optionSurf, (dialogRect.x + 20,
                                     dialogRect.y + dialogHeight - (len(self.currentOptions) - i) * 40))

    def handleInput(self, event):
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selectedOption = (self.selectedOption - 1) % len(self.currentOptions)
            elif event.key == pygame.K_DOWN:
                self.selectedOption = (self.selectedOption + 1) % len(self.currentOptions)
            elif event.key == pygame.K_RETURN:
                chosenOption = self.selectedOption
                if self.currentNpc:
                    self.currentResponse = self.currentNpc.getResponse(chosenOption)
                    if not self.currentResponse:  # If no response, end dialog
                        self.active = False
                        self.currentNpc = None
                return chosenOption
        return None


class NPC(pygame.sprite.Sprite):
    def __init__(self, pos, groups, name):
        super().__init__(groups)
        # Make NPC more visible
        self.image = pygame.Surface((64, 64))  # Even bigger for testing
        self.image.fill((255, 0, 0))  # Red color
        pygame.draw.circle(self.image, (255, 255, 255), (32, 32), 25)  # White circle for debugging

        self.rect = self.image.get_rect(topleft=pos)
        self.name = name
        self.interactionRadius = 150  # Increased radius for testing
        self.dialogs = {
            "greeting": {
                "options": ["Hello, how are you?", "Leave me alone"],
                "responses": {
                    0: "I'm doing well, thank you for asking!",
                    1: "Oh... okay then..."
                }
            }
        }

    def canInteract(self, player, offset):
        # Adjust coordinates for camera offset
        screenPos = pygame.math.Vector2(self.rect.center) - offset
        playerScreenPos = pygame.math.Vector2(player.rect.center) - offset
        distance = screenPos.distance_to(playerScreenPos)

        # Debug print
        print(f"Distance to {self.name}: {distance}, Interaction radius: {self.interactionRadius}")
        return distance <= self.interactionRadius

    def drawInteractionPrompt(self, surface, offset):
        # Calculate screen position
        screenPos = (self.rect.centerx - offset.x, self.rect.centery - offset.y)

        # Draw interaction radius circle
        pygame.draw.circle(surface, (0, 255, 0), screenPos, self.interactionRadius, 2)

        # Draw interaction prompt
        font = pygame.font.Font(None, 36)
        prompt = font.render(f"Press E to talk to {self.name}", True, (255, 255, 255))
        promptRect = prompt.get_rect(centerx=screenPos[0], bottom=screenPos[1] - 20)
        surface.blit(prompt, promptRect)

        # Draw debug distance circle
        pygame.draw.circle(surface, (255, 255, 0), screenPos, 5)  # Yellow dot at NPC center

    def startDialog(self, dialogSystem):
        print(f"Starting dialog with {self.name}")  # Debug print
        dialogSystem.currentNpc = self
        dialogSystem.setDialog(self.dialogs["greeting"]["options"])
        dialogSystem.active = True  # Makes sure dialog is activated

    def getResponse(self, optionIndex):
        response = self.dialogs["greeting"]["responses"].get(optionIndex, "")
        print(f"NPC {self.name} responding with: {response}")  # Debug print
        return response
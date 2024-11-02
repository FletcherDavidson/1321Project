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
        self.currentNpc = None # Keep track of which NPC we're talking to

    def setDialog(self, options, response=""):
        self.active = True
        self.currentOptions = options
        self.currentResponse = response
        self.selectedOption = 0

    def closeDialog(self):
        self.active = False
        self.currentNpc = None
        self.currentOptions = []
        self.currentResponse = ""
        self.selectedOption = 0

    def draw(self, surface):
        if not self.active:
            return

        dialogHeight = 200
        dialogRect = pygame.Rect(50, surface.get_height() - dialogHeight - 50,
                               surface.get_width() - 100, dialogHeight)
        pygame.draw.rect(surface, self.dialogBoxColor, dialogRect)
        pygame.draw.rect(surface, self.textColor, dialogRect, 2)

        yOffset = 20
        if self.currentResponse:
            words = self.currentResponse.split()
            lines = []
            currentLine = []
            for word in words:
                currentLine.append(word)
                text = ' '.join(currentLine)
                if self.font.size(text)[0] > dialogRect.width - 40:
                    currentLine.pop()
                    lines.append(' '.join(currentLine))
                    currentLine = [word]
            if currentLine:
                lines.append(' '.join(currentLine))

            for line in lines:
                responseSurf = self.font.render(line, True, self.textColor)
                surface.blit(responseSurf, (dialogRect.x + 20, dialogRect.y + yOffset))
                yOffset += 30

        optionStartY = dialogRect.y + dialogHeight - (len(self.currentOptions) * 40) - 20
        for i, option in enumerate(self.currentOptions):
            color = (255, 255, 0) if i == self.selectedOption else self.textColor
            optionSurf = self.font.render(f"{i + 1}. {option}", True, color)
            surface.blit(optionSurf, (dialogRect.x + 20, optionStartY + (i * 40)))

    def handleInput(self, event):
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selectedOption = (self.selectedOption - 1) % len(self.currentOptions)
            elif event.key == pygame.K_DOWN:
                self.selectedOption = (self.selectedOption + 1) % len(self.currentOptions)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_e:
                if self.currentNpc:
                    responseText, nextOptions = self.currentNpc.getResponse(self.selectedOption)
                    if responseText is None:  # End dialog
                        self.closeDialog()
                    else:
                        self.currentResponse = responseText
                        if nextOptions:
                            self.currentOptions = nextOptions
                            self.selectedOption = 0
                return self.selectedOption
            elif event.key == pygame.K_ESCAPE:
                self.closeDialog()
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

        # Initialize dialog tree based on NPC type
        self.currentConversation = "greeting"  # Track current conversation state
        self.dialogs = self.getNpcDialogs()

    def startDialog(self, dialogSystem):
        print(f"Starting dialog with {self.name}")
        dialogSystem.currentNpc = self
        self.currentConversation = "greeting"
        currentDialog = self.dialogs.get(self.currentConversation, {})
        options = currentDialog.get("options", [])
        dialogSystem.setDialog(options)

    def getResponse(self, optionIndex):
        currentDialog = self.dialogs.get(self.currentConversation, {})
        responseData = currentDialog.get("responses", {}).get(optionIndex, {})

        responseText = responseData.get("text", "")
        nextState = responseData.get("next")

        if nextState is None:
            return None, None

        self.currentConversation = nextState
        nextDialog = self.dialogs.get(nextState, {})
        nextOptions = nextDialog.get("options", [])

        print(f"NPC {self.name} response: {responseText}, Next state: {nextState}")
        return responseText, nextOptions


    def canInteract(self, player, offset):
        # Adjust coordinates for camera offset
        screenPos = pygame.math.Vector2(self.rect.center) - offset
        playerScreenPos = pygame.math.Vector2(player.rect.center) - offset
        distance = screenPos.distance_to(playerScreenPos)

        # Debug print
        # print(f"Distance to {self.name}: {distance}, Interaction radius: {self.interactionRadius}")
        return distance <= self.interactionRadius

    def drawInteractionPrompt(self, surface, offset):
        # Calculate screen position
        screenPos = (self.rect.centerx - offset.x, self.rect.centery - offset.y)

        # Draw interaction radius circle for debugging
        # pygame.draw.circle(surface, (0, 255, 0), screenPos, self.interactionRadius, 2)

        # Draw interaction prompt
        font = pygame.font.Font(None, 36)
        prompt = font.render(f"Press E to talk to {self.name}", True, (255, 255, 255))
        promptRect = prompt.get_rect(centerx=screenPos[0], bottom=screenPos[1] - 20)
        surface.blit(prompt, promptRect)

        # Draw debug distance circle
        # pygame.draw.circle(surface, (255, 255, 0), screenPos, 5)  # Yellow dot at NPC center

    def getNpcDialogs(self):
        #Return different dialog trees based on NPC type
        if self.name == "Guard":
            return {
                "greeting": {
                    "options": [
                        "What are you guarding?",
                        "Have you seen anything suspicious?",
                        "Goodbye"
                    ],
                    "responses": {
                        0: {
                            "text": "I protect these ancient ruins. They hold many secrets.",
                            "next": "guardDuty"
                        },
                        1: {
                            "text": "There have been strange noises coming from below...",
                            "next": "suspicious"
                        },
                        2: {
                            "text": "Stay safe, traveler.",
                            "next": None  # None means end conversation
                        }
                    }
                },
                "guardDuty": {
                    "options": [
                        "Tell me about these secrets",
                        "How long have you been here?",
                        "I'll let you get back to work"
                    ],
                    "responses": {
                        0: {
                            "text": "I'm sworn to secrecy, but legends speak of great power hidden within.",
                            "next": "greeting"
                        },
                        1: {
                            "text": "Been standing guard for 10 years now. Not much changes around here.",
                            "next": "greeting"
                        },
                        2: {
                            "text": "Farewell.",
                            "next": None
                        }
                    }
                },
                "suspicious": {
                    "options": [
                        "What kind of noises?",
                        "When did this start?",
                        "I should investigate"
                    ],
                    "responses": {
                        0: {
                            "text": "Like whispers and scratching. Gives me the creeps.",
                            "next": "greeting"
                        },
                        1: {
                            "text": "Started about a week ago. Been getting worse each night.",
                            "next": "greeting"
                        },
                        2: {
                            "text": "Be careful down there...",
                            "next": None
                        }
                    }
                }
            }
        elif self.name == "Merchant":
            return {
                "greeting": {
                    "options": [
                        "What are you selling?",
                        "Where do you get your goods?",
                        "Goodbye"
                    ],
                    "responses": {
                        0: {
                            "text": "Ah, a potential customer! I have potions, scrolls, and rare artifacts.",
                            "next": "shop"
                        },
                        1: {
                            "text": "I travel far and wide to find the rarest items.",
                            "next": "trading"
                        },
                        2: {
                            "text": "Come back with more coins!",
                            "next": None
                        }
                    }
                },
                "shop": {
                    "options": [
                        "Tell me about your potions",
                        "Show me the artifacts",
                        "Maybe later"
                    ],
                    "responses": {
                        0: {
                            "text": "My potions are too strong for you, traveler!",
                            "next": "greeting"
                        },
                        1: {
                            "text": "Each artifact has a story... and a hefty price tag!",
                            "next": "greeting"
                        },
                        2: {
                            "text": "Don't wait too long, these deals won't last!",
                            "next": None
                        }
                    }
                },
                "trading": {
                    "options": [
                        "Any dangerous adventures?",
                        "Found anything unusual lately?",
                        "I'll let you get back to business"
                    ],
                    "responses": {
                        0: {
                            "text": "Lost my last caravan to a dragon! But the treasures were worth it.",
                            "next": "greeting"
                        },
                        1: {
                            "text": "Now that you mention it, I did find this strange amulet...",
                            "next": "greeting"
                        },
                        2: {
                            "text": "Safe travels, friend!",
                            "next": None
                        }
                    }
                }
            }
        # Add more NPCs here with their dialog trees
        return {}  # Default empty dialog for unknown NPCs
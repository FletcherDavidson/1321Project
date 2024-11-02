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

        self.name = name

        self.dialogs = self.getNpcDialogs()
        self.rect = self.image.get_rect(topleft=pos)
        self.interactionRadius = 150  # Increased radius for testing

        # Initialize dialog tree based on NPC type
        self.currentConversation = "greeting"  # Track current conversation state

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




    # To add a new npc go to level and in createNpcs just copy one of the ones there change pos and name

    def getNpcDialogs(self):
        if self.name == "Lucius":
            return {
                "greeting": {
                    "options": [
                        "I'm interested in your historical research",
                        "I've heard you have an impressive collection",
                        "Goodbye"
                    ],
                    "responses": {
                        0: {
                            "text": "Ah, a fellow scholar? It's rare to find others who appreciate the value of ancient knowledge.",
                            "next": "research"
                        },
                        1: {
                            "text": "Indeed, I've spent decades gathering texts and artifacts. Each piece tells its own story.",
                            "next": "collection"
                        },
                        2: {
                            "text": "Farewell, seeker of knowledge.",
                            "next": None
                        }
                    }
                },
                "research": {
                    "options": [
                        "Tell me about your current studies",
                        "I could help organize your research",
                        "Let's discuss something else"
                    ],
                    "responses": {
                        0: {
                            "text": "My current focus lies in ancient resistance movements. The strategies they employed were... fascinating.",
                            "next": "strategies"
                        },
                        1: {
                            "text": "Hmm... an intriguing offer. But I must be cautious with who accesses my more... sensitive materials.",
                            "next": "trust"
                        },
                        2: {
                            "text": "Very well. What would you like to discuss?",
                            "next": "greeting"
                        }
                    }
                },
                "collection": {
                    "options": [
                        "Any particularly rare pieces?",
                        "How do you protect your collection?",
                        "Return to previous topics"
                    ],
                    "responses": {
                        0: {
                            "text": "There are some... unique texts. But I must be selective about what I share.",
                            "next": "trust"
                        },
                        1: {
                            "text": "In these times, one can't be too careful. The Empire has... particular interests in certain knowledge.",
                            "next": "empire"
                        },
                        2: {
                            "text": "What else would you like to know?",
                            "next": "greeting"
                        }
                    }
                },
                "trust": {
                    "options": [
                        "I understand your caution",
                        "I could share some of my own research",
                        "Perhaps another time"
                    ],
                    "responses": {
                        0: {
                            "text": "Your patience is... refreshing. Perhaps in time, we could collaborate more closely.",
                            "next": "research"
                        },
                        1: {
                            "text": "Intriguing. What areas of study have captured your interest?",
                            "next": "strategies"
                        },
                        2: {
                            "text": "Yes, trust must be earned slowly in these dangerous times.",
                            "next": None
                        }
                    }
                },
                "strategies": {
                    "options": [
                        "Tell me about resistance tactics",
                        "What makes these strategies special?",
                        "Let's return to safer topics"
                    ],
                    "responses": {
                        0: {
                            "text": "The ancients had... unique ways of opposing tyranny. Some texts speak of methods lost to time.",
                            "next": "empire"
                        },
                        1: {
                            "text": "Their brilliance lies in subtlety. Not mere force, but wisdom in knowing when and how to act.",
                            "next": "collection"
                        },
                        2: {
                            "text": "Perhaps that would be wise. The walls have ears, after all.",
                            "next": "greeting"
                        }
                    }
                },
                "empire": {
                    "options": [
                        "You seem concerned about the Empire",
                        "These texts must be protected",
                        "I should go"
                    ],
                    "responses": {
                        0: {
                            "text": "One must be... diplomatic in expressing such concerns. But yes, their interest in ancient knowledge troubles me.",
                            "next": "strategies"
                        },
                        1: {
                            "text": "Indeed. Knowledge is power, and some powers are too dangerous in the wrong hands.",
                            "next": "trust"
                        },
                        2: {
                            "text": "Yes... perhaps you should. But return if you wish to discuss more... academic matters.",
                            "next": None
                        }
                    }
                }
            }

        elif self.name == "Marcus":
            return {
                "greeting": {
                    "options": [
                        "Lucius suggested I speak with you",
                        "I hear you're knowledgeable about local politics",
                        "Goodbye"
                    ],
                    "responses": {
                        0: {
                            "text": "Did he now? Lucius rarely sends visitors my way. You must have impressed him.",
                            "next": "lucius"
                        },
                        1: {
                            "text": "The currents of power in Rome run deep. One must be careful in discussing such matters.",
                            "next": "politics"
                        },
                        2: {
                            "text": "Safe travels, friend.",
                            "next": None
                        }
                    }
                }
                # Add more dialog options for Marcus...
            }

        elif self.name == "Artist":
            return {
                "greeting": {
                    "options": [
                        "I admire your work",
                        "Do you know Lucius the historian?",
                        "Farewell"
                    ],
                    "responses": {
                        0: {
                            "text": "You have an eye for art? Not many appreciate the deeper meanings in my work.",
                            "next": "art"
                        },
                        1: {
                            "text": "Ah, the reclusive scholar? Yes, he's commissioned several pieces from me.",
                            "next": "lucius"
                        },
                        2: {
                            "text": "May the muses guide your path.",
                            "next": None
                        }
                    }
                }
                # Add more dialog options for Artist...
            }

        return {}  # Default empty dialog for unknown NPCs
import pygame
from level import *
from player import *
from soundManager import *


class Dialog:
    def __init__(self):
        self.active = False # Whether the dialog system is active
        self.currentOptions = [] # Options player can choose between
        self.currentResponse = "" # NPC responses
        self.font = pygame.font.Font(None, 32)
        self.dialogBoxColor = (0, 0, 0)
        self.textColor = (255, 255, 255)
        self.selectedOption = 0 # What option player selects
        self.currentNpc = None
        self.levelRef = None # Reference to current level

        self.fullResponse = ""  # Stores the complete response text
        self.displayedChars = 0  # Number of characters currently displayed
        self.charDisplaySpeed = 45  # Characters per second
        self.lastCharTime = 0  # Last time a character was added
        self.isTyping = False  # Whether text is currently being typed
        self.showOptions = False  # Whether to show response options

        self.soundManager = SoundManager()

        #self.dialogBox = pygame.image.load('../graphics/test/DialogBox4.png').convert_alpha()
        #self.dialogBox = pygame.transform.scale(self.dialogBox, (1200, 300))

    def setLevelReference(self, level):
        self.levelRef = level
        self.soundManager = self.soundManager

    def setDialog(self, options, response=""):
        self.active = True
        self.currentOptions = options
        self.fullResponse = response
        self.currentResponse = ""
        self.displayedChars = 0
        self.selectedOption = 0
        self.isTyping = True
        self.showOptions = False
        self.lastCharTime = pygame.time.get_ticks()
        self.soundManager.playSound('dialogOpen')

    def updateTypewriter(self):
        if not self.isTyping:
            return

        currentTime = pygame.time.get_ticks()
        elapsed = currentTime - self.lastCharTime
        charsToAdd = int((elapsed / 1000.0) * self.charDisplaySpeed)

        # if self.isTyping and charsToAdd >= 0: # I couldn't find a good typing sound so I got rid of it I was going insane
            # self.soundManager.playSound('typing')

        if charsToAdd > 0:
            self.lastCharTime = currentTime
            self.displayedChars += charsToAdd

            if self.displayedChars >= len(self.fullResponse):
                self.displayedChars = len(self.fullResponse)
                self.isTyping = False
                self.showOptions = True  # Show options when typing is complete

            self.currentResponse = self.fullResponse[:self.displayedChars]

            # Play typing sound
            # if self.isTyping and charsToAdd > 0:
            #     self.typingSound.play()

    def closeDialog(self):
        self.active = False
        self.currentNpc = None
        self.currentOptions = []
        self.currentResponse = ""
        self.fullResponse = ""
        self.selectedOption = 0
        self.isTyping = False
        self.showOptions = False
        self.soundManager.playSound('dialogClose')

    def draw(self, surface):
        if not self.active:
            return

        # Update typewriter effect
        self.updateTypewriter()

        dialogHeight = 200
        dialogRect = pygame.Rect(50, surface.get_height() - dialogHeight - 50,
                               surface.get_width() - 100, dialogHeight)
        #surface.blit(self.dialogBox, (dialogRect.x, dialogRect.y))

        pygame.draw.rect(surface, self.dialogBoxColor, dialogRect)
        pygame.draw.rect(surface, self.textColor, dialogRect, 2)


        # Draw the text with word wrap
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

        # Only draw options if typing is complete and showOptions is True
        if self.showOptions:
            optionStartY = dialogRect.y + dialogHeight - (len(self.currentOptions) * 40) - 20
            for i, option in enumerate(self.currentOptions):
                color = (255, 255, 0) if i == self.selectedOption else self.textColor
                optionSurf = self.font.render(f"{i + 1}. {option}", True, color)
                surface.blit(optionSurf, (dialogRect.x + 20, optionStartY + (i * 40)))

    def handleInput(self, event):
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            # If still typing, allow skipping the typewriter effect
            if self.isTyping and event.key in [pygame.K_RETURN, pygame.K_e, pygame.K_SPACE]:
                self.displayedChars = len(self.fullResponse)
                self.currentResponse = self.fullResponse
                self.isTyping = False
                self.showOptions = True
                return None

            # Only allow option selection if typing is complete
            if not self.isTyping:
                if event.key == pygame.K_UP:
                    self.selectedOption = (self.selectedOption - 1) % len(self.currentOptions)
                    self.soundManager.playSound('dialogSelect')
                elif event.key == pygame.K_DOWN:
                    self.selectedOption = (self.selectedOption + 1) % len(self.currentOptions)
                    self.soundManager.playSound('dialogSelect')
                elif event.key == pygame.K_RETURN or event.key == pygame.K_e:
                    if self.currentNpc:
                        responseText, nextOptions, action = self.currentNpc.getResponse(self.selectedOption)
                        # Handle transitions
                        if action == "transition_town":
                            self.closeDialog()
                            if self.levelRef:
                                self.levelRef.startTransition('town', (2630, 650))
                                # THIS IS THE ACTUAL VARIABLE THAT CONTROLS PLAYER POS WHEN SENDING TO TOWN
                            return None
                        elif action == "transition_crypt":
                            self.closeDialog()
                            if self.levelRef:
                                self.levelRef.startTransition('crypt', (1214, 168))
                            return None
                        elif action == "portal_animation":
                            print("Starting portal animation")
                            self.closeDialog()  # Close the current dialog
                            self.active = False  # Ensure dialog is completely inactive during animation
                            if self.levelRef:
                                self.levelRef.startWinAnimation()
                                print("Win animation started")
                            return None


                        # Handle regular dialog
                        if responseText is None:
                            self.closeDialog()
                        else:
                            self.setDialog(nextOptions, responseText)
                    return self.selectedOption
                elif event.key == pygame.K_ESCAPE:
                    self.closeDialog()
        return None


'''
    def startVictoryDialog(self):
        print("Second test")
        # Set up the victory dialog
        self.fullResponse = "You have won, congratulations!"  # Victory message
        self.currentOptions = ["Continue"]  # Option(s) for the player to continue
        self.selectedOption = 0
        self.displayedChars = 0  # Reset the typewriter display count
        self.isTyping = True
        self.showOptions = False  # Start without showing options until typing finishes
        self.lastCharTime = pygame.time.get_ticks()  # Initialize timing for typewriter effect
        self.active = True  # Activate the dialog box
'''

class NPC(pygame.sprite.Sprite):
    def __init__(self, pos, groups, name, spriteImage):
        super().__init__(groups)
        # Set the image
        if isinstance(spriteImage, tuple):
            # If spriteImage is a tuple, we assume it's a list of images
            self.images = [pygame.transform.scale(image, (image.get_width() * 3, image.get_height() * 3)) for image in
                           spriteImage]
            self.image = self.images[0]
        elif spriteImage is None:
            self.image = None
        else:
            # Scale a single image if it's not a tuple
            self.image = pygame.transform.scale(spriteImage,
                                                (spriteImage.get_width() * 3, spriteImage.get_height() * 3))

        # Set the rect for the image
        if self.image is None:
            self.rect = pygame.Rect(pos[0], pos[1], 0, 0)
        else:
            self.rect = pygame.Rect(pos[0], pos[1], self.image.get_width(), self.image.get_height())

        # Make transition NPCs invisible if the name is "outside" or "crypt" or if no image exists
        if name in ["outside", "crypt"] or self.image is None:
            if self.image is not None:
                self.image.set_alpha(0)
        else:
            # Create a surface large enough to hold the image, assuming 64x64 is the base size
            self.image = pygame.Surface((self.image.get_width(), self.image.get_height()), pygame.SRCALPHA)
            self.image.blit(self.images[0], (0, 0))  # Blit the scaled image onto the new surface

        self.name = name
        self.dialogs = self.getNpcDialogs()
        # self.rect = self.image.get_rect(topleft=pos)
        self.interactionRadius = 150
        self.currentConversation = "greeting"
        self.isTransitionNPC = name in ["outside", "crypt"]

    def startDialog(self, dialogSystem):
        print(f"Starting dialog with {self.name}")
        dialogSystem.currentNpc = self
        self.currentConversation = "greeting"
        currentDialog = self.dialogs.get(self.currentConversation, {})
        options = currentDialog.get("options", [])
        dialogSystem.setDialog(options)

        self.currentConversation = "greeting"
        currentDialog = self.dialogs.get(self.currentConversation, {})
        options = currentDialog.get("options", [])
        dialogSystem.setDialog(options)

    def getResponse(self, optionIndex):
        currentDialog = self.dialogs.get(self.currentConversation, {})
        responseData = currentDialog.get("responses", {}).get(optionIndex, {})

        responseText = responseData.get("text", "")
        nextState = responseData.get("next")
        action = responseData.get("action", None)  # Get the action if it exists

        if nextState is None:
            return None, None, action

        self.currentConversation = nextState
        nextDialog = self.dialogs.get(nextState, {})
        nextOptions = nextDialog.get("options", [])

        return responseText, nextOptions, action

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
        if self.name == "outside":
            prompt = font.render(f"Press E to enter the {self.name}", True, (255, 255, 255))
        elif self.name == "crypt":
            prompt = font.render(f"Press E to enter the {self.name}", True, (255, 255, 255))
        else:
            prompt = font.render(f"Press E to talk to {self.name}", True, (255, 255, 255))
        promptRect = prompt.get_rect(centerx=screenPos[0], bottom=screenPos[1] - 45)
        surface.blit(prompt, promptRect)

        # Draw debug distance circle
        # pygame.draw.circle(surface, (255, 255, 0), screenPos, 5)  # Yellow dot at NPC center

    # To add a new npc go to level and in create Npcs just copy one of the ones there change pos and name

    def getNpcDialogs(self):
        if self.name == 'Lucius':
            return {
                'greeting': {
                    'options': [
                        'I need your help!',
                        'Have you heard of the codex?',
                        'Goodbye!'
                    ],
                    'responses': {
                        0: {
                            'text': 'How can I help you?',
                            'next': "help"
                        },
                        1: {
                            'text': 'I know very little about the codex.',
                            'next': 'codex'
                        },
                        2: {
                            'text': 'Safe travels!',
                            'next': None
                        }
                    }
                },
                'help': {
                    'options': [
                        'I need to know the location of the codex.',
                        'How much do you know about the codex?'
                    ],
                    'responses': {
                        0: {
                            'text': 'The location of the codex is hidden to me as well.',
                            'next': 'Worker'
                        },
                        1: {
                            'text': 'Only that it is hidden away.',
                            'next': 'Worker'
                        }
                    }
                },
                'codex': {
                    'options': [
                        'Do you know where it was hidden?'
                    ],
                    'responses': {
                        0: {
                            'text': 'The location is unknown to me.',
                            'next': 'Worker'
                        }
                    }
                },
                'Worker': {
                    'options': [
                        'Do you have any clue to the location of the codex?',
                        'Do you know anyone that does know the location?'
                    ],
                    'responses': {
                        0: {
                            'text': "There's is only one person I know that might be able to help you. Her name is Camilla and she runs the shops in town.",
                            'next': "Final"
                        },
                        1: {
                            'text': "Her name is Camilla. She runs a shop in town. She may be able to help you.",
                            'next': "Final"
                        }
                    }
                },
                "Final": {
                    'options': [
                        "Thank You! "
                    ],
                    "responses": {
                        0: {
                            'text': "There's is only one person I know that might be able to help you. Her name is Camilla and she runs the shops in town.",
                            'next': None
                        }
                    }
                }
            }
        elif self.name == 'Camilla':
            return {
                'greeting': {
                    'options': [
                        'Hello!',
                        'Are you Camilla?',
                        'Goodbye!'
                    ],
                    'responses': {
                        0: {
                            'text': 'Hello traveler, would you like to buy something?',
                            'next': 'introduction'
                        },
                        1: {
                            'text': 'That is I. How can I help you?',
                            'next': 'information'
                        },
                        2: {
                            'text': 'Safe Travels!',
                            'next': None
                        }
                    }
                },
                'introduction': {
                    'options': [
                        'No, I actually have a question for you.',
                        'No, are you Camilla?'
                    ],
                    'responses': {
                        0: {
                            'text': 'For me? How can I help you?',
                            'next': 'location'
                        },
                        1: {
                            'text': 'That is I. How can I help you?',
                            'next': 'location'
                        }
                    }
                },
                'location': {
                    'options': [
                        'Do you know the location of the codex?',
                        'Can you help me find the codex?'
                    ],
                    'responses': {
                        0: {
                            'text': 'I cannot give you the location of the codex but I can give you a clue of where you can find it.',
                            'next': 'clue'
                        },
                        1: {
                            'text': 'I cannot give you the location of the codex but I can give you a clue of where you can find it.',
                            'next': 'clue'
                        }
                    }
                },
                'clue': {
                    'options': [
                        'A clue would be very helpful.',
                        'Please anything will help!'
                    ],
                    'responses': {
                        0: {
                            'text': 'The codex is contained where ancient stories are kept.',
                            'next': 'thank'
                        },
                        1: {
                            'text': 'The codex is contained where ancient stories are kept.',
                            'next': 'thank'
                        }
                    }
                },
                'thank': {
                    'options': [
                        'Thank you for your help!'
                        'That was very helpful! Thank you!'
                    ],
                    'responses': {
                        0: {
                            'text': 'Your welcome! Safe Travels!',
                            'next': None
                        },
                        1: {
                            'text': 'Your welcome! Safe Travels!',
                            'next': None
                        },
                    },
                },
            }
        elif self.name == "outside":
            return {
                "greeting": {
                    "options": ["Enter the town"],
                    "responses": {
                        0: {
                            "text": "Transitioning to town...",
                            "next": None,
                            "action": "transition_town"
                        }
                    }
                }
            }
        elif self.name == "crypt":
            return {
                "greeting": {
                    "options": ["Enter the crypt"],
                    "responses": {
                        0: {
                            "text": "Transitioning to crypt...",
                            "next": None,
                            "action": "transition_crypt"
                        }
                    }
                }
            }
        elif self.name == "portal":
            return {
                "greeting": {
                    "options": [
                        "I'd like to open the portal!"
                    ],
                    "responses": {
                        0: {
                            "text": "What is the password?",
                            "next": "guess"
                        }
                    }
                },
                "guess": {
                    "options": [
                        "The password is Effugium",
                        "The password is Bestias",
                        "The password is Pennarum "
                    ],
                    "responses": {
                        0: {
                            "text": "The portal has opened, you have won! ",
                            "next": "win",
                            "action": "portal_animation"
                        },
                        1: {
                            "text": "That password is incorrect, begone.",
                            "next": "wrong"
                        },
                        2: {
                            "text": "That password is incorrect, begone.",
                            "next": "wrong"
                        }
                    }
                },
                "wrong": {
                    "options": [
                        "The password is Effugium",
                        "The password is Bestias",
                        "The password is Pennarum "
                    ],
                    "responses": {
                        0: {
                            "text": "The portal has opened, you have won!",
                            "next": "win",
                            "action": "portal_animation"
                        },
                        1: {
                            "text": "That password is incorrect, begone.",
                            "next": "wrong"
                        },
                        2: {
                            "text": "That password is incorrect, begone.",
                            "next": "wrong"
                        },
                    },
                },
                "win": {
                    "options": [
                        "You have won, congratulations!",
                    ],
                    "responses": {
                        0: {
                            "text": "The portal has opened, you have won!",
                            "next": None
                        }
                    }
                }
            }
        elif self.name == "codex":
            return {
                "greeting": {
                    "options": [
                        "Is this the codex? "
                    ],
                    "responses": {
                        0: {
                            "text": "Codex of ancient knowledge",
                            "next": "firstPage"
                        }
                    }
                },
                "firstPage": {
                    "options": [
                        "The only word I can make out is Effugium",
                    ],
                    "responses": {
                        0: {
                            "text": "The code to the portal is Effugium",
                            "next": None,
                        }
                    }
                }
            }

        return {}  # Default empty dialog for unknown NPCs
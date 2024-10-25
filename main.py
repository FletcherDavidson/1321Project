import pygame
import sys

pygame.init()

screenWidth = 800
screenHeight = 600
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Pygame Project")

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 255, 0)
green = (0, 0, 255)

font = pygame.font.Font(None, 36)

# This is a dictionary which when called loads an image
roomImages = {
    "start": pygame.image.load("assets/start_room.jpg").convert_alpha(),
    "hallway": pygame.image.load("assets/hallway.jpg").convert_alpha(),
    "bossRoom": pygame.image.load("assets/boss_room.jpg").convert_alpha()
}

# If we have characters then this is a separate dictionary which loads characters
characterImages = {
    "boss": pygame.image.load("assets/boss.png").convert_alpha()
}

# This takes the images in those 2 dictionaries and scales them to fit the screen/size
for key in roomImages:
    roomImages[key] = pygame.transform.scale(roomImages[key], (screenWidth, screenHeight))
for key in characterImages:
    characterImages[key] = pygame.transform.scale(characterImages[key], (200, 300))

currentRoom = "start"
playerInput = ""
outputText = ""
currentCharacter = None  # To track if a character is active

# Dictionary with all the options for rooms (can be expanded)
rooms = {
    "start": {
        "description": "You are in a dark room. There's a door to the north.",
        "options": {"north": "hallway"},
        "characters": {}
    },
    "hallway": {
        "description": "You find yourself in a long hallway. There's a door at the end.",
        "options": {"south": "start", "enter": "bossRoom"},
        "characters": {}
    },
    "bossRoom": {
        "description": "This is the boss room. The air is thick with tension.",
        "options": {"escape": "hallway"},
        "characters": {"boss": "The boss stands before you, ready for battle."}
    }
}


# Function to handle player movement between rooms
def processInput(inputText):
    global currentRoom, outputText, currentCharacter
    inputText = inputText.strip().lower()
    roomData = rooms[currentRoom]

    # Clears characters when changing rooms
    currentCharacter = None

    if inputText in roomData["options"]:
        currentRoom = roomData["options"][inputText]
        outputText = rooms[currentRoom]["description"]
    elif inputText in roomData["characters"]:
        # When interacting with a character (Untested)
        currentCharacter = inputText
        outputText = rooms[currentRoom]["characters"][inputText]
    else:
        outputText = "Invalid action. Try something else."


# Handles all the drawing of text
def drawText(surface, text, pos):
    lines = text.split('\n')
    yOffset = 0
    for line in lines:
        textSurface = font.render(line, True, white)
        surface.blit(textSurface, (pos[0], pos[1] + yOffset))
        yOffset += textSurface.get_height() + 5


outputText = rooms[currentRoom]["description"]

while True:
    screen.fill(black)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_BACKSPACE:
                playerInput = playerInput[:-1]
            elif event.key == pygame.K_RETURN:
                processInput(playerInput)
                playerInput = ""  # Clears input after processing
            else:
                playerInput += event.unicode

    # Displays the image of the current room
    screen.blit(roomImages[currentRoom], (0, 0))

    # Displays character image if interacting with one
    if currentCharacter and currentCharacter in characterImages:
        screen.blit(characterImages[currentCharacter], (500, 250))  # Puts a character at 500, 250

    # Displays current room description or character interaction text
    drawText(screen, outputText, (50, 50))

    # Displays player input
    drawText(screen, "> " + playerInput, (50, 500))

    pygame.display.flip()
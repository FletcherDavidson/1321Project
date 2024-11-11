import pygame


class SoundManager:
    def __init__(self):
        # Initialize mixer
        pygame.mixer.init()

        # Sound effect dictionary
        self.sounds = {
            # Dialog sounds
            # 'typing': pygame.mixer.Sound('../audio/sfx/typing.wav'),
            'dialogOpen': pygame.mixer.Sound('../audio/sfx/dialogOpen.wav'),
            'dialogClose': pygame.mixer.Sound('../audio/sfx/dialogClose.wav'),
            'dialogSelect': pygame.mixer.Sound('../audio/sfx/dialogSelect.wav'),

            # Map transition
            'transition': pygame.mixer.Sound('../audio/sfx/transition.wav'),

            # Ambient sound channels (these will be longer audio files)
            'ambientCrypt': pygame.mixer.Sound('../audio/ambient/cryptAmbient.wav'),
            'ambientTown': pygame.mixer.Sound('../audio/ambient/townAmbient.wav'),

            #Portal
            'portalOpen': pygame.mixer.Sound('../audio/sfx/portalOpen.wav'),

            #Intro
            'intro': pygame.mixer.Sound('../audio/sfx/Intro.wav')

        }

        # Set default volumes
        self.volumes = {
            'sfx': 0.7,
            'ambient': 0.9,
            # 'typing': 0.7  # Typing sound should be quieter
        }

        # Apply volumes
        for soundName, sound in self.sounds.items():
            # if 'typing' in soundName:
                # sound.set_volume(self.volumes['typing'])
            if 'ambient' in soundName:
                sound.set_volume(self.volumes['ambient'])
            else:
                sound.set_volume(self.volumes['sfx'])

        # Track current ambient sound
        self.currentAmbient = None

        # Reserve channels
        pygame.mixer.set_num_channels(8)
        self.ambientChannel = pygame.mixer.Channel(7)  # Reserve last channel for ambient

    def playSound(self, soundName):
        # Play a sound effect once
        if soundName in self.sounds:
            self.sounds[soundName].play()

    def startAmbient(self, mapName):
        # Start playing the ambient sound for a specific map
        ambientName = f'ambient{mapName.capitalize()}'

        # Stop current ambient if it's different
        if self.currentAmbient != ambientName:
            self.ambientChannel.stop()

            if ambientName in self.sounds:
                # Play new ambient sound on loop
                self.ambientChannel.play(self.sounds[ambientName], loops=-1, fade_ms=1000)
                self.currentAmbient = ambientName

    def stopAmbient(self):
        # Stop current ambient sound with fade out
        if self.currentAmbient:
            self.ambientChannel.fadeout(1000)
            self.currentAmbient = None

    def setVolume(self, volumeType, value):
        # Adjust volume for a specific type of sound
        if volumeType in self.volumes:
            self.volumes[volumeType] = max(0.0, min(1.0, value))

            # Update volumes for affected sounds
            for soundName, sound in self.sounds.items():
                # if volumeType == 'typing' and 'typing' in soundName:
                    # sound.set_volume(self.volumes['typing'])
                if volumeType == 'ambient' and 'ambient' in soundName:
                    sound.set_volume(self.volumes['ambient'])
                elif volumeType == 'sfx' and 'ambient' not in soundName: # and 'typing' not in soundName:
                    sound.set_volume(self.volumes['sfx'])
import pygame, os.path
from config import *
class Player(pygame.sprite.Sprite):
    def __init__(self, position:pygame.Vector2) -> None:
        super().__init__()
        self.image = pygame.image.load(self.accessFile("playerblock.png")).convert_alpha()
        self.rect = pygame.rect.Rect(0, 0, 32, 32)
        self.rect.topleft = position
        self.isalive = True

    def handleDeath(self):
        deathSound = pygame.mixer.Sound(self.accessFile("death.wav"))
        deathSound.play()
        self.image = pygame.image.load(self.accessFile("deathblock.png")).convert_alpha()

    def handleKeyPressed(self, event:int):
        movementSound = pygame.mixer.Sound(self.accessFile("playermovement.wav"))
        if event.key == pygame.K_DOWN:
            self.rect.topleft += pygame.Vector2(0, 32)
            movementSound.play()
        elif event.key == pygame.K_UP:
            self.rect.topleft -= pygame.Vector2(0, 32)
            movementSound.play()
        elif event.key == pygame.K_RIGHT:
            self.rect.topleft += pygame.Vector2(32, 0)
            movementSound.play()
        elif event.key == pygame.K_LEFT:
            self.rect.topleft -= pygame.Vector2(32, 0)
            movementSound.play()

    @staticmethod
    def accessFile(filename:str) -> str:
        cwd = os.path.dirname(__file__)
        path = f"{cwd}/Assets/{filename}"
        return path
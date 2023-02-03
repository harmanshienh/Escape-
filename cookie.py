import pygame, os.path
from config import *
class Cookie(pygame.sprite.Sprite):
    def __init__(self, position:pygame.Vector2) -> None:
        super().__init__()
        self.image = pygame.image.load(self.accessFile("cookie.png")).convert_alpha()
        self.rect = pygame.rect.Rect(0, 0, 32, 32)
        self.rect.topleft = position
    
    @staticmethod
    def accessFile(filename:str) -> str:
        cwd = os.path.dirname(__file__)
        path = f"{cwd}/Assets/{filename}"
        return path
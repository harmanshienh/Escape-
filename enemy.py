import pygame, os.path
from config import *
class Enemy(pygame.sprite.Sprite):
    enemyTotal = 0
    def __init__(self, position:pygame.Vector2, type:int) -> None:
        super().__init__()
        self.image = pygame.image.load(self.accessFile("enemyblock.png")).convert_alpha()
        self.rect = pygame.rect.Rect(0, 0, 32, 32)
        self.rect.topleft = position
        self.type = type
        self.id = Enemy.enemyTotal
        self.event = pygame.USEREVENT + self.id
        self.oldpos = position

        Enemy.enemyTotal += 1
        
        if self.type == 1:
            pygame.time.set_timer(self.event, 500)
            self.speed = pygame.Vector2(32, 0)
        elif self.type == 2:
            pygame.time.set_timer(self.event, 333)
            self.speed = pygame.Vector2(0, 32)

    def update(self, event:int):
        if event == self.event:
            self.oldpos = self.rect.topleft
            self.rect.topleft += pygame.Vector2(self.speed)

    @staticmethod
    def accessFile(filename:str) -> str:
        cwd = os.path.dirname(__file__)
        path = f"{cwd}/Assets/{filename}"
        return path
import pygame, sys, os.path, random, math
from config import *
from wall import Wall
from player import Player
from enemy import Enemy
from cookie import Cookie
from goal import Goal
from warp import Warp

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Block Escape")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 60, False, False)
        self.promptFont = pygame.font.SysFont(None, 30, False, False)
        self.menu = pygame.image.load(self.accessFile("menu.png")).convert_alpha()
        self.bg = pygame.image.load(self.accessFile("bg.png")).convert_alpha()
        self.selector = pygame.image.load(self.accessFile("cookie.png")).convert_alpha()
        self.selectorRect = self.selector.get_rect()
        self.selectorRect.center = pygame.Vector2(550, 310)
        self.index = 0

        self.wallGroup = pygame.sprite.Group()
        self.player = pygame.sprite.Group()
        self.enemyGroup = pygame.sprite.Group()
        self.cookieGroup = pygame.sprite.Group()
        self.goalGroup = pygame.sprite.Group()
        self.warpGroup = pygame.sprite.Group()

        self.state = states.get("TITLE")

        self.score = 0
        self.level = 1
        self.drawWarpIndex = False

    def determineGridLocation(self, loadingLevel:bool) -> pygame.Vector2:
        self.height = 0
        path = self.accessLevel(f"level{self.level}.txt")
        f = open(path, "r")
        for line in f:
            width = len(line)
            self.height += 1
        f.close()

        if loadingLevel:
            self.countdown = math.ceil(0.15 * (width * self.height))

        width *= 32
        self.height *= 32

        levelDisplay = pygame.Rect(0, 0, width, self.height)
        levelDisplay.center = pygame.Vector2(WIDTH / 2, 410)
        return levelDisplay.topleft
    
    def loadLevel(self):
        self.emptySpriteGroups()
        self.timeElapsed = 0
        self.score = 0
        self.warps = []
        topleft = self.determineGridLocation(True)
        f = open(self.accessLevel(f"level{self.level}.txt"), "r")
        for row, line in enumerate(f):
            for col, block in enumerate(line):
                pos = topleft + pygame.Vector2(col * 32, row * 32)
                if block == "p":
                    self.p = Player(pos)
                    self.player.add(self.p)
                elif block == "x":
                    self.wallGroup.add(Wall(pos))
                elif block == "1" or block == "2":
                    self.enemyGroup.add(Enemy(pos, int(block)))
                elif block == "e":
                    self.goalGroup.add(Goal(pos))
                elif block == "w":
                    self.warpGroup.add(Warp(pos))
                    self.warps.append(pos)
        f.close()
        self.organizeWarps()
        self.spawnCookie()
    
    def organizeWarps(self):
        self.warpXPos = []
        self.sortedWarps = []

        for pos in self.warps:
            self.warpXPos.append(pos.x)

        self.warpXPos.sort()

        for xPos in self.warpXPos:    
            for pos in self.warps:
                if pos.x == xPos:
                    self.sortedWarps.append(pos)

    def spawnCookie(self):
        valid_pos = False
        path = self.accessLevel(f"level{self.level}.txt")
        f = open(path, "r")
        grid = [list(line.strip())for line in f.readlines()]
        f.close()

        while not valid_pos:
            row = random.randint(0, len(grid) - 1)
            col = random.randint(0, len(grid[0]) - 1)
            if grid[row][col] == "_":
                valid_pos = True

        topleft = self.determineGridLocation(False)
            
        pos = topleft + pygame.Vector2(col * 32, row * 32)
        c = Cookie(pos)
        self.cookieGroup.add(c)

    def update(self):
        if self.state == states.get("GAMEPLAY"):
            self.checkCollisions()
            if self.score >= 5:
                self.goalGroup.update()

            self.timeElapsed += self.clock.get_time()
            if self.timeElapsed > 1000 and self.countdown != 0 and self.p.isalive:
                self.countdown -= 1
                self.timeElapsed -= 1000
                if self.countdown <= 3:
                    self.playSFX("countdown.wav")
            if self.countdown == 0:
                self.p.isalive = False
                self.p.handleDeath()
                self.state = states.get("LOSE")

    def draw(self):
        if self.state == states.get("TITLE"):
            self.screen.blit(self.menu, (0,0))
            self.screen.blit(self.selector, self.selectorRect)
        else:
            self.screen.blit(self.bg, (0,0))
            self.drawText()
        self.drawSpriteGroups()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.handleOtherEvents(event)

            self.screen.fill("black")
            self.update()
            self.draw()
            pygame.display.update()
            self.clock.tick(FPS)

    def handleOtherEvents(self, event:int):
        if self.state == states.get("GAMEPLAY"):
            if event.type == pygame.KEYDOWN:
                self.p.handleKeyPressed(event)
                if self.drawWarpIndex:
                    self.handleWarpKeyPressed()
            for i in range(Enemy.enemyTotal):
                if event.type == pygame.USEREVENT + i:
                    self.enemyGroup.update(event.type)

        if self.state == states.get("TITLE"):
            if event.type == pygame.KEYDOWN:
                self.handleTitleKeyPressed()

        if self.state == states.get("TRANSITION"):
            if event.type == pygame.KEYDOWN:
                self.handleTransitionKeyPressed()

        if self.state == states.get("WIN") or self.state == states.get("LOSE"):
            if event.type == pygame.KEYDOWN:
                self.handleWinLoseKeyPressed()

    def handleTitleKeyPressed(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            if self.index == 0:
                self.index = 1
            else:
                self.index -= 1
        elif keys[pygame.K_DOWN]:
            if self.index == 1:
                self.index = 0
            else:
                self.index += 1
        elif keys[pygame.K_RETURN]:
            if self.index == 0:
                self.state = states.get("GAMEPLAY")
                self.loadLevel()
            elif self.index == 1:
                pygame.quit()
                sys.exit()

        self.selectorRect.center = pygame.Vector2(550, 310 + 70 * self.index)
    
    def handleTransitionKeyPressed(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RETURN]:
            self.level += 1
            self.state = states.get("GAMEPLAY")
            self.loadLevel()
    
    def handleWinLoseKeyPressed(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RETURN]:
            self.level = 1
            self.state = states.get("GAMEPLAY")
            self.loadLevel()
        elif keys[pygame.K_q]:
            pygame.quit()
            sys.exit()
    
    def handleWarpKeyPressed(self):
        keys = pygame.key.get_pressed()
        for i in range(len(self.sortedWarps)):
            if keys[i + 49]:
                if self.sortedWarps[i] != self.p.rect.topleft:
                    self.playSFX("warp.wav")
                    self.p.rect.topleft = self.sortedWarps[i]

    def drawText(self):
        textScore = self.font.render(f"{self.score}", True, (255, 255, 255))
        textLevel = self.font.render(f"{self.level}", True, (255, 255, 255))

        self.drawWarpIndices()
        
        if self.countdown > 3:
            textCountdown = self.font.render(f"{self.countdown}", True, (255, 255, 255))
        else:
            textCountdown = self.font.render(f"{self.countdown}", True, (255, 0, 0))

        self.screen.blit(textScore, (1080, 27))
        self.screen.blit(textLevel, (705, 27))
        self.screen.blit(textCountdown, (400, 27))

        if self.state != states.get("GAMEPLAY"):
            if self.state == states.get("TRANSITION"):
                prompt = "Level Beaten.     Press ENTER to Advance"
            elif self.state == states.get("WIN"):
                prompt = "You Win!     Press ENTER to Play Again     Press Q to Quit"
            elif self.state == states.get("LOSE"):
                prompt = "Game Over, You lost.     Press ENTER to Start Over     Press Q to Quit"
            textPrompt = self.promptFont.render(prompt, True, (255, 255, 255))
            promptRect = textPrompt.get_rect()
            promptRect.center = (WIDTH / 2, 100)
            self.screen.blit(textPrompt, (promptRect.midleft[0], 80))
    
    def drawWarpIndices(self):
        topleft = self.determineGridLocation(False)
        for i, xPos in enumerate(self.warpXPos):
            textWarp = self.font.render(f"{i + 1}", True, (255, 255, 255))
            if self.drawWarpIndex:
                self.screen.blit(textWarp, (xPos + 5, (topleft[1] + self.height)))

    def checkCollisions(self):
        self.checkPlayerCollisions()
        self.checkEnemyCollisions()
    
    def checkPlayerCollisions(self):
        self.playerBoundaryCollision()
        self.playerCookieCollision()
        self.playerEnemyCollision()
        self.playerGoalCollision()
        self.playerWarpCollision()
    
    def playerBoundaryCollision(self):
        boundaryCollision = pygame.sprite.spritecollide(self.p, self.wallGroup, False)
        for goal in self.goalGroup:
            if goal.wall:
                earlyGoalCollision = pygame.sprite.spritecollide(goal, self.player, False)
            else:
                earlyGoalCollision = None

        if boundaryCollision or earlyGoalCollision:
            self.p.rect.topleft = self.playerLastPos
        else:
            self.playerLastPos = self.p.rect.topleft
    
    def playerCookieCollision(self):
        cookieCollision = pygame.sprite.spritecollide(self.p, self.cookieGroup, False)
        if cookieCollision:
            self.playSFX("playereat.wav")
            self.score += 1
            if self.score == 5:
                self.playSFX("goalunlocked.wav")
            self.cookieGroup.empty()
            self.spawnCookie()
    
    def playerEnemyCollision(self):
        enemyCollision = pygame.sprite.spritecollide(self.p, self.enemyGroup, True)
        if enemyCollision:
            self.p.isalive = False
            self.p.handleDeath()
            self.state = states.get("LOSE")
    
    def playerGoalCollision(self):
        goalCollision = pygame.sprite.spritecollide(self.p, self.wallGroup, False)
        for goal in self.goalGroup:
            if goal.wall:
                goalCollision = None
            else:
                goalCollision = pygame.sprite.spritecollide(goal, self.player, False)
        
        if goalCollision:
            self.playSFX("goalreached.wav")
            if self.level != 3:
                self.state = states.get("TRANSITION")
            else:
                self.state = states.get("WIN")
    
    def playerWarpCollision(self):
        warpCollision = pygame.sprite.spritecollide(self.p, self.warpGroup, False)
        if warpCollision:
            self.drawWarpIndex = True
        else:
            self.drawWarpIndex = False

    def checkEnemyCollisions(self):
        for enemy in self.enemyGroup:
            self.enemyWallCollision(enemy)
            self.enemyCookieCollision(enemy)
            self.enemyEnemyCollision(enemy)
            self.enemyGoalCollision(enemy)

    def enemyWallCollision(self, enemy:Enemy):
        wallCollision = pygame.sprite.spritecollide(enemy, self.wallGroup, False)
        if wallCollision and enemy.type == 1:
            enemy.rect.topleft = enemy.oldpos
            enemy.speed.x *= -1
        if wallCollision and enemy.type == 2:
            enemy.rect.topleft = enemy.oldpos
            enemy.speed.y *= -1
    
    def enemyCookieCollision(self, enemy:Enemy):
        cookieCollision = pygame.sprite.spritecollide(enemy, self.cookieGroup, False)
        if cookieCollision:
            self.playSFX("enemyeat.wav")
            self.cookieGroup.empty()
            self.spawnCookie()
    
    def enemyEnemyCollision(self, enemy:Enemy):
        enemyCollision = pygame.sprite.spritecollide(enemy, self.enemyGroup, False)
        if len(enemyCollision) > 1:
            enemy.rect.topleft = enemy.oldpos
        else:
            enemy.oldpos = enemy.rect.topleft
    
    def enemyGoalCollision(self, enemy:Enemy):
        goalCollision = pygame.sprite.spritecollide(enemy, self.goalGroup, False)
        if goalCollision and enemy.type == 1:
            enemy.rect.topleft = enemy.oldpos
            enemy.speed.x *= -1
        if goalCollision and enemy.type == 2:
            enemy.rect.topleft = enemy.oldpos
            enemy.speed.y *= -1

    def playSFX(self, filename:str):
        sound = pygame.mixer.Sound(self.accessFile(filename))
        sound.play()
    
    def drawSpriteGroups(self):
        self.warpGroup.draw(self.screen)
        self.goalGroup.draw(self.screen)
        self.player.draw(self.screen)
        self.enemyGroup.draw(self.screen)
        self.cookieGroup.draw(self.screen)
        self.wallGroup.draw(self.screen)
    
    def emptySpriteGroups(self):
        self.wallGroup.empty()
        self.player.empty()
        self.enemyGroup.empty()
        self.cookieGroup.empty()
        self.goalGroup.empty()
        self.warpGroup.empty()
    
    @staticmethod
    def accessLevel(filename:str) -> str:
        cwd = os.path.dirname(__file__)
        path = f"{cwd}/Levels/{filename}"
        return path
    
    @staticmethod
    def accessFile(filename:str) -> str:
        cwd = os.path.dirname(__file__)
        path = f"{cwd}/Assets/{filename}"
        return path
    
if __name__ == "__main__":
    game = Game()
    game.run()
import pygame
import random
import sys

# ゲームの初期化
pygame.init()

# 画面設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("縦スクロールシューティングゲーム")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# FPS設定
clock = pygame.time.Clock()
FPS = 60

class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.speed = 5
        self.bullets = []
        self.bullet_speed = 7
        self.last_shot = 0
        self.shot_delay = 200  # ミリ秒
        
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
    
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shot_delay:
            bullet = {
                'x': self.x + self.width // 2 - 2,
                'y': self.y,
                'width': 4,
                'height': 10
            }
            self.bullets.append(bullet)
            self.last_shot = current_time
    
    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet['y'] -= self.bullet_speed
            if bullet['y'] < 0:
                self.bullets.remove(bullet)
    
    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        # 弾丸を描画
        for bullet in self.bullets:
            pygame.draw.rect(screen, YELLOW, (bullet['x'], bullet['y'], bullet['width'], bullet['height']))

class Enemy:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.speed = random.randint(2, 5)
        self.bullets = []
        self.bullet_speed = 4
        self.last_shot = 0
        self.shot_delay = random.randint(1000, 3000)  # ランダムな射撃間隔
    
    def update(self):
        self.y += self.speed
        
        # 敵の弾丸発射
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shot_delay:
            if random.random() < 0.3:  # 30%の確率で発射
                bullet = {
                    'x': self.x + self.width // 2 - 2,
                    'y': self.y + self.height,
                    'width': 4,
                    'height': 8
                }
                self.bullets.append(bullet)
                self.last_shot = current_time
                self.shot_delay = random.randint(1000, 3000)
        
        # 敵の弾丸更新
        for bullet in self.bullets[:]:
            bullet['y'] += self.bullet_speed
            if bullet['y'] > SCREEN_HEIGHT:
                self.bullets.remove(bullet)
    
    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        # 敵の弾丸を描画
        for bullet in self.bullets:
            pygame.draw.rect(screen, RED, (bullet['x'], bullet['y'], bullet['width'], bullet['height']))

class Game:
    def __init__(self):
        self.player = Player()
        self.enemies = []
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 1000  # ミリ秒
        self.game_over = False
        
    def spawn_enemy(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.enemy_spawn_timer > self.enemy_spawn_delay:
            self.enemies.append(Enemy())
            self.enemy_spawn_timer = current_time
            # 時間が経つにつれて敵の出現頻度を上げる
            if self.enemy_spawn_delay > 300:
                self.enemy_spawn_delay -= 5
    
    def check_collisions(self):
        # プレイヤーの弾丸と敵の衝突判定
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if (bullet['x'] < enemy.x + enemy.width and
                    bullet['x'] + bullet['width'] > enemy.x and
                    bullet['y'] < enemy.y + enemy.height and
                    bullet['y'] + bullet['height'] > enemy.y):
                    self.player.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    break
        
        # 敵の弾丸とプレイヤーの衝突判定
        for enemy in self.enemies:
            for bullet in enemy.bullets:
                if (bullet['x'] < self.player.x + self.player.width and
                    bullet['x'] + bullet['width'] > self.player.x and
                    bullet['y'] < self.player.y + self.player.height and
                    bullet['y'] + bullet['height'] > self.player.y):
                    self.game_over = True
                    return
        
        # プレイヤーと敵の直接衝突判定
        for enemy in self.enemies:
            if (self.player.x < enemy.x + enemy.width and
                self.player.x + self.player.width > enemy.x and
                self.player.y < enemy.y + enemy.height and
                self.player.y + self.player.height > enemy.y):
                self.game_over = True
                return
    
    def update(self):
        if not self.game_over:
            keys = pygame.key.get_pressed()
            self.player.move(keys)
            
            if keys[pygame.K_SPACE]:
                self.player.shoot()
            
            self.player.update_bullets()
            self.spawn_enemy()
            
            # 敵の更新と画面外の敵を削除
            for enemy in self.enemies[:]:
                enemy.update()
                if enemy.y > SCREEN_HEIGHT:
                    self.enemies.remove(enemy)
            
            self.check_collisions()
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        if not self.game_over:
            self.player.draw(screen)
            for enemy in self.enemies:
                enemy.draw(screen)
            
            # スコア表示
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            screen.blit(score_text, (10, 10))
        else:
            # ゲームオーバー画面
            game_over_text = self.font.render("GAME OVER", True, WHITE)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press R to restart or Q to quit", True, WHITE)
            
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
            screen.blit(score_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 50))
    
    def restart(self):
        self.__init__()

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game.game_over:
                    if event.key == pygame.K_r:
                        game.restart()
                    elif event.key == pygame.K_q:
                        running = False
        
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

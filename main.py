import pygame
import random
import sys

pygame.init()

# Настройки окна
WIDTH, HEIGHT = 700, 800
FPS = 100
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игра с пушкой и пришельцами")
clock = pygame.time.Clock()

# Загрузка картинок
gun_img = pygame.image.load("gun.png")
shield_img = pygame.image.load("lit.png")
alien_img = pygame.image.load("ino.png")

# Масштабирование
gun_img = pygame.transform.scale(gun_img, (50, 50))
shield_img = pygame.transform.scale(shield_img, (70, 50))
alien_img = pygame.transform.scale(alien_img, (50, 50))


class Gun(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = gun_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.hp = 3
        self.invincible = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += 5
        if self.invincible > 0:
            self.invincible -= 1

    def hit(self):
        if self.invincible == 0:
            self.hp -= 1
            self.invincible = FPS


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = alien_img
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hp = 2
        self.direction = 0
        self.vy = 0  # вертикальное движение

    def update(self):
        self.rect.x += self.direction
        self.rect.y += self.vy

        # Меняем горизонтальное направление при касании краёв
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction *= -1

        # Отскок от щитов без урона
        for shield in shields:
            if self.rect.colliderect(shield.rect):
                self.vy *= -1  # меняем направление по Y
                self.rect.y += self.vy * 5  # сдвигаем, чтобы не застревал

    def shoot(self):
        if random.randint(0, 300) == 0:
            bullet = Bullet(self.rect.centerx, self.rect.bottom, 5, WHITE)
            alien_bullets.add(bullet)



class Shield(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = shield_img.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hp = 40

    def update(self):
        if self.hp <= 0:
            self.kill()


def create_shields():
    group = pygame.sprite.Group()
    for x in (150, 450):
        shield = Shield(x, HEIGHT - 200)
        group.add(shield)
    return group


def create_aliens():
    group = pygame.sprite.Group()
    for row in range(3):
        for col in range(6):
            alien = Alien(80 + col * 90, 50 + row * 70)
            group.add(alien)
    return group


def draw_text(text, size, x, y, color=WHITE):
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


def reset_game():
    global gun, bullets, alien_bullets, aliens, shields, all_sprites, game_over, win
    gun = Gun()
    bullets = pygame.sprite.Group()
    alien_bullets = pygame.sprite.Group()
    aliens = create_aliens()
    shields = create_shields()
    all_sprites = pygame.sprite.Group(gun, shields, aliens)
    game_over = False
    win = False


reset_game()

# Игровой цикл
while True:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if not game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not any(b.rect.bottom < gun.rect.top for b in bullets):
                bullet = Bullet(gun.rect.centerx, gun.rect.top, -18, (0, 255, 0))
                bullets.add(bullet)
        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            if 260 < event.pos[0] < 440 and 400 < event.pos[1] < 450:
                reset_game()

    if not game_over:
        all_sprites.update()
        bullets.update()
        alien_bullets.update()

        for alien in aliens:
            alien.shoot()

        # Пули игрока попадают в пришельцев
        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, aliens, False)
            for alien in hits:
                alien.hp -= 1
                bullet.kill()
                if alien.hp <= 0:
                    alien.kill()

        # Пули пришельцев в пушку
        if pygame.sprite.spritecollide(gun, alien_bullets, True):
            gun.hit()

        # Пули в щиты
        for shield in shields:
            if pygame.sprite.spritecollide(shield, bullets, True) or pygame.sprite.spritecollide(shield, alien_bullets, True):
                shield.hp -= 1

        # Победа или поражение
        if len(aliens) == 0:
            game_over = True
            win = True
        if gun.hp <= 0:
            game_over = True

    # Отрисовка
    all_sprites.draw(screen)
    bullets.draw(screen)
    alien_bullets.draw(screen)

    draw_text(f"Gun HP: {gun.hp}", 24, 10, 10)

    # Показываем жизни у пришельцев
    for alien in aliens:
        draw_text(str(alien.hp), 18, alien.rect.x, alien.rect.y - 15)

    if game_over:
        msg = "YOU WIN!" if win else "GAME OVER"
        draw_text(msg, 50, WIDTH // 2 - 130, 200)
        pygame.draw.rect(screen, WHITE, (260, 400, 180, 50))
        draw_text("PLAY AGAIN", 30, 275, 410, BLACK)

    pygame.display.flip()
    clock.tick(FPS)

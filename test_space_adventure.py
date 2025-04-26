import pytest
import pygame
import os
from space_adventure import (
    Player, Enemy, Bullet, Powerup, 
    SCREEN_WIDTH, SCREEN_HEIGHT,
    load_image
)

# Initialize pygame for testing
pygame.init()
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

@pytest.fixture
def sprite_groups():
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    return {
        'all_sprites': all_sprites,
        'bullets': bullets,
        'enemies': enemies,
        'powerups': powerups
    }

@pytest.fixture
def player(sprite_groups):
    player = Player()
    sprite_groups['all_sprites'].add(player)
    return player

@pytest.fixture
def enemy(sprite_groups):
    enemy = Enemy()
    sprite_groups['all_sprites'].add(enemy)
    sprite_groups['enemies'].add(enemy)
    return enemy

@pytest.fixture
def bullet(player, sprite_groups):
    bullet = Bullet(player.rect.centerx, player.rect.top)
    sprite_groups['all_sprites'].add(bullet)
    sprite_groups['bullets'].add(bullet)
    return bullet

@pytest.fixture
def powerup(sprite_groups):
    powerup = Powerup()
    sprite_groups['all_sprites'].add(powerup)
    sprite_groups['powerups'].add(powerup)
    return powerup

def test_player_initialization(player):
    assert player.rect.centerx == SCREEN_WIDTH // 2
    assert player.rect.bottom == SCREEN_HEIGHT - 10
    assert player.shield == 100
    assert player.lives == 3
    assert not player.hidden
    assert player.power_level == 1

def test_player_movement(player, monkeypatch):
    # Test right movement
    keys = {pygame.K_RIGHT: True, pygame.K_LEFT: False}
    monkeypatch.setattr(pygame.key, 'get_pressed', lambda: keys)
    initial_x = player.rect.x
    player.update()
    assert player.rect.x > initial_x

    # Test left movement
    keys = {pygame.K_RIGHT: False, pygame.K_LEFT: True}
    monkeypatch.setattr(pygame.key, 'get_pressed', lambda: keys)
    initial_x = player.rect.x
    player.update()
    assert player.rect.x < initial_x

def test_player_screen_bounds(player):
    # Test right boundary
    player.rect.right = SCREEN_WIDTH + 100
    player.update()
    assert player.rect.right == SCREEN_WIDTH

    # Test left boundary
    player.rect.left = -100
    player.update()
    assert player.rect.left == 0

def test_enemy_initialization(enemy):
    assert 0 <= enemy.rect.x <= SCREEN_WIDTH - enemy.rect.width
    assert -150 <= enemy.rect.y <= -100
    assert 1 <= enemy.speedy <= 8
    assert -3 <= enemy.speedx <= 3

def test_enemy_movement(enemy):
    initial_pos = enemy.rect.y
    enemy.update()
    assert enemy.rect.y > initial_pos

def test_bullet_movement(bullet):
    initial_y = bullet.rect.y
    bullet.update()
    assert bullet.rect.y < initial_y
    assert bullet.speedy == -10

def test_powerup_movement(powerup):
    initial_y = powerup.rect.y
    powerup.update()
    assert powerup.rect.y > initial_y
    assert powerup.speedy == 4
    assert powerup.type in ['shield', 'power']

def test_player_power_up(player):
    initial_power = player.power_level
    player.powerup()
    assert player.power_level == initial_power + 1

def test_player_shooting(player, sprite_groups):
    # Test normal shot
    player.power_level = 1
    bullets = player.shoot(sprite_groups['all_sprites'], sprite_groups['bullets'])
    assert len(bullets) == 1
    assert len(sprite_groups['bullets']) == 1

    # Test powered up shot
    player.power_level = 2
    bullets = player.shoot(sprite_groups['all_sprites'], sprite_groups['bullets'])
    assert len(bullets) == 2
    assert len(sprite_groups['bullets']) == 3  # 1 from previous + 2 new ones
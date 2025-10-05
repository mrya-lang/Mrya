import os
import sys

# Pygame-based graphics system - lazy imports
pygame = None
initialized = False
screen = None
clock = None
background_image = None
all_sprites = None
font_cache = {}

def _ensure_pygame():
    global pygame, all_sprites
    if pygame is None:
        # Suppress pygame welcome message during import
        import contextlib
        import io
        import sys
        with contextlib.redirect_stdout(io.StringIO()):
            import pygame
        all_sprites = pygame.sprite.Group()

def init():
    global initialized, pygame, all_sprites
    _ensure_pygame()
    pygame.init()
    initialized = True
    # Suppress pygame welcome message by redirecting stdout temporarily
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        pygame.display.init()
    print("Pygame Graphics initialized")

def create_display(width, height):
    global screen, clock
    if not initialized:
        raise RuntimeError("Graphics not initialized. Call init() first.")
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    print(f"Display created: {width}x{height}")

def update(tick):
    if not initialized or screen is None:
        raise RuntimeError("Display not initialized.")
    pygame.display.flip()
    clock.tick(tick)

def get_events():
    if not initialized:
        raise RuntimeError("Graphics not initialized.")
    return pygame.event.get()

def get_event_type(event):
    return event.type

def get_event_key(event):
    return event.key if hasattr(event, 'key') else 0

def fill(r, g, b):
    if not initialized or screen is None:
        raise RuntimeError("Display not initialized.")
    screen.fill((r, g, b))

def get_const(const_name):
    _ensure_pygame()
    try:
        return getattr(pygame, const_name)
    except:
        raise RuntimeError(f"{const_name} is invaild const.")

def text(x, y, text_str, size, font_name, r, g, b):
    if not initialized or screen is None:
        raise RuntimeError("Display not initialized.")
    
    cache_key = (font_name, size)
    if cache_key not in font_cache:
        font_cache[cache_key] = pygame.font.SysFont(font_name, size)
    
    font = font_cache[cache_key]
    text_surface = font.render(str(text_str), True, (r, g, b))
    screen.blit(text_surface, (x, y))


def circle(x, y, radius, width, r, g, b):
    if not initialized or screen is None:
        raise RuntimeError("Display not initialized.")
    pygame.draw.circle(screen, (r, g, b), (x, y), radius, width)

def rect(x, y, sx, sy, r, g, b):
    if not initialized or screen is None:
        raise RuntimeError("Display not initialized.")
    pygame.draw.rect(screen, (r, g, b), (x, y, sx, sy))

def get_key_state(key):
    if not initialized:
        raise RuntimeError("Graphics not initialized.")
    return pygame.key.get_pressed()[key]

def update_key_states():
    # Pygame handles key states internally
    pass

# New functions for images and sprites
def load_image(path):
    if not initialized:
        raise RuntimeError("Graphics not initialized.")
    try:
        return pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        raise RuntimeError(f"Could not load image {path}: {e}")

def set_background(image):
    global background_image
    if not initialized:
        raise RuntimeError("Graphics not initialized.")
    background_image = image
    if screen and background_image:
        screen.blit(background_image, (0, 0))

class Sprite:
    def __init__(self, image, x, y):
        _ensure_pygame()
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

def create_sprite(image, x, y):
    if not initialized:
        raise RuntimeError("Graphics not initialized.")
    sprite = Sprite(image, x, y)
    all_sprites.add(sprite)
    return sprite

def draw_sprite(sprite):
    if not initialized or screen is None:
        raise RuntimeError("Display not initialized.")
    screen.blit(sprite.image, sprite.rect)

def update_sprites():
    if not initialized:
        raise RuntimeError("Graphics not initialized.")
    all_sprites.update()

def draw_all_sprites():
    if not initialized or screen is None:
        raise RuntimeError("Display not initialized.")
    all_sprites.draw(screen)

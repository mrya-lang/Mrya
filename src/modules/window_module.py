pygame = None
surface = None
fonts = {}
keys = None
clock = None

def init():
    global pygame, clock
    import pygame as pg
    pygame = pg
    pygame.init()
    clock = pygame.time.Clock()

def create_display(size_x, size_y):
    global surface
    if pygame is None:
        raise RuntimeError("Pygame not initialized. Call init() first.")
    surface = pygame.display.set_mode((size_x, size_y))

def update(tick):
    if pygame and surface:
        pygame.display.update()
        clock.tick(tick)

def get_events():
    return pygame.event.get()

def get_event_type(event):
    return event.type

def get_event_key(event):
    return event.key

def fill(r, g, b):
    surface.fill((r, g, b))

def get_const(const_name):
    try:
        return getattr(pygame, const_name)
    except:
        raise RuntimeError(f"{const_name} is invaild const.")

def text(x, y, text, size, font, r, g, b):
    global fonts

    if pygame is None or surface is None:
        raise RuntimeError("Display not initialized. Call init() and create_display() first.")

    key = (font, size)
    if key not in fonts:
        fonts[key] = pygame.font.SysFont(font, size)

    rendered = fonts[key].render(text, True, (r,g,b))
    surface.blit(rendered, (x, y))

def circle(x, y, radius, width, r, g, b):
    pygame.draw.circle(surface, (r, g, b), (x, y), radius, width)

def rect(x, y, sx, sy, r, g, b):
    pygame.draw.rect(surface, (r, g, b), pygame.Rect(x, y, sx, sy))

def get_key_state(key):
    global keys
    return keys[key]

def update_key_states():
    global keys
    keys = pygame.key.get_pressed()
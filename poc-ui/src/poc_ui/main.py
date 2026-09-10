from pathlib import Path

import pygame
import cv2
import numpy as np
import io
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # up from main.py -> poc_tts -> src -> poc-tts
PIKACHU_PNG = PROJECT_ROOT / "static" / "img" / "pikachu.png"
SPRITE_SCALE = 4


pygame.init()
screen = pygame.display.set_mode((1280, 720))  # match your display res
clock = pygame.time.Clock()

cap = cv2.VideoCapture(0)

class AppState:
    def __init__(self):
        self.mode = "camera"
        self.current_sprite_surface = None
        self.running = True

def cv2_frame_to_surface(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.rot90(frame)  # orientation depends on your camera mount
    return pygame.surfarray.make_surface(frame)

def blob_to_surface(sprite_bytes):
    img = Image.open(io.BytesIO(sprite_bytes)).convert("RGBA")  # keep alpha
    mode_, size, data = img.mode, img.size, img.tobytes()
    return pygame.image.fromstring(data, size, mode_)

def load_image_blob(path):
    with open(path, "rb") as f:
        return f.read()
def handle_events(state):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                toggle_mode(state)

def toggle_mode(state):
    if state.mode == "camera":
        sprite_bytes = load_image_blob(PIKACHU_PNG)
        surface = blob_to_surface(sprite_bytes).convert_alpha()
        state.current_sprite_surface = pygame.transform.scale(
            surface,
            (surface.get_width() * SPRITE_SCALE, surface.get_height() * SPRITE_SCALE)
        )
        state.mode = "sprite"
    else:
        state.mode = "camera"

def draw_camera(screen, cap):
    ret, frame = cap.read()
    if ret:
        surface = cv2_frame_to_surface(frame)
        surface = pygame.transform.scale(surface, screen.get_size())
        screen.blit(surface, (0, 0))

def draw_sprite(screen, state):
    screen.fill((0, 0, 0))
    if state.current_sprite_surface:
        rect = state.current_sprite_surface.get_rect(center=screen.get_rect().center)
        screen.blit(state.current_sprite_surface, rect)

def draw(screen, cap, state):
    if state.mode == "camera":
        draw_camera(screen, cap)
    elif state.mode == "sprite":
        draw_sprite(screen, state)

def main():
    state = AppState()

    while state.running:
        handle_events(state)
        draw(screen, cap, state)
        pygame.display.flip()
        clock.tick(30)

    cap.release()
    pygame.quit()

if __name__ == "__main__":
    main()
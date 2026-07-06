import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import pygame
import math
import random
import time

# --- Setup MediaPipe ---
base_options = mp_python.BaseOptions(model_asset_path='face_landmarker.task')
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    num_faces=1,
    min_face_detection_confidence=0.5,
    min_face_presence_confidence=0.5,
    min_tracking_confidence=0.5,
    output_face_blendshapes=True
)
detector = vision.FaceLandmarker.create_from_options(options)

# --- Define Pygame Game ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mind-Controlled Game (Fake BCI)")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Game Entities
player_w, player_h = 50, 50
player_x = WIDTH // 2 - player_w // 2
player_y = HEIGHT - player_h - 20
player_y_base = player_y

player_speed = 7
is_jumping = False
jump_speed = -15
gravity = 1
jump_velocity = 0

bullets = []
bullet_speed = -10

enemies = []
enemy_speed = 3
enemy_spawn_timer = 0
score = 0

font = pygame.font.SysFont(None, 36)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Cooldowns
last_shoot_time = 0
last_jump_time = 0

def get_distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def calculate_ear(landmarks, left_indices, right_indices):
    def ear(indices):
        h = get_distance(landmarks[indices[0]], landmarks[indices[1]])
        v1 = get_distance(landmarks[indices[2]], landmarks[indices[4]])
        v2 = get_distance(landmarks[indices[3]], landmarks[indices[5]])
        if h == 0: return 0
        return (v1 + v2) / (2.0 * h)
    return (ear(left_indices) + ear(right_indices)) / 2.0

# 468 landmark face mesh indices
LEFT_EYE = [33, 133, 159, 158, 145, 153]
RIGHT_EYE = [362, 263, 386, 385, 374, 380]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    success, frame = cap.read()
    if not success:
        continue
        
    frame = cv2.flip(frame, 1) # Mirror for natural feel
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    results = detector.detect(mp_image)
    
    # Defaults
    move_left = False
    move_right = False
    blink = False
    eyebrow_raise = False
    
    hud_text = "No Face Detected"
    
    if getattr(results, 'face_landmarks', None) and len(results.face_landmarks) > 0:
        landmarks = results.face_landmarks[0]
        
        # 1. Blink Detection (using our EAR)
        ear = calculate_ear(landmarks, LEFT_EYE, RIGHT_EYE)
        if ear < 0.22:
            blink = True
            
        # 2. Eyebrow raise (distance from eye to eyebrow)
        # 159 is left eye top. 105 is left eyebrow top.
        brow_dist = get_distance(landmarks[159], landmarks[105])
        # Average distance depends on face size, but generally > 0.05 is a raise for normalized coordinates
        # We can also use blendshapes!
        
        # Blendshapes are much more reliable if available
        # They come in results.face_blendshapes[0] which is a list of categories
        if getattr(results, 'face_blendshapes', None) and len(results.face_blendshapes) > 0:
            blendshapes = results.face_blendshapes[0]
            scores = {category.category_name: category.score for category in blendshapes}
            
            # Use blendshape for blink instead of EAR for precision!
            if scores.get('eyeBlinkLeft', 0) > 0.5 and scores.get('eyeBlinkRight', 0) > 0.5:
                blink = True
            else:
                blink = False
                
            if scores.get('browInnerUp', 0) > 0.5 or scores.get('browOuterUpLeft', 0) > 0.5:
                eyebrow_raise = True
                
            # Look Left / Right
            if scores.get('eyeLookInLeft', 0) > 0.4 or scores.get('eyeLookOutRight', 0) > 0.4:
                move_right = True # It's mirrored! Looking 'right' real-life -> moves right on screen
            elif scores.get('eyeLookOutLeft', 0) > 0.4 or scores.get('eyeLookInRight', 0) > 0.4:
                move_left = True
                
            hud_text = f"Blink: {scores.get('eyeBlinkLeft', 0):.2f} | Brow: {scores.get('browInnerUp', 0):.2f}"
        else:
            # Fallback to pure coordinates
            if brow_dist > 0.035:
                eyebrow_raise = True
                
            # Nose tracking for Left/Right
            nose_tip = landmarks[1].x
            if nose_tip < 0.45:
                # Left on screen (since it's mirrored it works naturally)
                move_left = True
            elif nose_tip > 0.55:
                move_right = True
                
            hud_text = f"EAR: {ear:.2f} | Brow: {brow_dist:.3f} | Nose: {nose_tip:.2f}"

    current_time = time.time()
    
    # Process Actions
    if move_left:
        player_x -= player_speed
    if move_right:
        player_x += player_speed
        
    # Keep on screen
    player_x = max(0, min(WIDTH - player_w, player_x))
    
    if eyebrow_raise and not is_jumping and (current_time - last_jump_time > 0.5):
        is_jumping = True
        jump_velocity = jump_speed
        last_jump_time = current_time
        
    if blink and (current_time - last_shoot_time > 0.3):
        bullets.append([player_x + player_w//2 - 5, player_y])
        last_shoot_time = current_time

    # Update Jump
    if is_jumping:
        player_y += jump_velocity
        jump_velocity += gravity
        if player_y >= player_y_base:
            player_y = player_y_base
            is_jumping = False
            
    # Update Bullets
    for b in bullets[:]:
        b[1] += bullet_speed
        if b[1] < 0:
            bullets.remove(b)
            
    # Update Enemies
    enemy_spawn_timer += 1
    if enemy_spawn_timer > 60:
        enemy_size = 40
        ex = random.randint(0, WIDTH - enemy_size)
        enemies.append([ex, -enemy_size, enemy_size])
        enemy_spawn_timer = 0
        
    for e in enemies[:]:
        e[1] += enemy_speed
        if e[1] > HEIGHT:
            enemies.remove(e)
            
    # Collisions
    for b in bullets[:]:
        b_rect = pygame.Rect(b[0], b[1], 10, 20)
        for e in enemies[:]:
            e_rect = pygame.Rect(e[0], e[1], e[2], e[2])
            if b_rect.colliderect(e_rect):
                if b in bullets: bullets.remove(b)
                if e in enemies: enemies.remove(e)
                score += 10
                break

    # Rendering
    screen.fill(BLACK)
    
    # Draw Player
    pygame.draw.rect(screen, GREEN, (player_x, player_y, player_w, player_h))
    
    # Draw Bullets
    for b in bullets:
        pygame.draw.rect(screen, YELLOW, (b[0], b[1], 10, 20))
        
    # Draw Enemies
    for e in enemies:
        pygame.draw.rect(screen, RED, (e[0], e[1], e[2], e[2]))
        
    # Show PiP webcam
    frame = cv2.resize(frame, (160, 120))
    # Pygame needs Surface (rgb):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_surf = pygame.image.frombuffer(frame_rgb.flatten(), (160, 120), 'RGB')
    screen.blit(frame_surf, (WIDTH - 170, 10))
    
    # Text
    score_surf = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_surf, (10, 10))
    
    controls_surf = font.render("Look L/R: Move | Brow: Jump | Blink: Shoot", True, WHITE)
    screen.blit(controls_surf, (10, HEIGHT - 40))
    
    hud_surf = font.render(hud_text, True, BLUE)
    screen.blit(hud_surf, (200, 10))
    
    pygame.display.flip()
    clock.tick(30)

cap.release()
pygame.quit()

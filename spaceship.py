import pygame
import speech_recognition as sr
from config import *
from tools import MovingDirection
import threading

latest_command = None

class Missile:
    def __init__(self):
        self.rect = None
        self.moving_direction = MovingDirection.UP
        self.move_amount = 0
        self.time_since_explosion = 0
        self.explosion_sprite = pygame.image.load(SPRITE_PATH + MISSILE_EXPLOSION_SPRITE_NAME)
        self.is_exploded = False
        self.is_active = False

    def launch(self, rect):
        self.rect = rect
        self.moving_direction = MovingDirection.UP
        self.move_amount = 0
        self.is_exploded = False
        self.time_since_explosion = 0
        self.is_active = True

    def update(self, dt):
        if not self.is_active:
            return
        if self.is_exploded:
            self.time_since_explosion += dt
        else:
            self._move(dt)

    def _move(self, dt):
        if self.moving_direction == MovingDirection.IDLE:
            return
        dt_s = dt / 1000
        self.move_amount += dt_s * MISSILE_SPEED_PIXEL_PER_SECOND
        if self.move_amount > 1.:
            direction = -1 if self.moving_direction == MovingDirection.UP else 1
            self.rect.y += int(self.move_amount) * direction
            self.move_amount -= int(self.move_amount)

    def draw(self, surf: pygame.Surface):
        if not self.is_active:
            return
        if self.is_exploded:
            surf.blit(self.explosion_sprite, self.explosion_sprite.get_rect(center=self.rect.center))
        else:
            pygame.draw.rect(surf, MISSILE_RECT_COLOR, self.rect)

    def explode(self):
        self.is_exploded = True

    def set_inactive(self):
        self.is_active = False

class Spaceship:
    def __init__(self):
        self.sprite = pygame.image.load(SPRITE_PATH + SPACESHIP_SPRITE_NAME)
        self.rect = self.sprite.get_rect(center=SPACESHIP_STARTING_POSITION)
        self.destruction_sprite = pygame.image.load(SPRITE_PATH + SPACESHIP_DESTRUCTION_SPRITE_NAME)
        self.shoot_sound = pygame.mixer.Sound(SOUND_PATH + SPACESHIP_SHOOT_SOUND)
        self.destruction_sound = pygame.mixer.Sound(SOUND_PATH + SPACESHIP_DESTRUCTION_SOUND)
        self.moving_direction = MovingDirection.IDLE
        self.move_amount = 0
        self.is_firing = False
        self.missile = Missile()
        self.is_destroyed = False  # Ensure this attribute is initialized
        self.delay_since_explosion = 0
        self.is_active = True
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognition_thread = None
        self.should_listen = True
        self.start_listening()

    def reset(self):
        self.shoot_sound.stop()
        self.destruction_sound.stop()
        self.rect = self.sprite.get_rect(center=SPACESHIP_STARTING_POSITION)
        self.moving_direction = MovingDirection.IDLE
        self.move_amount = 0
        self.is_firing = False
        self.is_destroyed = False
        self.delay_since_explosion = 0
        self.is_active = True

    def update(self, dt, events):
        self._handle_events(events)
        if not self.is_destroyed:
            self._move(dt)
            self._update_missile(dt)
            self._fire()
        else:
            self.delay_since_explosion += dt
            if self.is_destroyed and self.delay_since_explosion > SPACESHIP_EXPLOSION_DURATION_MS:
                self.is_active = False

    def start_listening(self):
        print("Starting listening thread...")
        self.should_listen = True
        self.recognition_thread = threading.Thread(target=self.listen_for_launch_command, daemon=True)
        self.recognition_thread.start()

    def stop_listening(self):
        print("Stopping listening thread...")
        self.should_listen = False
        if self.recognition_thread:
            self.recognition_thread.join()
            self.recognition_thread = None

    def listen_for_launch_command(self):
        global latest_command
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.should_listen:
                print("Listening for launch command...")
                audio = self.recognizer.listen(source)
                try:
                    command = self.recognizer.recognize_google(audio)
                    latest_command = command.lower()
                    print(f"Heard: {command}")
                    if "fire" in latest_command:
                        self.is_firing = True
                    elif "left" in latest_command:
                        self.moving_direction = MovingDirection.LEFT
                    elif "right" in latest_command:
                        self.moving_direction = MovingDirection.RIGHT
                except sr.UnknownValueError:
                    print("Could not understand the command")
                except sr.RequestError:
                    print("Could not request results; check your network connection")
                except Exception as e:
                    print(f"Error in listening thread: {e}")

    def draw(self, surf: pygame.Surface):
        if self.is_active:
            if self.is_destroyed:
                self.destruction_sprite = pygame.transform.flip(self.destruction_sprite, True, False)
                surf.blit(self.destruction_sprite, self.rect)
            else:
                surf.blit(self.sprite, self.rect)
        if self.missile.is_active:
            self.missile.draw(surf)

    def _handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.moving_direction = MovingDirection.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.moving_direction = MovingDirection.RIGHT
                elif event.key == pygame.K_SPACE:
                    self.is_firing = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and self.moving_direction == MovingDirection.LEFT:
                    self.moving_direction = MovingDirection.IDLE
                elif event.key == pygame.K_RIGHT and self.moving_direction == MovingDirection.RIGHT:
                    self.moving_direction = MovingDirection.IDLE
                elif event.key == pygame.K_SPACE:
                    self.is_firing = False

    def _move(self, dt):
        if self.moving_direction == MovingDirection.IDLE:
            return
        dt_s = dt / 1000
        self.move_amount += dt_s * SPACESHIP_SPEED_PIXEL_PER_SECOND
        if self.move_amount > 1.:
            direction = -1 if self.moving_direction == MovingDirection.LEFT else 1
            self.rect.x += int(self.move_amount) * direction
            self.move_amount -= int(self.move_amount)
            if self.rect.left < 0:
                self.rect.x = 0
            if self.rect.right >= WORLD_DIM[0]:
                self.rect.right = WORLD_DIM[0] - 1

    def _update_missile(self, dt):
        if not self.missile.is_active:
            return
        self.missile.update(dt)
        if self.missile.rect.top < 0:
            self.missile.rect.top = 0
            self.missile.explode()
        if self.missile.time_since_explosion > ALIEN_EXPLOSION_DURATION_MS:
            self.missile.set_inactive()

    def _fire(self):
        if not self.is_firing:
            return
        if self.missile.is_active:
            return
        self._launch_missile()
        self.shoot_sound.play()
        self.is_firing = False

    def destroy(self):
        self.is_destroyed = True
        self.destruction_sound.play()

    def _launch_missile(self):
        missile_rect = pygame.Rect(
            self.rect.centerx - (MISSILE_RECT_DIM[0]),
            self.rect.top - MISSILE_RECT_DIM[1],
            MISSILE_RECT_DIM[0],
            MISSILE_RECT_DIM[1]
        )
        self.missile.launch(missile_rect)

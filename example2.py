import pygame
import threading
import speech_recognition as sr

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Voice Controlled Spaceship")

# Set up voice recognition
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Global variable to control spaceship movement
moving_left = False

def listen_for_commands():
    global moving_left
    while True:
        with microphone as source:
            print("Listening for commands...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio)
                print(f"Recognized command: {command}")
                command = command.lower()
                if "stop" in command:
                    moving_left = False
                else:
                    moving_left = True
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

# Start the voice command thread
command_thread = threading.Thread(target=listen_for_commands)
command_thread.daemon = True
command_thread.start()

class Spaceship:
    def __init__(self):
        self.x = 400
        self.y = 300
        self.size = 50
        self.speed = 5
    
    def move_left(self):
        self.x -= self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.size, self.size))

# Create an instance of Spaceship
spaceship = Spaceship()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move spaceship left if the global flag is set
    if moving_left:
        spaceship.move_left()

    # Clear screen
    screen.fill((0, 0, 0))

    # Draw the spaceship
    spaceship.draw(screen)

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(30)

pygame.quit()
import pygame
import threading
import speech_recognition as sr

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Multimodal Control Example")

# Set up voice recognition
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Global variable to store the latest voice command
latest_command = None

def listen_for_commands():
    global latest_command
    while True:
        with microphone as source:
            print("Listening for commands...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio)
                print(f"Recognized command: {command}")
                latest_command = command.lower()
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

# Start the voice command thread
command_thread = threading.Thread(target=listen_for_commands)
command_thread.daemon = True
command_thread.start()

# Game variables
rect_x, rect_y = 400, 300
rect_speed = 5
rect_size = 50

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle keyboard input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        rect_x -= rect_speed
    if keys[pygame.K_RIGHT]:
        rect_x += rect_speed
    if keys[pygame.K_UP]:
        rect_y -= rect_speed
    if keys[pygame.K_DOWN]:
        rect_y += rect_speed

    # Handle voice commands
    if latest_command:
        if "fire" in latest_command:
            rect_x -= 8*rect_speed
        elif "r" in latest_command:
            rect_x += rect_speed
        elif "u" in latest_command:
            rect_y -= rect_speed
        elif "d" in latest_command:
            rect_y += rect_speed
        # Reset the latest command after processing
        latest_command = None

    # Clear screen
    screen.fill((0, 0, 0))

    # Draw the rectangle
    pygame.draw.rect(screen, (255, 0, 0), (rect_x, rect_y, rect_size, rect_size))

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(30)

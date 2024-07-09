import pygame
import sys
import speech_recognition as sr

# Initialize Pygame
pygame.init()

# Set up the display
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pygame Text Example")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Create a font object
font = pygame.font.Font(None, 36)  # None means default font, 36 is the font size

# Initialize speech recognizer
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Speech recognition logic
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"Recognized command: {command}")
        
        # Check for the "fire" command
        if "fire" in command:
            text_to_display = "Hello, Pygame!"
            text_surface = font.render(text_to_display, True, BLACK)
            screen.fill(WHITE)  # Clear the screen
            text_rect = text_surface.get_rect()
            text_rect.center = (screen_width // 2, screen_height // 2)
            screen.blit(text_surface, text_rect)
            pygame.display.flip()  # Update the display
            
    except sr.UnknownValueError:
        print("Could not understand the command")
    except sr.RequestError:
        print("Could not request results; check your network connection")
    except Exception as e:
        print(f"Error in speech recognition: {e}")

# Quit Pygame
pygame.quit()
sys.exit()
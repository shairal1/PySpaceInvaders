import speech_recognition as sr

def listen_for_launch_command():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening for launch command...")
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            print(f"Heard: {command}")
            if "fire" in command.lower():
                print("Firing command recognized!")
            else:
                print("Unknown command:", command)
        except sr.UnknownValueError:
            print("Could not understand the command")
        except sr.RequestError:
            print("Could not request results; check your network connection")

if __name__ == "__main__":
    listen_for_launch_command()
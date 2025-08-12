import speech_recognition as sr
import pyttsx3
import webbrowser
from datetime import datetime
import sys
import time

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 160)  # speech rate

def say(text):
    """Speak the given text and also print it."""
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# Initialize speech recognizer
recognizer = sr.Recognizer()

def listen(timeout=5, phrase_time_limit=6):
    """
    Listen from the microphone and return recognized text.
    On failure, returns None.
    """
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            print("Listening... (speak now)")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        # Use Google Web Speech API (default). This requires internet.
        text = recognizer.recognize_google(audio)
        print("You:", text)
        return text.lower()
    except sr.WaitTimeoutError:
        print("Listening timed out — no speech detected.")
        return None
    except sr.RequestError:
        # API was unreachable or unresponsive
        print("Speech recognition service unavailable.")
        return None
    except sr.UnknownValueError:
        # speech was unintelligible
        print("Couldn't understand audio.")
        return None
    except Exception as e:
        print(f"Microphone error: {e}")
        return None

def get_text_input(prompt="Type your command: "):
    """Fallback typed input if voice not available."""
    try:
        return input(prompt).strip().lower()
    except KeyboardInterrupt:
        return "exit"
    except Exception:
        return ""

# Command handlers
def handle_greeting():
    responses = [
        "Hello! How can I help you?",
        "Hi there! What can I do for you?",
        "Hey! Ready when you are."
    ]
    say(responses[int(time.time()) % len(responses)])

def handle_time():
    now = datetime.now().strftime("%I:%M %p")
    say(f"The time is {now}")

def handle_date():
    today = datetime.now().strftime("%A, %B %d, %Y")
    say(f"Today is {today}")

def handle_search(query):
    # strip trigger words
    # open a Google search in default browser
    if not query:
        say("What would you like me to search for?")
        return
    say(f"Searching the web for {query}")
    url = "https://www.google.com/search?q=" + webbrowser.quote(query)
    webbrowser.open(url)

def handle_help():
    say("I can greet you, tell the time or date, and search the web. Say 'exit' to stop.")

def parse_and_execute(command):
    """Very simple rule-based parser for beginner assistant."""
    if command is None:
        return False  # nothing to do, continue loop

    # common exit forms
    if any(tok in command for tok in ("exit", "quit", "goodbye", "stop")):
        say("Goodbye! Have a nice day.")
        return True  # signal to terminate

    if any(greet in command for greet in ("hello", "hi", "hey", "good morning", "good afternoon", "good evening")):
        handle_greeting()
        return False

    if "time" in command:
        handle_time()
        return False

    if "date" in command or "day is it" in command:
        handle_date()
        return False

    if command.startswith("search ") or command.startswith("google "):
        # user said "search cats" or "google python"
        query = command.split(" ", 1)[1] if " " in command else ""
        handle_search(query)
        return False

    # if user said "search for X" handle that
    if "search for" in command:
        query = command.split("search for",1)[1].strip()
        handle_search(query)
        return False

    if "help" in command:
        handle_help()
        return False

    # if nothing matched, ask follow-up
    say("Sorry, I didn't understand that. I can tell time, date, or search the web. Say 'help' for options.")
    return False

def main_loop():
    say("Voice assistant started. Say 'help' to hear what I can do.")
    while True:
        # Try listening first
        cmd = listen()
        if cmd is None:
            # fallback to typed input
            say("I didn't catch that. You can type your command instead.")
            cmd = get_text_input()
            if not cmd:
                # if still empty, continue
                continue
        # parse and act
        should_exit = parse_and_execute(cmd)
        if should_exit:
            break

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        say("Shutting down. Goodbye!")
        try:
            sys.exit(0)
        except SystemExit:
            pass

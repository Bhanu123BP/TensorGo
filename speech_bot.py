import openai
import speech_recognition as sr
import pyttsx3
import threading
import sys
import tkinter as tk
from tkinter import scrolledtext
import config

engine = pyttsx3.init()

# Initialize the GUI window
root = tk.Tk()
root.title("🤖 Speech-to-Speech LLM Bot")
root.geometry("700x500")

# Chat display area
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20)
text_area.pack(pady=10)

# Flag to control listening state
listening = False  
stop_listening_event = threading.Event()  # Event to control listening flow

def update_text_area(message):
    """Update the chat display with user and bot messages."""
    text_area.insert(tk.END, message + "\n")
    text_area.yview(tk.END)  # Auto-scroll to the latest message

def recognize_speech():
    """Listen for user speech and return recognized text."""
    global listening
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        update_text_area("🤖 Bot: Listening...")  # Display in text field
        root.update()
        recognizer.adjust_for_ambient_noise(source)

        try:
            audio = recognizer.listen(source, timeout=8)
            text = recognizer.recognize_google(audio)
            update_text_area(f"Bhanu: {text}")
            return text.lower()
        except sr.UnknownValueError:
            update_text_area("🤖 Bot: Sorry, I couldn't understand that.")
            return None
        except sr.RequestError:
            update_text_area("🤖 Bot: API unavailable.")
            return None

def generate_response(text):
    """Generate a response using OpenAI API."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text}],
            temperature=0.7,
            max_tokens=100
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        update_text_area(f"🤖 Bot: Error with OpenAI API: {e}")
        return "Sorry, something went wrong."

def speak_response(response_text):
    """Speak out the bot's response in a separate thread."""
    def run_tts():
        global listening
        listening = False  # Stop listening while speaking
        stop_listening_event.set()  # Pause listening
        engine.say(response_text)
        engine.runAndWait()
        stop_listening_event.clear()  # Resume listening
        root.after(500, start_listening)  # Restart listening after speaking

    tts_thread = threading.Thread(target=run_tts, daemon=True)
    tts_thread.start()

def process_conversation():
    """Continuously process speech and responses."""
    global listening

    if not listening or stop_listening_event.is_set():
        return  

    user_input = recognize_speech()
    if user_input is None:
        return  

    if "exit" in user_input:
        update_text_area("🤖 Bot: Exiting. Goodbye!")
        speak_response("Exiting. Goodbye!")
        root.after(1000, exit_bot)  
        return

    response = generate_response(user_input)
    update_text_area(f"🤖 Bot: {response}")

    # Speak the response and only listen again after speaking is done
    speak_response(response)

def start_listening():
    """Start listening for user speech in a separate thread."""
    global listening
    if not listening:
        listening = True
        thread = threading.Thread(target=process_conversation, daemon=True)
        thread.start()

def exit_bot():
    """Exit the bot application cleanly."""
    root.destroy()
    sys.exit()

# Buttons
listen_button = tk.Button(root, text="Start Listening", command=start_listening, font=("Arial", 12), bg="green", fg="white")
listen_button.pack(pady=10)

exit_button = tk.Button(root, text="Exit", command=exit_bot, font=("Arial", 12), bg="red", fg="white")
exit_button.pack(pady=5)

root.mainloop()

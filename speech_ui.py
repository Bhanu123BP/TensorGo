import openai
import speech_recognition as sr
import pyttsx3
import threading
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import cv2
import config

# Here Initializing Text-to-Speech Engine
engine = pyttsx3.init()

running = True  

cap = cv2.VideoCapture(0)

def recognize_speech():
    """Listens for user speech input."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        text_display.insert(tk.END, "\n🔵 Listening your voice...\n")
        text_display.see(tk.END)  # Auto-scroll
        recognizer.adjust_for_ambient_noise(source)

        try:
            audio = recognizer.listen(source, timeout=3)
            text = recognizer.recognize_google(audio)
            text_display.insert(tk.END, f"🟢 Bhanu: {text}\n")
            text_display.see(tk.END)
            return text
        except sr.UnknownValueError:
            text_display.insert(tk.END, "⚠️ Could not understand. Try again.\n")
        except sr.RequestError:
            text_display.insert(tk.END, "⚠️ API unavailable. Check connection.\n")
        except sr.WaitTimeoutError:
            text_display.insert(tk.END, "⚠️ Timeout! No speech detected.\n")
        except Exception as e:
            text_display.insert(tk.END, f"⚠️ Error: {e}\n")

        text_display.see(tk.END)
        return None

def generate_response(text):
    """Generates AI response based on user speech."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text}],
            temperature=0.7,
            max_tokens=150
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        text_display.insert(tk.END, f"⚠️ OpenAI Error: {e}\n")
        text_display.see(tk.END)
        return "Sorry, something went wrong."

def speak_response(response_text):
    """Speaks AI response using Text-to-Speech."""
    engine.say(response_text)
    engine.runAndWait()

def update_video():
    """Updates the video feed in the UI."""
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
    video_label.after(10, update_video)

def start_conversation():
    """Continuously listens and responds."""
    global running
    running = True  

    while running:
        user_input = recognize_speech()

        if user_input:
            if user_input.lower() == "exit":
                text_display.insert(tk.END, "🔴 Exiting the bot. Goodbye!\n")
                text_display.see(tk.END)
                stop_conversation()
                return  
            
            response = generate_response(user_input)
            text_display.insert(tk.END, f"🤖 Bot: {response}\n")
            text_display.see(tk.END)

            speech_thread = threading.Thread(target=speak_response, args=(response,))
            speech_thread.start()
            speech_thread.join()  

def stop_conversation():
    """Stops the conversation and gracefully exits."""
    global running
    running = False
    cap.release()
    root.quit()  

root = tk.Tk()
root.title("🤖 Speech-to-Speech LLM Bot")

main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10)

video_label = tk.Label(main_frame)
video_label.pack(side=tk.LEFT, padx=10)

text_display = scrolledtext.ScrolledText(main_frame, width=50, height=20, font=("Arial", 12))
text_display.pack(side=tk.RIGHT, padx=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="🎤 Start Listening", font=("Arial", 12), command=lambda: threading.Thread(target=start_conversation).start())
start_button.pack(side=tk.LEFT, padx=5)

exit_button = tk.Button(button_frame, text="❌ Exit", font=("Arial", 12), command=stop_conversation)
exit_button.pack(side=tk.RIGHT, padx=5)

update_video()
root.mainloop()
import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser
import datetime
from pynput.keyboard import Key, Controller
import pyautogui
import sys
import os
from os import listdir
from os.path import isfile, join, normpath
import smtplib
import wikipedia
import Gesture_Controller
#import Gesture_Controller_Gloved as Gesture_Controller
import app
from queue import Queue
from threading import Thread
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Thread-safe TTS queue and worker
tts_queue = Queue()
def tts_worker():
    while True:
        text = tts_queue.get()
        if text is None:
            break
        try:
            engine.say(text)
            engine.runAndWait()
            # Add a small delay to ensure TTS engine is ready for next message
            time.sleep(0.1)
        except Exception as e:
            logging.error(f"TTS error: {e}")
        tts_queue.task_done()

tts_thread = Thread(target=tts_worker, daemon=True)
tts_thread.start()

# ----------------Variables------------------------
file_exp_status = False
files = []
path = ''
is_awake = True  # Bot status
last_reply = ""  # Store last reply for repeat command

# ------------------Functions----------------------
def reply(audio):
    """Send reply to user via TTS and GUI."""
    global last_reply
    logging.info(f"Reply: {audio}")
    print(audio)
    tts_queue.put(audio)
    last_reply = audio
    app.ChatBot.addAppMsg(audio)


def wish():
    """Greet the user based on the time of day."""
    hour = int(datetime.datetime.now().hour)

    if hour >= 0 and hour < 12:
        reply("Good Morning!")
    elif hour >= 12 and hour < 18:
        reply("Good Afternoon!")
    else:
        reply("Good Evening!")

    reply("I am Proton, how may I help you?")


# Set Microphone parameters
with sr.Microphone() as source:
    r.energy_threshold = 500
    r.dynamic_energy_threshold = False


def record_audio(retry=1):
    """
    Listen from microphone and convert audio to text.
    Retries once if recognition fails.
    """
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        voice_data = ''
        try:
            audio = r.listen(source, phrase_time_limit=7)
            voice_data = r.recognize_google(audio)
        except sr.RequestError:
            reply('Sorry my Service is down. Please check your Internet connection.')
        except sr.UnknownValueError:
            if retry > 0:
                logging.info("Speech not recognized, retrying...")
                return record_audio(retry=retry-1)
            else:
                logging.info('Could not recognize speech.')
        except Exception as e:
            logging.error(f"Error in record_audio: {e}")
        return voice_data.lower()


def send_email(to_address, subject, message, from_address, password, smtp_server='smtp.gmail.com', smtp_port=587):
    """
    Send an email using SMTP.
    """
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_address, password)
        email_message = f"Subject: {subject}\n\n{message}"
        server.sendmail(from_address, to_address, email_message)
        server.quit()
        reply("Email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        reply("Failed to send email. Please check the details and try again.")


def respond(voice_data):
    """
    Process the voice command and execute corresponding actions.
    """
    global file_exp_status, files, is_awake, path

    if not voice_data:
        return

    logging.info(f"Received command: {voice_data}")
    print(voice_data)
    # Remove 'proton' from the command for easier matching
    voice_data = voice_data.replace('proton', '').strip()
    app.eel.addUserMsg(voice_data)

    if is_awake is False:
        if 'wake up' in voice_data:
            is_awake = True
            wish()
        return

    # STATIC CONTROLS
    if 'hello' in voice_data:
        wish()
        return

    if 'what is your name' in voice_data:
        reply('My name is Proton!')
        return

    if 'date' in voice_data:
        reply(today.strftime("%B %d, %Y"))
        return

    if 'time' in voice_data:
        reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])
        return

    if 'search' in voice_data:
        try:
            search_term = voice_data.split('search', 1)[1].strip()
        except IndexError:
            search_term = ''
        reply('Searching for ' + search_term)
        url = 'https://google.com/search?q=' + search_term
        try:
            webbrowser.get().open(url)
            reply('This is what I found Sir')
        except Exception as e:
            logging.error(f"Webbrowser error: {e}")
            reply('Please check your Internet connection.')
        return

    if 'location' in voice_data:
        reply('Which place are you looking for?')
        temp_audio = record_audio()
        app.eel.addUserMsg(temp_audio)
        reply('Locating...')
        url = 'https://google.nl/maps/place/' + temp_audio + '/'
        try:
            webbrowser.get().open(url)
            reply('This is what I found Sir')
        except Exception as e:
            logging.error(f"Webbrowser error: {e}")
            reply('Please check your Internet connection.')
        return

    if 'wikipedia' in voice_data:
        try:
            topic = voice_data.split('wikipedia', 1)[1].strip()
            reply(f"Searching Wikipedia for {topic}")
            summary = wikipedia.summary(topic, sentences=2)
            reply(summary)
        except Exception as e:
            logging.error(f"Wikipedia error: {e}")
            reply("Sorry, I couldn't find any information on that topic.")
        return

    if 'repeat' in voice_data:
        if last_reply:
            reply(last_reply)
        else:
            reply("I have nothing to repeat.")
        return

    if 'help' in voice_data:
        help_text = (
            "You can ask me to tell the time, date, search the web, locate places, "
            "launch or stop gesture recognition, copy or paste, list files, open files or folders, "
            "send email, or say goodbye to exit."
        )
        reply(help_text)
        return

    if ('bye' in voice_data) or ('by' in voice_data):
        reply("Good bye Sir! Have a nice day.")
        is_awake = False
        return

    if ('exit' in voice_data) or ('terminate' in voice_data) or ('shutdown' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        reply("Shutting down. Goodbye!")
        app.ChatBot.close()
        # Graceful shutdown for TTS thread
        tts_queue.put(None)
        tts_thread.join()
        sys.exit()
        return

    # DYNAMIC CONTROLS
    if 'launch gesture recognition' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active')
        else:
            gc = Gesture_Controller.GestureController()
            t = Thread(target=gc.start)
            t.start()
            reply('Launched Successfully')
        return

    if ('stop gesture recognition' in voice_data) or ('top gesture recognition' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped')
        else:
            reply('Gesture recognition is already inactive')
        return

    if 'copy' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('c')
            keyboard.release('c')
        reply('Copied')
        return

    if 'page' in voice_data or 'pest' in voice_data or 'paste' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('v')
            keyboard.release('v')
        reply('Pasted')
        return

    # File Navigation (Default Folder set to C:\)
    if 'list' in voice_data:
        counter = 0
        path = 'C:\\'
        try:
            files = listdir(path)
        except Exception as e:
            logging.error(f"Error listing directory {path}: {e}")
            reply("Unable to list files in the directory.")
            return
        filestr = ""
        for f in files:
            counter += 1
            logging.info(f"File {counter}: {f}")
            filestr += f"{counter}:  {f}<br>"
        file_exp_status = True
        reply('These are the files in your root directory')
        app.ChatBot.addAppMsg(filestr)
        return

    if file_exp_status:
        counter = 0
        if 'open' in voice_data:
            try:
                idx = int(voice_data.split(' ')[-1]) - 1
                full_path = normpath(os.path.join(path, files[idx]))
                if isfile(full_path):
                    os.startfile(full_path)
                    file_exp_status = False
                else:
                    path = normpath(os.path.join(path, files[idx])) + os.sep
                    files = listdir(path)
                    filestr = ""
                    for f in files:
                        counter += 1
                        filestr += f"{counter}:  {f}<br>"
                        logging.info(f"File {counter}: {f}")
                    reply('Opened Successfully')
                    app.ChatBot.addAppMsg(filestr)
            except Exception as e:
                logging.error(f"Error opening file/folder: {e}")
                reply('You do not have permission to access this folder or invalid index.')
            return
        if 'back' in voice_data:
            filestr = ""
            if os.path.normpath(path) == os.path.normpath('C:\\'):
                reply('Sorry, this is the root directory')
            else:
                try:
                    a = os.path.normpath(path).split(os.sep)[:-1]
                    path = os.sep.join(a) + os.sep
                    files = listdir(path)
                    for f in files:
                        counter += 1
                        filestr += f"{counter}:  {f}<br>"
                        logging.info(f"File {counter}: {f}")
                    reply('ok')
                    app.ChatBot.addAppMsg(filestr)
                except Exception as e:
                    logging.error(f"Error going back in directory: {e}")
                    reply("Cannot go back further.")
            return

    # If no command matched
    reply('I am not functioned to do this!')


# ------------------Driver Code--------------------

t1 = Thread(target=app.ChatBot.start)
t1.start()

# Lock main thread until Chatbot has started
while not app.ChatBot.started:
    time.sleep(0.5)

wish()
voice_data = None
try:
    while True:
        if app.ChatBot.isUserInput():
            # take input from GUI
            voice_data = app.ChatBot.popUserInput()
            logging.info(f"GUI input: {voice_data}")
        else:
            # take input from Voice
            voice_data = record_audio()
            logging.info(f"Voice input: {voice_data}")

        # process voice_data
        if voice_data and voice_data.strip():
            try:
                respond(voice_data)
            except SystemExit:
                reply("Exit Successful")
                break
            except Exception as e:
                logging.error(f"Exception raised while processing command: {e}")
                break
        else:
            logging.info("No valid input received.")
except KeyboardInterrupt:
    logging.info("KeyboardInterrupt received, shutting down.")
finally:
    # Graceful shutdown for TTS thread
    tts_queue.put(None)
    tts_thread.join()

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
from os.path import isfile, join
import smtplib
import wikipedia
import Gesture_Controller
#import Gesture_Controller_Gloved as Gesture_Controller
import app
from queue import Queue
from threading import Thread


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
            print(f"TTS error: {e}")
        tts_queue.task_done()

tts_thread = Thread(target=tts_worker, daemon=True)
tts_thread.start()

# ----------------Variables------------------------
file_exp_status = False
files =[]
path = ''
is_awake = True  #Bot status

# ------------------Functions----------------------
def reply(audio):
    print(audio)
    tts_queue.put(audio)
    # Ensure chat message is always updated after TTS is queued
    app.ChatBot.addAppMsg(audio)


def wish():
    hour = int(datetime.datetime.now().hour)

    if hour>=0 and hour<12:
        reply("Good Morning!")
    elif hour>=12 and hour<18:
        reply("Good Afternoon!")   
    else:
        reply("Good Evening!")  
        
    reply("I am Proton, how may I help you?")

# Set Microphone parameters
with sr.Microphone() as source:
        r.energy_threshold = 500 
        r.dynamic_energy_threshold = False

# Audio to String
def record_audio():
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        voice_data = ''
        audio = r.listen(source, phrase_time_limit=5)

        try:
            voice_data = r.recognize_google(audio)
        except sr.RequestError:
            reply('Sorry my Service is down. Plz check your Internet connection')
        except sr.UnknownValueError:
            print('cant recognize')
            pass
        return voice_data.lower()


# Executes Commands (input: string)
def respond(voice_data):
    global file_exp_status, files, is_awake, path

    print(voice_data)
    # Remove 'proton' from the command for easier matching
    voice_data = voice_data.replace('proton', '').strip()
    app.eel.addUserMsg(voice_data)

    if is_awake == False:
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
        except:
            reply('Please check your Internet')
        return

    if 'location' in voice_data:
        reply('Which place are you looking for ?')
        temp_audio = record_audio()
        app.eel.addUserMsg(temp_audio)
        reply('Locating...')
        url = 'https://google.nl/maps/place/' + temp_audio + '/&amp;'
        try:
            webbrowser.get().open(url)
            reply('This is what I found Sir')
        except:
            reply('Please check your Internet')
        return

    if ('bye' in voice_data) or ('by' in voice_data):
        reply("Good bye Sir! Have a nice day.")
        is_awake = False
        return

    if ('exit' in voice_data) or ('terminate' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        app.ChatBot.close()
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

    # File Navigation (Default Folder set to C://)
    if 'list' in voice_data:
        counter = 0
        path = 'C://'
        files = listdir(path)
        filestr = ""
        for f in files:
            counter += 1
            print(str(counter) + ':  ' + f)
            filestr += str(counter) + ':  ' + f + '<br>'
        file_exp_status = True
        reply('These are the files in your root directory')
        app.ChatBot.addAppMsg(filestr)
        return

    if file_exp_status == True:
        counter = 0
        if 'open' in voice_data:
            try:
                idx = int(voice_data.split(' ')[-1]) - 1
                if isfile(join(path, files[idx])):
                    os.startfile(path + files[idx])
                    file_exp_status = False
                else:
                    path = path + files[idx] + '//'
                    files = listdir(path)
                    filestr = ""
                    for f in files:
                        counter += 1
                        filestr += str(counter) + ':  ' + f + '<br>'
                        print(str(counter) + ':  ' + f)
                    reply('Opened Successfully')
                    app.ChatBot.addAppMsg(filestr)
            except:
                reply('You do not have permission to access this folder')
            return
        if 'back' in voice_data:
            filestr = ""
            if path == 'C://':
                reply('Sorry, this is the root directory')
            else:
                a = path.split('//')[:-2]
                path = '//'.join(a)
                path += '//'
                files = listdir(path)
                for f in files:
                    counter += 1
                    filestr += str(counter) + ':  ' + f + '<br>'
                    print(str(counter) + ':  ' + f)
                reply('ok')
                app.ChatBot.addAppMsg(filestr)
            return

    # If no command matched
    reply('I am not functioned to do this !')

# ------------------Driver Code--------------------

t1 = Thread(target = app.ChatBot.start)
t1.start()

# Lock main thread until Chatbot has started
while not app.ChatBot.started:
    time.sleep(0.5)

wish()
voice_data = None
while True:
    if app.ChatBot.isUserInput():
        # take input from GUI
        voice_data = app.ChatBot.popUserInput()
        print(f"GUI input: {voice_data}")
    else:
        # take input from Voice
        voice_data = record_audio()
        print(f"Voice input: {voice_data}")

    # process voice_data
    if voice_data and voice_data.strip():
        try:
            respond(voice_data)
        except SystemExit:
            reply("Exit Successfull")
            break
        except Exception as e:
            print(f"EXCEPTION raised while closing: {e}")
            break
    else:
        print("No valid input received.")

# Graceful shutdown for TTS thread
tts_queue.put(None)
tts_thread.join()
        



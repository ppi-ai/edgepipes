import pyttsx3
import os

def play(text):
    engine = pyttsx3.init()
    #engine.setProperty('rate', 150)
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[10].id)
    
    engine.say(text)
    engine.runAndWait()
    engine.stop()
    return

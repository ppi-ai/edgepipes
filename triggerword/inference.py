import sounddevice as sd
import numpy as np
import scipy.signal
import timeit
import python_speech_features
import sys
from python_speech_features import mfcc
from python_speech_features import delta
from tflite_runtime.interpreter import Interpreter

model_path = './models/tr_model.tflite'
debug_time = 1
debug_acc = 0
word_threshold = 0.7
rec_duration =  2.56
sample_rate = 16000
resample_rate = 16000
num_channels = 1
num_mfcc = 20
eps = sys.float_info.epsilon
# Sliding window
window = np.zeros(int(rec_duration * resample_rate) * 2)


# Load model (interpreter)
interpreter = Interpreter(model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def normalize(x, axis=0):
    mean = x.mean(axis=axis)
    std = x.std(axis=axis) + eps
    return (x-mean)/std

# This gets called every 0.5 seconds
def sd_callback(rec, frames, time, status):
    # Start timing for testing
    start = timeit.default_timer()

    # Notify if errors
    if status:
        print('Error:', status)
    # Remove 2nd dimension from recording sample
    rec = np.squeeze(rec)
    print(rec.shape)
    new_fs = sample_rate
    # Save recording onto sliding window
    window[:len(window)//2] = window[len(window)//2:]
    window[len(window)//2:] = rec
    # Compute features
    mfccs = mfcc(window, 
                 samplerate=new_fs,
                 winlen=0.01,
                 winstep=0.01,
                 numcep=num_mfcc,
                 nfilt=40,
                 nfft=480,
                 appendEnergy=True)
                     
    
    mfccs = normalize(mfccs, axis=0)
    deltas = delta(mfccs, 2)
    combined = np.hstack((mfccs, deltas))
    # Make prediction from model
    in_tensor = np.float32(combined.reshape(1, combined.shape[0], combined.shape[1]))
    interpreter.set_tensor(input_details[0]['index'], in_tensor)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    val = output_data[0][0]
    if val > word_threshold:
        print('stop {}'.format(val))
    if debug_acc:
        print('print val {}'.format(val))
    if debug_time:
        print('debug Time {} val {}'.format(timeit.default_timer() - start, val))
            
# Start streaming from microphone
with sd.InputStream(channels=num_channels,
                    samplerate=sample_rate,
                    blocksize=int(sample_rate * rec_duration),
                    callback=sd_callback):
    while True:
        pass

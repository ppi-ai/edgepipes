import numpy as np
import sys
from python_speech_features import mfcc
from python_speech_features import delta
from tflite_runtime.interpreter import Interpreter

class TriggerModel():
    def __init__(self,  
                 word_threshold = 0.7,
                 rec_duration = 2.56,
                 num_mfcc = 20,
                 sample_rate = 16000, 
                 resample_rate = 16000):
        
     
        self.word_threshold  = word_threshold
        self.rec_duration = rec_duration
        self.num_mfcc = num_mfcc
        self.sample_rate = sample_rate
        self.resample_rate = resample_rate
        self.model_path = 'triggerword/models/tr_model.tflite'
        
        self.model = self._build_model()
        self.buffer_size = int(self.rec_duration*self.sample_rate) * 2
        self.buffer = []
        
    def _build_model(self):
        interpreter = Interpreter(self.model_path)
        interpreter.allocate_tensors()
        return interpreter
        
        
    @staticmethod
    def _normalize(x, axis=0):
        eps = sys.float_info.epsilon
        mean = x.mean(axis=axis)
        std = x.std(axis=axis) + eps
        return (x-mean)/std
    
    def _addToBuffer(self, x):
        for d in x:
            self.buffer.append(d)
    
    def _slideBuffer(self):
        self.buffer = self.buffer[self.buffer_size//2:]
               
    def detect(self, x):
    
        if len(self.buffer) < self.buffer_size:
            self._addToBuffer(x)
        else:
           
            rec = np.array(self.buffer[: self.buffer_size])

            self._slideBuffer()
            self._addToBuffer(x)
            
            new_fs = self.sample_rate
            
            # Compute features
            mfccs = mfcc(rec, 
                         samplerate=new_fs,
                         winlen=0.01,
                         winstep=0.01,
                         numcep=self.num_mfcc,
                         nfilt=40,
                         nfft=480,
                         appendEnergy=True)                 

            mfccs = TriggerModel._normalize(mfccs, axis=0)
            deltas = delta(mfccs, 2)
            combined = np.hstack((mfccs, deltas))
            
            # Make prediction from model
            in_tensor = np.float32(combined.reshape(1, combined.shape[0], combined.shape[1]))
            input_details = self.model.get_input_details()
            output_details =self.model.get_output_details()    
                
            self.model.set_tensor(input_details[0]['index'], in_tensor)
            self.model.invoke()
            
            output_data = self.model.get_tensor(output_details[0]['index'])
            
            val = output_data[0][0]
            print(val)
            if val > self.word_threshold:
                return True
            else:
                return False

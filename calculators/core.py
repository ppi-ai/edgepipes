#
# Data pipelines for Edge Computing
#
# Inspired by Google Media pipelines
#
#
# Dataflow can be within a "process" and then hook in locally
# But can also be via a "bus" or other communication mechanism
# 

class TextData:
    def __init__(self, text, timestamp):
        self.text = text
        self.timestamp = timestamp


class Calculator:
    def __init__(self, name, streams, options=None):
        self.name = name
        # input names
        self.input = [name + '-in']
        self.input_data = [None]
        # output names
        self.output = [name + '-out']
        self.output_data = [None]
        self.lastStep = False
        self.streams = streams
        self.options = options

    # called to trigger a calculation of inputs => output
    def process_node(self):
        self.lastStep = self.process()
        return self.lastStep

    def get_output_index(self, name):
        return self.output.index(name)

    def get_input_index(self, name):
        return self.input.index(name)

    def set_input(self, index, input_data):
        self.input_data[index] = input_data
    
    def get_output(self, index):
        return self.output_data[index]

    def set_output(self, index, data):
        if self.output[index] not in self.streams:
            print(f"  - No subscriber of {self.name}...")
        else:
            # Set this in all "subscribers"
            subs = self.streams[self.output[index]]
            for sub in subs:
                # 0 => node, 1 => index
                sub[0].set_input(sub[1], data)
        # the cache
        self.output_data[index] = data

    def set_input_names(self, inputs):
        self.input = inputs
        self.input_data = [None] * len(inputs)
    
    def set_output_names(self, outputs):
        self.output = outputs
        self.output_data = [None] * len(outputs)

    # Get out data and "clear".
    def get(self, index):
        val = self.input_data[index]
        self.input_data[index] = None
        return val

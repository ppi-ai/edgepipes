#!/usr/bin/env python3
#
import argparse
import os
import sys
import threading
import edgepipes
from calculators.core import SwitchNode
from cmd import Cmd
import networkx as nx
import matplotlib.pyplot as plt


def plot(g, labels):
    print("Plotting... Thread:", threading.get_ident())
    plt.subplot(121)
    pos=nx.spring_layout(g)
    nx.draw(g, pos, with_labels=True, font_weight='bold')
    nx.draw_networkx_edge_labels(g ,pos,edge_labels=labels,font_size=10)
    plt.show()


class PipeCli(Cmd):
    prompt = 'pipecli> '

    def __init__(self, completekey='tab', stdin=None, stdout=None):
        Cmd.__init__(self, completekey=completekey, stdin=stdin, stdout=stdout)
        self.pipeline = edgepipes.Pipeline()
        self.ctr = 1
        self.options = {}

    def do_exit(self, inp):
        """exit the application."""
        print("Bye")
        self.pipeline.exit()
        return True

    def do_setvideo(self, inp):
        """set the current (default) video stream input. (setvideo <source>)"""
        print("Set video input '{}'".format(inp))
        self.options['input_video'] = {'video': inp}

    def do_setaudio(self, inp):
        """set the current (default) audio stream input. (setaudio <source>)"""
        print("Set audio input '{}'".format(inp))
        self.options['input_audio'] = {'audio': inp}

    def do_togglestate(self, inp):
        nodes = self.pipeline.get_nodes_by_type(SwitchNode)
        if nodes:
            for n in nodes:
                n.toggle_state()
                print(f"Toggled state in {n.name} => {n.switch_state}")
        else:
            print("Found no switch nodes to toggle")

    def do_print(self, inp):
        for n in self.pipeline.pipeline:
            print("N:", n.name)
            print("  Time consumed:", self.pipeline.elapsed[n.name], self.pipeline.elapsed[n.name] / self.pipeline.count[n.name] )
            print("  input :", n.input)
            print("  output:", n.output)
        print("Done...")

    def do_plot(self, inp):
        g = nx.Graph()
        labels = dict()
        for n in self.pipeline.pipeline:
            g.add_node(n.name)
            # Add input edges
            for ni in n.input:
                nodes = self.pipeline.get_node_by_output(ni)
                if len(nodes) > 0:
                    g.add_edge(n.name, nodes[0].name)
                    labels[(n.name,nodes[0].name)] = ni
        self.pipeline.scheduler.enter(1, 1, plot, argument=(g,labels,))

    def emptyline(self):
        return

    def do_load(self, inp):
        if len(inp) == 0:
            files = [f for f in os.listdir("graphs")]
            print("Available pipelines (in graphs):")
            for file in files:
                print(file)
        else:
            print("Loading pipeline from ", inp)
            try:
                f = open(inp, "r")
            except:
                try:
                    f = open("graphs/" + inp, "r")
                except:
                    print("File not found:", inp)
                    return
            txt = f.read()
            f.close()
            print("Load graphs: '{}'".format(txt))
            self.pipeline.setup_pipeline(txt, prefix=str(self.ctr) + "/", options=self.options)
            self.ctr += 1

    def do_start(self, inp):
        if not self.pipeline.run_pipeline:
            self.pipeline.start()

    def do_stop(self, inp):
        self.pipeline.stop()

    def do_step(self, inp):
        self.pipeline.step()


if __name__ == "__main__":
    try:
        args = sys.argv[1:]
        p = argparse.ArgumentParser()
        p.add_argument('--input', dest='input_video', default=None, help='video stream input')
        p.add_argument('--input_audio', dest='input_audio', default=None, help='audio stream input')
        p.add_argument('pipeline', nargs='?')
        conopts = p.parse_args(args)
    except Exception as e:
        sys.exit(f"Illegal arguments: {e}")

    pipeline_graph = None
    if conopts.pipeline:
        print(f"Loading pipeline from {conopts.pipeline}")
        try:
            with open(conopts.pipeline, "r") as f:
                pipeline_graph = f.read()
        except FileNotFoundError:
            sys.exit(f"Could not find the pipeline config file {conopts.pipeline}")

    # Setup the CLI and start a separate thread for that - as main is needed for the CV processing.
    p = PipeCli()

    opts = {}
    if conopts.input_video:
        video = int(conopts.input_video) if conopts.input_video.isnumeric() else conopts.input_video
        opts['input_video'] = {'video': video}
    if conopts.input_audio:
        audio = int(conopts.input_audio) if conopts.input_audio.isnumeric() else conopts.input_audio
        opts['input_audio'] = {'audio': audio}
    p.options = opts

    if pipeline_graph:
        p.pipeline.setup_pipeline(pipeline_graph, options=opts)
        p.pipeline.start()
    thread = threading.Thread(target=p.cmdloop)
    thread.start()
    p.pipeline.run()
    thread.join()

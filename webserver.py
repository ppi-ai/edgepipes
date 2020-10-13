from flask import Flask
import networkx as nx
from networkx.readwrite import json_graph
import base64, json
import cv2
import calculators.image

app = Flask(__name__,  static_url_path='/force/', static_folder='force')
pipeline = None

@app.route('/data/<name>')
def data(name):
    nodes = pipeline.get_node_by_output(name)
    if len(nodes) == 0:
        return "can not find stream data: " + name
    else:
        d = nodes[0]
        index = d.get_output_index(name)
        out = d.get_output(index)
        if isinstance(out, calculators.image.ImageData):
            img =  b'data:image/jpeg;base64,' + base64.encodebytes(cv2.imencode('.jpeg',  out.image)[1].tostring())
            val = "Image:<img src=\"" + img.decode('ascii') + "\"/>";
        else:
            val = str(out)
        return val;

@app.route('/')
def hello():
    data = "<ul>"
    for n in pipeline.pipeline:
        data += "<li>Node:" +  n.name + "<ul>"
        data += '<li>input :' + str(n.input)
        data += '<li>output:'
        for out in n.output:
            data += '<a href="/data/' + str(out) + '">' + str(out) + '</a>'
        data += '</ul>'
    return "EdgePipes - pipeline." + data + "</ul>"

@app.route('/graph.json')
def graph():
    g = nx.DiGraph()
    labels = dict()
    for n in pipeline.pipeline:
        g.add_node(n.name)
        # Add input edges
        for ni in n.input:
            nodes = pipeline.get_node_by_output(ni)
            if len(nodes) > 0:
                g.add_edge(n.name, nodes[0].name)
                labels[(n.name, nodes[0].name)] = ni
    #return json.dumps(json_graph.cytoscape_data(g))
    return json.dumps(json_graph.node_link_data(g))

@app.route("/force/")
def static_proxy():
    return app.send_static_file("force.html")

# This will run the web-server
def run(pipes):
    global pipeline
    pipeline = pipes
    app.run()
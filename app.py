from flask import Flask, render_template, request, jsonify, abort
import cf_deployment_tracker
import os
import json
import requests

import tensorflow as tf

# Emit Bluemix deployment event
cf_deployment_tracker.track()

app = Flask(__name__)
BASE = './assets/'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# If you are using a Mobilenet, the following should be uncommented.

INPUT_LAYER = 'input'
INPUT_HEIGHT = 224
INPUT_WIDTH = 224

# If you are using Inception v3, the following should be uncommented.
"""
INPUT_LAYER = 'Mul'
INPUT_HEIGHT = 299
INPUT_WIDTH = 299
"""

# Load labels.
LABEL_LIST = [line.rstrip() for line
              in tf.gfile.GFile(BASE + "retrained_labels.txt")]

# Load graph from file.
GRAPH = tf.Graph()
with tf.gfile.FastGFile(BASE + "retrained_graph.pb", 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    with GRAPH.as_default():
        _ = tf.import_graph_def(graph_def, name='')
sess = tf.Session(graph=GRAPH)

# On Bluemix, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/classify', methods=['POST'])
def upload_image():
    # If a URL was given.
    if request.json:
        # TODO validation.
        print(request.json['url'])
        # Spoof User-Agent as some websites don't like non-browser requests.
        headers = {'User-Agent':
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/64.0.3282.140 Safari/537.36'}
        resp = requests.get(request.json['url'], headers=headers)
        if resp.status_code == 200:
            scores = run_model(resp.content)
            return jsonify(scores)
        else:
            abort(400, 'Server could not access image at given url.')
    elif request.files:
        if 'file' not in request.files:
            abort(400, '"file" key not in part.')
        file = request.files['file']
        if not file.filename:
            abort(400, 'No selected file.')
        if file and allowed_file(file.filename):
            image_data = file.read()
            scores = run_model(image_data)
            return jsonify(scores)
    else:
        abort(400)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def adjust_image(image_contents, input_height=299, input_width=299,
                 input_mean=128, input_std=128):
    """Adapted from /tensorflow/examples/label_image/label_image.py"""
    image_reader = tf.image.decode_image(image_contents, channels=3)
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    with tf.Session() as ses:
        result = ses.run(normalized)
    return result


def run_model(image_data):
    scores = []

    input_operation = sess.graph.get_operation_by_name(INPUT_LAYER)
    output_operation = sess.graph.get_operation_by_name("final_result")

    t = adjust_image(image_data, input_height=INPUT_HEIGHT,
                     input_width=INPUT_WIDTH)

    predictions = sess.run(output_operation.outputs[0], {
        input_operation.outputs[0]: t
    })

    # Sort to show labels of predictions by confidence
    sorted_nodes = predictions[0].argsort()[-len(predictions[0]):][::-1]
    for node in sorted_nodes:
        label = LABEL_LIST[node]
        score = predictions[0][node]
        scores.append({label: float('%.5f' % score)})
    return scores


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)

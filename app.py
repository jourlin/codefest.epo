from flask import Flask, Response, render_template, stream_template,send_from_directory
from markupsafe import escape

import time
import click
import warnings
import os
from toolkit import Toolkit

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    app.logger.info("Path: "+os.path.join(app.root_path, 'static'))
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/answer')
def generate_answer():
    def update(tokens):
        toogle_bold=True
        yield 'data: open\n\n'
        for token in tokens:
            token=str(token).replace("\n","<br>")
            yield f'data: {token}\n\n'
        yield 'data: close\n\n'

    app.logger.info("In generation")
    tokens=Toolkit(read_only=True).patchat("What types of patented dental devices do you know?").response_gen
    return Response(update(tokens), mimetype='text/event-stream')

@app.route('/')
def index():
    # warnings.filterwarnings('ignore')
    return stream_template('index.html')

@app.cli.command("textchat")
def textchat():
    t = Toolkit()
    while True:
        print("How can I help ? (type 'bye' to quit.)")
        question = input("> ")
        print()
        if question == "bye":
            print("Bye. Looking forward talking with you again !")
            break
        streaming_response = t.patchat(question)
        print()
        for tokens in streaming_response.response_gen:
            print(str(tokens),end='', flush=True)
        print()
        print()

@app.cli.command("reindex")
def reindex():
    """Regenerate the Deeplake store."""
    t=Toolkit()
    t.reindex()

if __name__ == '__main__':
    app.run(debug=True, threaded=True)

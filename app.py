from flask import Flask, Response, render_template, stream_template,send_from_directory, request
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

@app.route('/answer', methods = ['POST', 'GET'])
def generate_answer():
    def render(token, is_start=True):
        rendered=str(token).replace('\n', '<br/>')
        return rendered
    
    def update(tokens):
        yield 'data: open\n\n'
        for token in tokens:
            yield f'data: {render(token)}\n\n'
        yield 'data: close\n\n'

    if request.method == 'POST':
      query = request.form['query']
    else:
      query = request.args.get('query')
    app.logger.info(f"Answering: '{query}'")
    t = Toolkit(read_only=True)

    search_results = t.retrieve(query)
    for offset in range(0, len(search_results['score'])):
        print(search_results['metadata'][offset]['file_path'])

    tokens=t.patchat(query).response_gen
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

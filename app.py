from flask import Flask, Response, render_template, stream_template,send_from_directory, request
from markupsafe import escape

import time
import click
import warnings
import os

from toolkit import Toolkit

toolkit = Toolkit(read_only=True)

app = Flask(__name__)

# Render the main web page
@app.route('/')
def index():
    return stream_template('index.html')

# Download PDF version of patent
@app.route("/download/<filename>")
def download(filename):
    workingdir = os.path.abspath(os.getcwd())
    filepath = workingdir + '/documents/'
    print(filepath, filename)
    return send_from_directory(filepath, filename)

# Don't want any 404 error code
@app.route('/favicon.ico')
def favicon():
    app.logger.info("Path: "+os.path.join(app.root_path, 'static'))
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico',mimetype='image/vnd.microsoft.icon')

# Search for patents
@app.route('/search', methods = ['POST', 'GET'])
def search():
    if request.method == 'POST':
      query = request.form['query']
    else:
      query = request.args.get('query')
    search_results = toolkit.retrieve(query)
    return Response(search_results, mimetype='text/html')

# Search for UMLS concepts
@app.route('/extend', methods = ['POST', 'GET'])
def extend():
    if request.method == 'POST':
      query = request.form['query']
    else:
      query = request.args.get('query')
    search_results = toolkit.extend(query)
    return Response(search_results, mimetype='text/html')

# Chatbot answering user's input
@app.route('/answer', methods = ['POST', 'GET'])
def generate_answer():
    # Web browser needs <br> instead of line feed character
    def render(token, is_start=True):
        rendered=str(token).replace('\n', '<br/>')
        return rendered
    # Send tokens as they arrive from Llama3
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
    # Start the chatbot engine and get the token stream
    tokens=toolkit.patchat(query).response_gen
    # The token stream is returned via update() to the Javascript EventSource 
    # object, answer_source, defined in template/index.html
    return Response(update(tokens), mimetype='text/event-stream')

# Type flask textchat in your terminal for a simple chatbot in console mode 
@app.cli.command("textchat")
def textchat():
    while True:
        print("How can I help ? (type 'bye' to quit.)")
        question = input("> ")
        print()
        if question == "bye":
            print("Bye. Looking forward talking with you again !")
            break
        streaming_response = toolkit.patchat(question)
        print()
        for tokens in streaming_response.response_gen:
            print(str(tokens),end='', flush=True)
        print()
        print()

# Type flask reindex <name> for (re)indexing data
# use BOTH for <name> for both UMLS and patent data
# use UMLS for UMLS concept or EP for patents
@app.cli.command("reindex")
@click.argument("index_name")
def reindex(index_name):
    """Regenerate the Deeplake store."""
    global toolkit 
    # Need to write the index
    app.logger.info("Reopening indexes in write mode...")
    toolkit=Toolkit(read_only=False, index_name=index_name)
    toolkit.reindex(index_name)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=False, threaded=True)

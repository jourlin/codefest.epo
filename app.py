from flask import Flask, render_template
import click
from toolkit import Toolkit

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.cli.command("reindex")
@click.argument("index_name")
def reindex(index_name):
    """Regenerate the Deeplake store."""
    t=Toolkit(index_name)
    t.reindex()

    
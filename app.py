from flask import Flask, render_template
import click
import warnings
import os
from toolkit import Toolkit

from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.deeplake import DeepLakeVectorStore

app = Flask(__name__)

@app.route('/')
def index():
    # warnings.filterwarnings('ignore')
    t=Toolkit()
    # embedding model
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=t.model_name
    )
    # ollama
    Settings.llm = Ollama(model=t.llm, request_timeout=t.llm_req_timeout)
    app.logger.info('Loading index from "'+t.vector_dir+"'")
    vector_store = DeepLakeVectorStore(dataset_path=t.vector_dir)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, streaming=True)
    app.logger.info('task completed.')
    memory = ChatMemoryBuffer.from_defaults(token_limit=t.token_limit)
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        memory=memory,
        system_prompt=(
            "You are a chatbot, able to have normal interactions, as well as talk"
            " about patents. Do not invent patent numbers"
        ),
    )
    question = "What are the main kinds of patented devices for healthcare?"
    streaming_response = chat_engine.stream_chat(question)
    for tokens in streaming_response.response_gen:
        app.logger.info(str(tokens))
    return render_template('index.html')

@app.cli.command("textchat")
def textchat():
    # warnings.filterwarnings('ignore')
    t=Toolkit()
    # embedding model
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=t.model_name
    )
    # ollama
    Settings.llm = Ollama(model=t.llm, request_timeout=t.llm_req_timeout)
    print('Loading index from "'+t.vector_dir+"'")
    vector_store = DeepLakeVectorStore(dataset_path=t.vector_dir)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, streaming=True)
    print('task completed.')
    memory = ChatMemoryBuffer.from_defaults(token_limit=t.token_limit)
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        memory=memory,
        system_prompt=(
            "You are a chatbot, able to have normal interactions, as well as talk"
            " about patents. Do not make up patent numbers."
        ),
    )
    while True:
        print("How can I help ? (type 'bye' to quit.)")
        question = input("> ")
        print()
        if question == "bye":
            print("Bye. Looking forward talking with you again !")
            break
        streaming_response = chat_engine.stream_chat(question)
        print()
        for tokens in streaming_response.response_gen:
            print(str(tokens),end='', flush=True)
        print()
        print()
@app.cli.command("reindex")
@click.argument("index_name")
def reindex(index_name):
    """Regenerate the Deeplake store."""
    t=Toolkit(index_name)
    t.reindex()

    
import os 
from bs4 import BeautifulSoup
from tqdm import tqdm
import deeplake

from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.deeplake import DeepLakeVectorStore
from llama_index.core.memory import ChatMemoryBuffer

class Toolkit:
    
    def __init__(self, read_only=False):
        self.query=os.getenv('SEARCH_TERM')
        self.model_name=os.getenv('MODEL_NAME')
        self.match_all=os.getenv('MATCH_ALL')
        self.ignore_case=os.getenv('IGNORE_CASE')
        self.epab_size=os.getenv('EPAB_SIZE')
        self.doc_limit=int(os.getenv('DOC_LIMIT'))
        self.llm=os.getenv('LLM')
        self.llm_req_timeout=float(os.getenv('LLM_REQ_TIMEOUT'))
        self.token_limit=int(os.getenv('TOKEN_LIMIT'))
        self.document_dir=os.getenv('DOC_DIR')
        self.vector_dir=os.getenv('VEC_DIR')
        self.tmp_dir=os.getenv('TMP_DIR')
        # embedding model
        self.embed_model = HuggingFaceEmbedding(
            model_name=self.model_name
        )
        Settings.embed_model = self.embed_model
        # ollama
        self.llm_settings = Ollama(model=self.llm, request_timeout=self.llm_req_timeout)
        Settings.llm = self.llm_settings
        self.vector_store = DeepLakeVectorStore(dataset_path=self.vector_dir)
        self.index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store, streaming=True, read_only=read_only)
        self.memory = ChatMemoryBuffer.from_defaults(token_limit=self.token_limit)
        self.chat_engine = self.index.as_chat_engine(
            chat_mode="context",
            memory=self.memory,
            system_prompt=(
                "You are a chatbot, able to have normal interactions, as well as talk"
                " about patents. Do not invent patent numbers."
            ),
        )
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        os.system("mkdir -p "+self.document_dir)
        os.system("mkdir -p "+self.vector_dir)

    def retrieve(self, query):
        store = deeplake.core.vectorstore.deeplake_vectorstore.DeepLakeVectorStore(path=self.vector_dir)
        result=store.search(embedding_data=query, embedding_function=self.embed_model.get_text_embedding)
        return result

    def reindex(self):
        print(f"Reindexing '{self.query}'...")
        file_list = os.popen("grep -i -l '"+self.query+"' "+self.document_dir+"/*.xml").read()
        file_list = file_list.splitlines()
        print(f"Found {len(file_list)} publications containing the following term: '{self.query}'")
        nb_docs = min(self.doc_limit, len(file_list))
        print(f"Storing {nb_docs} patents embeddings to disk...")
        os.system("rm -fr "+self.tmp_dir)
        os.system("mkdir -p "+self.tmp_dir)
        for fn in tqdm(file_list):
            if len(fn)>0:
                os.system("cp "+fn+" "+self.tmp_dir)
        # Load documents and build index
        documents = SimpleDirectoryReader(self.tmp_dir).load_data()
        # embedding model
        Settings.embed_model = self.embed_model
        # ollama
        Settings.llm = self.llm_settings
        print("Indexing patents can take some time...")
        index = VectorStoreIndex.from_documents(
            documents, show_progress=True, storage_context=self.storage_context
        )
        print("Indexing patents completed...")

    def patchat(self, question):
        streaming_response = self.chat_engine.stream_chat(question)
        return streaming_response


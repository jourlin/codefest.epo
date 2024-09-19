import os 
import sys
import lxml.etree as ET
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
        self.umls_document_dir=os.getenv('UMLS_DOC_DIR')
        self.umls_vector_dir=os.getenv('UMLS_VEC_DIR')
        self.tmp_dir=os.getenv('TMP_DIR')
        self.table_cells_maxchars=int(os.getenv('TABLE_CELLS_MAXCHARS'))
        self.span_top_k = 20 # Number of passages to be retrieved in DeepLake store
        # embedding model
        self.embed_model = HuggingFaceEmbedding(
            model_name=self.model_name
        )
        Settings.embed_model = self.embed_model
        # ollama
        self.llm_settings = Ollama(model=self.llm, request_timeout=self.llm_req_timeout)
        Settings.llm = self.llm_settings
        self.umls_vector_store = DeepLakeVectorStore(dataset_path=self.umls_vector_dir)
        self.umls_index = VectorStoreIndex.from_vector_store(vector_store=self.umls_vector_store, streaming=True, read_only=read_only)
        self.umls_storage_context = StorageContext.from_defaults(vector_store=self.umls_vector_store)
        
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
        result = store.search(embedding_data=query, embedding_function=self.embed_model.get_text_embedding, k=self.span_top_k)
        docname_list = {result['metadata'][offset]['file_path'] for offset in range(0, len(result['metadata']))} 
        result="<table><tr><th>ID</th><th>Published</th><th>Classification CPC</th><th>Short Desc.</th></tr>\n"
        for doc in docname_list:
            try:
                root=ET.parse(doc).getroot()
            except:
                continue
            id=root.xpath('//ep-patent-document')[0].get('id')
            date=root.xpath('//ep-patent-document')[0].get('date-publ')
            year=date[:4]
            month=date[4:6]
            day=date[6:8]
            date = day+'/'+month+"/"+year
            category=root.xpath('//B540/B542/text()')[1]
            short=root.xpath('//description/heading[text()="SUMMARY"]')
            if len(short)>0:
                short=short[0].getnext().xpath('text()')[0][:self.table_cells_maxchars]+'<a href="/download/'+os.path.basename(doc).strip(".xml")+".pdf"+'">[...]</a>'
            else:
                short="..."    
            result+=f"<tr><td>{id}</td><td>{date}</td><td>{category}</td><td>{short}</td></tr>\n"
        result+="</table>\n"
        return result

    def extend(self, query):
        store = deeplake.core.vectorstore.deeplake_vectorstore.DeepLakeVectorStore(path=self.umls_vector_dir)
        result = store.search(embedding_data=query, embedding_function=self.embed_model.get_text_embedding, k=self.span_top_k)
        result="<table><tr><th>ID</th><th>synonyms</th></tr>\n"
        result+="</table>\n"
        return result

    def reindex(self, index_name):
        if index_name == "EP":
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
            self.index = VectorStoreIndex.from_documents(
                documents, show_progress=True, storage_context=self.storage_context
            )
            print("Indexing patents completed...")
        elif index_name == "UMLS":
            print(f"Reindexing '{self.query}'...")
            os.system("mkdir -p "+self.umls_vector_dir)
            # Load documents and build index
            concepts = SimpleDirectoryReader(self.umls_document_dir).load_data()
            # embedding model
            Settings.embed_model = self.embed_model
            # ollama
            Settings.llm = self.llm_settings
            print("Indexing umls concepts can take some time...")
            self.umls_index = VectorStoreIndex.from_documents(
                concepts, show_progress=True, storage_context=self.umls_storage_context
            )
            print("Indexing umls concepts completed...")
        else:
            print("Error : Invalid index name. Choose 'EP' for patents or 'UMLS' for concepts", file=sys.stderr)

    def patchat(self, question):
        streaming_response = self.chat_engine.stream_chat(question)
        return streaming_response


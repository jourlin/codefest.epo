import os 
import sys
import re
from tqdm import tqdm
from markdown import markdown

import deeplake
import lxml.etree as ET
from html2text import html2text
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage
from llama_index.vector_stores.deeplake import DeepLakeVectorStore
from llama_index.core.memory import ChatMemoryBuffer

# pattern for matching UMLS IDs
concept_pattern = re.compile("^c[0-9]+$")
ai_generated_prompts = {
    "strengths" : ["Major strengths", "Top 5 major strengths of the following invention. Answer in less than 50 words: "]
}

class Toolkit:
    """ Toolkit is the main structure for handling HF embeddings, Ollama, Deeplake & LlamaIndex"""
    def __init__(self, read_only=False, index_name="BOTH"):
        # import all configuration values from .env file
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
        self.span_top_k = int(os.getenv('SPAN_TOPK'))
        print("Initializing toolkit...",file=sys.stderr)
        self.embed_model = HuggingFaceEmbedding(
            model_name=self.model_name
        )
        Settings.embed_model = self.embed_model
        # ollama
        self.llm_settings = Ollama(model=self.llm, request_timeout=self.llm_req_timeout)
        Settings.llm = self.llm_settings
        accepted_names = ["UMLS", "EP", "BOTH"]
        if index_name not in accepted_names:
            print(f"Error: '{index_name}' is not a valid index name. Accepted values : {accepted_names}", file=sys.stderr)
            sys.exit(-1)
        if index_name=="UMLS" or index_name=="BOTH":
            # Configure deeplake for UMLS
            self.umls_vector_store = DeepLakeVectorStore(dataset_path=self.umls_vector_dir)
            self.umls_index = VectorStoreIndex.from_vector_store(vector_store=self.umls_vector_store, streaming=True, read_only=read_only)
            self.umls_storage_context = StorageContext.from_defaults(vector_store=self.umls_vector_store)
        if index_name=="EP" or index_name=="BOTH": 
            # Configure deeplake for patents
            self.vector_store = DeepLakeVectorStore(dataset_path=self.vector_dir)
            self.index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store, streaming=True, read_only=read_only)
            self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            self.memory = ChatMemoryBuffer.from_defaults(token_limit=self.token_limit)
            # Here is the prompt :
            self.chat_engine = self.index.as_chat_engine(
            chat_mode="context",
            memory=self.memory,
            system_prompt=(
                "You are a chatbot, able to have normal interactions, as well as talk"
                " about patents. Do not invent patent numbers."
            ),
        )
        # If needed, makes data directories
        os.system("mkdir -p "+self.document_dir)
        os.system("mkdir -p "+self.vector_dir)
        os.system("mkdir -p "+self.umls_document_dir)
        os.system("mkdir -p "+self.umls_vector_dir)
        print("Initialization completed...",file=sys.stderr)

    def get_ai_generated_field(self,text, field):
        """ Extract a brief description of major strengths of the invention """
        llm = Ollama(model=self.llm)
        messages=[
            ChatMessage(role="assistant", content="You are an assistant, do what the user tells you to do properly."),
            ChatMessage(role="user", content=ai_generated_prompts[field][1]+text)
        ]
        resp = llm.chat(messages)
        content = None
        for item in resp:
            if isinstance(item, tuple) and item[0] == 'message':
                content = item[1].content
                break
        return content
    
    def retrieve(self, query, query_is_file=False):
        """ Retrieve patents by performing a K Nearest Neighbours, based on query and patents embeddings """
        if not query_is_file:
            # First expand all UMLS concepts contained in the query
            query = self.expand_query(query)
        
        # LLama Index does not provide the search() method for its embedded Deeplake stores, so : 
        store = deeplake.core.vectorstore.deeplake_vectorstore.DeepLakeVectorStore(path=self.vector_dir)
        result = store.search(embedding_data=query, embedding_function=self.embed_model.get_text_embedding, k=self.span_top_k)
        # Get retrieved filenames from Deeplake results
        docname_list ={result['metadata'][offset]['file_path'] for offset in range(0, len(result['metadata']))}
        #strengths_list = [result['metadata'][offset]['strengths'] for offset in range(0, len(result['metadata']))]
        # Render results as a HTML table
        output="<table><tr><th>select</th><th>ID</th><th>Published</th><th>Classification CPC</th>"
        for field in ai_generated_prompts.keys():
            output+=f"<th>✨{ai_generated_prompts[field][0]} (AI generated)</th>"
        output+="</tr>\n"
        # Parse all retrieved XML document to extract relevant information
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
            output+='<tr>'
            output+="<td>"+'<input type="checkbox" id="'+id+'" onchange="append_query(this)" ></td>'
            output+='<td><a href="/download/'+os.path.basename(doc).strip(".xml")+'.pdf"'+f">{id}</a></td><td>{date}</td><td>{category}</td>"
            for field in ai_generated_prompts.keys():
                with open(doc.strip(".xml")+"."+field+'.html', "r") as file:
                    content = file.read()
                    output+=f"<td>{content}</td>"
            output+="</tr>\n"
        output+="</table>\n"
        return output

    def extend(self, query):
        """ extend() is for UMLS concepts what retrieved() is for patents """
        store = deeplake.core.vectorstore.deeplake_vectorstore.DeepLakeVectorStore(path=self.umls_vector_dir)
        result = store.search(embedding_data=query, embedding_function=self.embed_model.get_text_embedding, k=self.span_top_k)
        # Get retrieved concept IDs and their contents
        concept_list = [result['metadata'][offset]['file_name'] for offset in range(0, len(result['metadata']))]
        content_list = [result['text'][offset] for offset in range(0, len(result['text']))]
        output="<table><tr><th>select</th><th>concept</th><th>alternatives</th></tr>\n"
        num_lines=0
        for offset in range(0, len(result['text'])):
            num_lines+=1
            # As some concepts might be empty, we need to retrieve more than needed,
            # So stop once enough 
            if num_lines > int(os.getenv('MAXNUM_DISPLAYED_CONCEPTS'))+1:
                break
            # Don't display long descriptions
            forms= [html2text(x) for x in content_list[offset].split("\n") if x !="" and len(x)<int(os.getenv('MAX_LEN_FOR_CONCEPT_DESC'))]
            # Don't display spurious forms
            forms = sorted(list(filter(lambda f: len(f)>3, forms)))
            if len(forms)<=0: # skip if concept has no form
                continue
            # HTML for the row of selectable concept
            concept_id = concept_list[offset].strip(".txt")
            output+="<tr>"
            output+="<td>"+'<input type="checkbox" id="'+concept_id+'" onchange="append_query(this)" ></td>'
            output+='<td><b>'+forms[0]+"</b></td><td>"+" ; ".join(forms)+"</td>"
            output+="</tr>"
        output+="</table>\n"
        return output
    
    def filter_query(self, query):
        """ remove concept IDs from query """
        terms=query.split()
        filtered = list(filter(lambda t: not concept_pattern.match(t), terms))
        return " ".join(filtered)
    
    def expand_query(self, query):
        """ Replace concept IDs in query by their contents"""
        terms=query.split()
        concepts = list(filter(lambda t: concept_pattern.match(t), terms))
        filtered = list(filter(lambda t: not concept_pattern.match(t), terms))
        query = " ".join(filtered)
        for concept in concepts:
            with open(self.umls_document_dir+"/"+concept[:4]+"/"+concept+".txt") as f:
                content = f.readlines()
            query+=" "+html2text(" ".join(content)).replace('\n', ' ')
        return query

    def reindex(self, index_name):
        """ Load, store, index data as vectors of text spans embedding """
        # Indexing patents
        if index_name in ["EP", "BOTH"]:
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
                    # os.system("cp "+fn.strip(".xml")+".pdf "+self.tmp_dir)
            # Load documents and build index
            print("loading data...")
            documents = SimpleDirectoryReader(self.tmp_dir).load_data(num_workers=int(os.getenv('NUM_WORKERS')))
            print("Extract AI generated fields...")
            for doc in tqdm(documents):
                # parse xml file
                root=ET.fromstring(bytes(doc.text, encoding='utf8'))
                # Extract AI generated files
                for field in ai_generated_prompts.keys():
                    filename = doc.metadata["file_path"].strip(".xml")+'.'+field+'.html'
                    with open(filename, "w") as file:
                        file.write(markdown(self.get_ai_generated_field("\n".join(root.xpath('//text()'))[:self.token_limit], field)))
            # embedding model
            Settings.embed_model = self.embed_model
            # ollama
            Settings.llm = self.llm_settings
            print("Indexing patents can take some time...")
            self.index = VectorStoreIndex.from_documents(
                documents, show_progress=True, storage_context=self.storage_context
            )
            print("Indexing patents completed...")
        # Indexing UMLS concepts and their forms
        if index_name in ["UMLS", "BOTH"]:
            print(f"Reindexing UMLS...")
            os.system("mkdir -p "+self.umls_vector_dir)
            # Load documents and build index
            concepts = SimpleDirectoryReader(self.umls_document_dir, recursive=True).load_data(num_workers=int(os.getenv('NUM_WORKERS')))
            # embedding model
            Settings.embed_model = self.embed_model
            # ollama
            Settings.llm = self.llm_settings
            print("Indexing umls concepts can take some time...")
            self.umls_index = VectorStoreIndex.from_documents(
                concepts, show_progress=True, storage_context=self.umls_storage_context
            )
            print("Indexing umls concepts completed...")
        if index_name not in ["EP", "UMLS", "BOTH"]:
            print("Error : Invalid index name. Choose 'EP' for patents or 'UMLS' for concepts", file=sys.stderr)

    def patchat(self, question):
        """ Start the chatbot in streaming mode """
        # remove concept IDs as their are not helpfull here
        question = self.filter_query(question)
        print(f"Answering '{question}'", file=sys.stderr)
        streaming_response = self.chat_engine.stream_chat(question)
        return streaming_response

if __name__ == "main":
    print("Coucouc")
import os 
from bs4 import BeautifulSoup
from tqdm import tqdm
from epo.tipdata.epab import EPABClient

class Toolkit:
    
    def __init__(self, query):
        self.epab_query=query
        self.model_name=os.getenv('MODEL_NAME')
        self.match_all=os.getenv('MATCH_ALL')
        self.ignore_case=os.getenv('IGNORE_CASE')
        self.epab_size=os.getenv('EPAB_SIZE')
        self.doc_limit=os.getenv('DOC_LIMIT')
        self.llm=os.getenv('LLM')
        self.token_limit=os.getenv('TOKEN_LIMIT')
        self.document_dir=os.getenv('DOC_DIR')
        self.vector_dir=os.getenv('VEC_DIR')
        os.system("mkdir -p "+self.document_dir)
        os.system("mkdir -p "+self.vector_dir)

    def reindex(self):
        print(f"Reindexing '{self.epab_query}'...")
        # clean document directory
        os.system("rm -f "+self.document_dir+"/*")
        epab = EPABClient(env=self.epab_size)
        q = epab.query_description(text=self.name, match_all=self.match_all, ignore_case=self.ignore_case)
        all = "all" if self.match_all else "one of the"
        print(f"Found {q} publications containing the {all} following terms: {self.epab_query}")
        tab = q.get_results(
            "epab_doc_id, title.fr, abstract, description, publication, inventor", limit=self.doc_limit
        )
        print(f"Storing {self.doc_limit} patents to disk...")
        for offset in tqdm(range(self.doc_limit)):
            data = tab["description.text"][offset]
            with open(self.document_dir+"/" + tab["epab_doc_id"][offset] + ".txt", "w") as file:
                print(data, file=file)
            soup = BeautifulSoup(data, "html.parser")
        print("Done.")
        print("Completed.")

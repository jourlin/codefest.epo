import os
from dotenv import load_dotenv
from tqdm import tqdm

def extract_umls(input_file_name,output_dir): 
    concepts = dict()
    with open(input_file_name, 'r') as in_file:
        for line in tqdm(in_file):
            line=line.strip('\n').split('\t')
            if line:
                if line[1] not in concepts:
                    concepts[line[1]] = set(line[2:])
                    concepts[line[1]].add(line[0])
                else:
                    concepts[line[1]]= concepts[line[1]].union(set(line[2:]))
            else:
                break
    for key in tqdm(concepts.keys()):
        dirname=out_dir+'/'+key[:4]
        os.system('mkdir -p '+dirname)
        with open(dirname+'/'+key+'.txt', 'w+') as out_file:
            print('\n'.join(list(concepts[key])), file=out_file)
            
   
load_dotenv()
out_dir= os.getenv('UMLS_DOC_DIR') 
os.system('rm -fr '+out_dir+"/*")        
filename='../umls_defs/umls_def.tsv'
extract_umls(filename, out_dir)

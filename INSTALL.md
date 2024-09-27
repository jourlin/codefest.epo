# INSTALL INSTRUCTIONS

## Warning : 
The following instructions were tested successfully with the followings specs :
- Ubuntu 24.04 LTS
- Nvidia GPU with at least 6Gb VRAM (A3000 & 3060)
You might need to adapt some parts to fit your computer and its operating system

## Step 1: Download latest release

* visit [my github repository](https://github.com/jourlin/codefest.epo/releases) and download ```codefest.epo-X.Y.zip``` where X and Y are respectively the version and subversion numbers of the latest release.

## Step 2: Install Flask server

1. Commands to run in your linux terminal

1. ```cd codefest.epo``` 
2. ```python -m venv .```
3. ```source bin/activate```
4. ```pip install -r requirements.txt```
5. Edit ```.env``` to match your local system

## Step 3: Download full-text patents
- Full text patents can be downloaded by subscribed users from 
[EPO Bulk data](https://publication-bdds.apps.epo.org/raw-data/products/subscription/product/4>)
- The process of downloading the completed database might be fully automatized, but it would require to make use of very important ressources and bandwith. The full compressed database seems to weight over 500Gb and to contain over 500k full-text patents, each one provided in xml and pdf formats.
- Each zip archive contains several zip archives, that contains xml and pdf versions of the patents. We tested the flask server with EPRTBJV2024000037001001.zip and extracted only xml files for each one of the 5652 full-text patents contained in this particular zip archive.
- Top level zip files must be moved to the directory given by $DOC_DIR environement variable that is defined in file ```.env```

## Step 4: Download UMLS data
- Full UMLS data can be obtained at :
[UMLS Metathesaurus](https://download.nlm.nih.gov/umls/kss/2024AA/umls-2024AA-metathesaurus-full.zip)
However it is free of charge, user must obtain a UMLS licence and is requested to sign in before downloading the zip archive.
- umls-YYYY-AA-metathesaurus-full.zip must be moved to the directory given by $UMLS_DOC_DIR environement variable that is defined in file ```.env``` (XXXX is the current year and AA a letter code )

## Step 5: Data preparation
- Execute ```bash data_preparation.sh``` in your terminal (codefest.epo should be your current directory)
**WARNING** : Depending on the size of data to be unzipped, the full process can take hours, even days.
For instance, indexing only 209 full-text patents takes about 15 min on a Dell Precision 7560 laptop with 32Gb RAM and 6Gb VRAM (Nvidia A3000).

## Step 6: Run the embedding indexer
```flask reindex BOTH```
(instead of "BOTH" you can speficy "UMLS" (for medical concepts) or "EP" (for patents) when only one the the indexes needs (re)indexing)
**WARNING** : Depending on the size of data to be indexed, the full process can take hours or even days.
For instance, indexing only 10k concepts takes about 15 min on a Dell Precision 7560 laptop with 32Gb RAM and 6Gb VRAM (Nvidia A3000).
So, as the full UMLS database contains over 3 million concepts, expecting indexing duration would be about 3 days with an equivalent computer setting.

## Step 7: How to run the web server
```flask run```

## Step 8: Use the retriever and chatbot
1. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) with a web browser

## Step 9: User guide
Have a look at [USER_GUIDE.md](./USER_GUIDE.md) for instructions and explanation of user's interface

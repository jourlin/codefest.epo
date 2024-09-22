# Warning : 
The following instructions were tested successfully with the followings specs :
- Ubuntu 24.04 LTS
- Nvidia GPU with at least 6Gb VRAM (A3000 & 3060)
You might need to adapt some parts to fit your computer and its operating system

# Download latest release

1. 

## Step by step installation

*warning*: All instructions are given for installation on a Ubuntu 24.04 LTS operating system, with 32Gb RAM and 6Gb VRAM Nvidia GPU. They probably need to be adapted for different operating systems or machine specifications.

1. Download latest release of the sofware :
# How to install Flask server

## Commands to run in your linux terminal

1. ```python -m venv .```
2. ```source bin/activate```
3. ```pip install -r requirements.txt```
4. Edit ```.env``` to match your local system

## How to import full-text patents

- Full text patents can be downloaded by subscribed users from 
<https://publication-bdds.apps.epo.org/raw-data/products/subscription/product/4>
The process of downloading the completed database could be fully automatized, but it would require to make use of very important ressources and bandwith. The full compressed database seems to weight over 500Gb and over 500k full-text patents, each one provided in xml and pdf formats.
Each zip archive contains several zip archives, that contains xml and pdf versions of the patents. We tested the flask server with EPRTBJV2024000037001001.zip and extracted only xml files for each one of the 5652 full-text patents contained in this particular zip archive.
The xml files should be moved to the directory given by $DOC_DIR environement variable that is defined in file ```.env``` before executing ```flask reindex```

## How to run the embedding indexer

```flask reindex "my request"```

## How to run the web server

```flask run```

### Use the chatbot

1. Open ```http://127.0.0.1:5000``` with a web browser

# Directories
* [./docs](./docs): project documentation
* [./docs/images](./docs/images): required images for project documentation
* [./src](./src): code source and scripts
* [./resources](./resources): Downloaded data + filtered data + generated data

# Files :
* Documentation
    * [./README.md](./README.md): General information
    * [./requirements.txt](./requirements.txt): List of open source python modules needed for execution, along with their version
    * [./docs/DOWNLOAD_DATA.md](./docs/DOWNLOAD_DATA.md): How to download UMLS metathesaurus and EPO patents
    * [./docs/LICENSE.md](./docs/LICENSE.md): Licence information (GNU GPL Afero)
    * [./docs/INSTALL.md](./docs/INSTALL.md): Installation Instructions
    * [./docs/USER_GUIDE.md](./docs/USER_GUIDE.md): How to use the web UI
    * [./docs/TODO.md](./docs/TODO.md): Things that could be improved
* Resources
    * [./resources/documents](./resources/documents): Location of downloaded patents
    * [./resources/umls](./resources/umls): Location of download UMLS files
    * [./resources/my_patents](./resources/my_pâtents): Location of user's documents
* Source code
    * [./src/patchat.ipynb](./src/patchat.ipynb): a very simple notebook demonstrating some of the Patchat features on EPO TIP platform.
    * [./src/data_preparation.sh](./src/data_preparation.sh): bash script for preparing the data
    * [./src/.env](./src/.env): Environement variables (configuration) that are automatically loaded by Flask.
    * [./src/app.py](./src/app.py): Flask's main file. API routes are defined here.
    * [./src/toolkit.py](./src/toolkit.py): Main python code for langage processing, retrieval and RAG chatbot based on open source models
    * [./src/static/favicon.ico](./src/static/favicon.ico): a small decoration for browser's tabs.
    * [./src/static/patchat.css](./src/static/patchat.css): a very light styling for web pages
    * [./src/static/patchat.js](./src/static/patchat.css): main Javascript code
    * [./src/templates/index.html](./src/templates/index.html): Flask template to be rendered
    
    




    
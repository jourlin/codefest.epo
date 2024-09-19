# Download Patent data from EPO Data Bulk
For conditions see:  
https://www.epo.org/service-support/ordering/raw-data-terms-and-conditions.html
Once signed in, the list of zip files for EPO full-text data is located here :
https://publication-bdds.apps.epo.org/raw-data/products/subscription/product/32
- Download any subset of *.zip files into the ./documents directory situated at the project's root.

# DOWNLOAD UMLS data
The downloading of UMLS data is free of charge, but requires to obtain a licence.
Details are given here :
https://www.nlm.nih.gov/research/umls/index.html
The only required file is located here :
https://download.nlm.nih.gov/umls/kss/2024AA/umls-2024AA-mrconso.zip

# Data preparation
Execute ```sh data_preparation.sh``̀in the project's root directory to extract :
- full-text patents in both xml and pdf formats
- UMLS entities and their textual forms


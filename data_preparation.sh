# Prepare patent textual data (needs to be updated according to EPO Bulk Data updates)

cd documents
unzip *.zip
rm -f *.zip
rm -fr DTDS index.html VOLUMEID CONTENTS index.xml
find . -name "*.zip" -exec unzip -n {} \;
rm -fr DOC TOC.xml
cd ..

# Prepare UMLS data (needs to be updated according to UMLS updates)
# Note that at the time I wrote this, the data contained a total of :
# 8,684,051 textuals forms for a total of  3,210,943 concepts

cd umls
unzip umls-2024AA-metathesaurus-full.zip 2024AA/META/MRCONSO.RRF 2024AA/META/MRDEF.RRF
rm umls-2024AA-metathesaurus-full.zip

# The following code makes a directory tree containing a file for each UMLS concept
# The file contains all english lower-case textual forms and when they are provided, 
# all textual definitions in all languages that are provided.

grep '|ENG|' 2024AA/META/MRCONSO.RRF | cut -d '|' -f1,15 |tr '|' '\t'| tr '[:upper:]' '[:lower:]' > /tmp/cui_str.tsv
cut -d '|' -f1,6 2024AA/META/MRDEF.RRF |tr '|' '\t'| tr '[:upper:]' '[:lower:]' >> /tmp/cui_str.tsv
sort -u -k1 /tmp/cui_str.tsv > cui_str.tsv
rm /tmp/cui_str.tsv
while read -r cui str
do
  mkdir -p  ${cui::4}
  echo $str >>  ${cui::4}/$cui.txt
done < cui_str.tsv
rm cui_str.tsv
rm -fr 2024AA
cd ..
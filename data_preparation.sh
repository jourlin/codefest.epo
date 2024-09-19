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
unzip umls-2024AA-mrconso.zip
rm umls-2024AA-mrconso.zip
grep '|ENG|' 2024AA/META/MRCONSO.RRF| cut -d '|' -f1,15 |tr '|' '\t' | sort > cui_str.tsv
while read -r cui str
do
  mkdir -p  ${cui::4}
  echo $str >> ${cui::4}/$cui.txt
done < cui_str.tsv
rm cui_str.tsv
rm -fr 2024AA
cd ..
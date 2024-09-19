cd documents
unzip *.zip
rm -f *.zip
rm -fr DTDS index.html VOLUMEID CONTENTS index.xml
find . -name "*.zip" -exec unzip -n {} \;
rm -fr DOC TOC.xml
cd ..
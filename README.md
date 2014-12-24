
## Basic Django Project Setup

```bash
export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python3
export WORKON_HOME=/XXX/python-env
source /usr/local/bin/virtualenvwrapper.sh
export PATH=/usr/local/bin/:$PATH

mkvirtualenv xxx
pip install -r requirements.txt
```

Assumes a GMOD Chado schema installation with the relationship and sequence ontologies loaded.

```bash
insert into organism ( abbreviation, genus, species, common_name ) values ( 'H.sapiens', 'Homo', 'sapiens_GRCh38', 'human_GRCh38');
insert into organism ( abbreviation, genus, species, common_name ) values ( 'M.musculus', 'Mus', 'musculus_mm10', 'mouse_mm10');
```

Download chromosome data and populate the database:

```bash
curl ftp://hgdownload.cse.ucsc.edu/goldenPath/hg38/database/chromInfo.txt.gz > tmp/chromInfo_human.txt.gz
curl ftp://hgdownload.cse.ucsc.edu/goldenPath/mm10/database/chromInfo.txt.gz  > tmp/chromInfo_mouse.txt.gz

curl ftp://hgdownload.cse.ucsc.edu/goldenPath/hg38/database/cytoBand.txt.gz  -o tmp/cytoBand_human.txt.gz
curl ftp://hgdownload.cse.ucsc.edu/goldenPath/mm10/database/cytoBand.txt.gz  -o tmp/cytoBand_mouse.txt.gz

curl http://www.immunobase.org/regions/htdocs/downloads/Hs_GRCh38-AA-assoc_tableGFF -o tmp/Hs_GRCh38-AA-assoc_table.gff
curl http://www.immunobase.org/regions/htdocs/downloads/Hs_GRCh38-ATD-assoc_tableGFF -o tmp/Hs_GRCh38-ATD-assoc_table.gff
curl http://www.immunobase.org/regions/htdocs/downloads/Hs_GRCh38-CEL-assoc_tableGFF -o tmp/Hs_GRCh38-CEL-assoc_table.gff
curl http://www.immunobase.org/regions/htdocs/downloads/Hs_GRCh38-CRO-assoc_tableGFF -o tmp/Hs_GRCh38-CRO-assoc_table.gff
curl http://www.immunobase.org/regions/htdocs/downloads/Hs_GRCh38-JIA-assoc_tableGFF -o tmp/Hs_GRCh38-JIA-assoc_table.gff
curl http://www.immunobase.org/regions/htdocs/downloads/Hs_GRCh38-MS-assoc_tableGFF -o tmp/Hs_GRCh38-MS-assoc_table.gff
curl http://www.immunobase.org/regions/htdocs/downloads/Hs_GRCh38-PBC-assoc_tableGFF -o tmp/Hs_GRCh38-PBC-assoc_table.gff
curl http://www.immunobase.org/regions/htdocs/downloads/Hs_GRCh38-PSO-assoc_tableGFF -o tmp/Hs_GRCh38-PSO-assoc_table.gff
curl http://www.immunobase.org/regions/htdocs/downloads/Hs_GRCh38-RA-assoc_tableGFF -o tmp/Hs_GRCh38-RA-assoc_table.gff
curl http://www.immunobase.org/regions/htdocs/downloads/Hs_GRCh38-SLE-assoc_tableGFF -o tmp/Hs_GRCh38-SLE-assoc_table.gff
curl http://www.immunobase.org/regions/htdocs/downloads/Hs_GRCh38-T1D-assoc_tableGFF -o tmp/Hs_GRCh38-T1D-assoc_table.gff
curl http://www.immunobase.org/regions/htdocs/downloads/Hs_GRCh38-UC-assoc_tableGFF -o tmp/Hs_GRCh38-UC-assoc_table.gff
```

Use the populate_db command line argument to load the data:

```bash
python manage.py populate_db --help
python manage.py populate_db --chr tmp/chromInfo_human.txt.gz --org human_GRCh38
python manage.py populate_db --chr tmp/chromInfo_mouse.txt.gz --org mouse_mm10
python manage.py populate_db --bands tmp/cytoBand_human.txt.gz --org human_GRCh38 
python manage.py populate_db --bands tmp/cytoBand_mouse.txt.gz --org=mouse_mm10
python manage.py populate_db --disease tmp/disease.list

python manage.py populate_db --org human_GRCh38 --gff tmp/Hs_GRCh38-AA-assoc_table.gff 
python manage.py populate_db --org human_GRCh38 --gff tmp/Hs_GRCh38-AA-assoc_table.gff.gz 
python manage.py populate_db --org human_GRCh38 --gff tmp/Hs_GRCh38-ATD-assoc_table.gff.gz
python manage.py populate_db --org human_GRCh38 --gff tmp/Hs_GRCh38-CEL-assoc_table.gff.gz
python manage.py populate_db --org human_GRCh38 --gff tmp/Hs_GRCh38-CRO-assoc_table.gff.gz 
python manage.py populate_db --org human_GRCh38 --gff tmp/Hs_GRCh38-JIA-assoc_table.gff.gz 
python manage.py populate_db --org human_GRCh38 --gff tmp/Hs_GRCh38-MS-assoc_table.gff.gz 
python manage.py populate_db --org human_GRCh38 --gff tmp/Hs_GRCh38-PBC-assoc_table.gff.gz 
python manage.py populate_db --org human_GRCh38 --gff tmp/Hs_GRCh38-PSO-assoc_table.gff.gz 
python manage.py populate_db --org human_GRCh38 --gff tmp/Hs_GRCh38-RA-assoc_table.gff.gz 
python manage.py populate_db --org human_GRCh38 --gff tmp/Hs_GRCh38-SLE-assoc_table.gff.gz 
python manage.py populate_db --org human_GRCh38 --gff tmp/Hs_GRCh38-T1D-assoc_table.gff.gz 
python manage.py populate_db --org human_GRCh38 --gff tmp/Hs_GRCh38-UC-assoc_table.gff.gz 

```

Run the server:

```bash
python manage.py runserver localhost:9000
```

In a browser try http://localhost:9000/bands/cached/human_GRCh38/

```bash
./manage.py test db.tests.TastypieTests -v3
./manage.py test db.tests.DbTests -v3
```

### Cache 

To get the caching to work memcache needs to be installed:
```
cp django_template/settings_secret.py.template django_template/settings_secret.py
sudo apt-get install memcached
```


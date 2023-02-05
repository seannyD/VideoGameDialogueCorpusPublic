from urllib.request import *
import requests, io, os
from zipfile import ZipFile

url = "http://fayde.seadragonlair.co.uk/downloads/dealogue-db-jv-21-12-21.zip"

r = requests.get(url)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall("raw/db.zip")

os.rename("raw/db.zip/discobase12-17-2021-4-18-51-PM.db", "raw/discobase12-17-2021-4-18-51-PM.db")
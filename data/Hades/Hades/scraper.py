from urllib.request import *
import requests, io, os
from zipfile import ZipFile

url = "https://drive.google.com/uc?export=download&id=1EI84FH-FOXTh2thpt9GSAMTuzEyoE8TB"

r = requests.get(url)
z = ZipFile(io.BytesIO(r.content))
z.extractall("raw/")

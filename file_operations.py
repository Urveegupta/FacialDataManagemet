from pathlib import Path
from zipfile import ZipFile
import tarfile
import shutil
import os

class Extract:

    

    # extraction method 1 (.tar , .tgz , .tar.gz)

    def extract_tar(self):
        print(self.filepath)
        tar = tarfile.open(self.filepath, 'r')
        for item in tar:
            tar.extract(item, self.extract_path)
            if item.name.find(".tgz") != -1 or item.name.find(".tar") != -1:
                self.extract_tar(item.name, "./" + item.name[:item.name.rfind('/')])


    # extraction method 2 (.zip)

    def extract_zip(self):
        print(self.filepath)
        with ZipFile(self.filepath, 'r') as zip:
            print('Extracting all the files now...')
            zip.extractall(self.extract_path)
            print('Extraction complete!')


    # check extension and set a method for extraction
    
    def set_extract_method(self):

        # check extension
        ext = Path(self.filepath).suffix

        if ext in ['.tar','.tgz','.gz']:
            Extract.extract_tar(self)
           
        if ext in ['.zip']:
            Extract.extract_zip(self)

    def __init__(self, filepath,extract_path):
        self.filepath = filepath
        self.extract_path = extract_path
        self.set_extract_method()


class Uploadfile:
    

    def uploadfiles(self):
        #self.location = self.location + "/" + str(self.file.filename)
        print("in upload files")
        with open(self.location + "/" + str(self.file.filename) , "wb") as buffer:
            shutil.copyfileobj(self.file.file , buffer)
        print("upload complete")


    def __init__(self, file, location):
        self.file = file
        self.location = location
        

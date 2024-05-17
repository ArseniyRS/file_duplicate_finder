import subprocess


class FileInfo:
    def __init__(self, name, path, size):
        self.name = name
        self.path = path
        self.size = size

    def name(self):
        return self.name
    
    def path(self):
        return self.path
    
    def size(self):
        return self.size
    
    def open_file_folder(self):
        subprocess.Popen(f'explorer /select, {self.path}')
        
    def open_file(self):
        subprocess.Popen(f'explorer {self.path}')
    
    def delete_file(self):
        subprocess.Popen(f'del {self.path}')


class ExtendedFileInfo(FileInfo):
    def __init__(self, fileInfo, hash):
        super().__init__(fileInfo.name, fileInfo.path, fileInfo.size)
        self.hash = hash

    def hash(self):
        return self.hash

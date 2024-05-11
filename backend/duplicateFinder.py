import os
import hashlib
from backend.common import Singleton
from backend.fileInfo import FileInfo, ExtendedFileInfo
from backend.logger import ProgressLogger
from PyQt6.QtCore import pyqtSignal, QObject

default_path = os.path.join(os.getcwd(), '')

class DuplicateFinder(Singleton, QObject):
  
  def __init__(self):
    super().__init__()
    self.open_files_logger = ProgressLogger()
    self.search_duplicates_logger = ProgressLogger()

    self.files = []
    self.sub_directories = []
    self.duplicate_files = []
  
    self.aborted = False
  
  def abort(self):
    self.aborted = True
    
  def clear_abort(self):
    self.aborted = False
  
  def _set_log_open_files(self, message):
    self.open_files_logger.set_log(message)
    self.open_files_logger.log_signal.emit(message)
    
  def _set_log_search_duplicate_files(self, message):
    self.search_duplicates_logger.set_log(message)
    self.search_duplicates_logger.log_signal.emit(message)
  
  def _set_open_files_progress(self, value):
    self.open_files_logger.set_progress(value)
    self.open_files_logger.progress_signal.emit(value)
    
  def _set_open_files_total(self, value):
    self.open_files_logger.set_total(value)
    self.open_files_logger.total_signal.emit(value)
    
  def _set_search_duplicates_progress(self, value):
    self.search_duplicates_logger.set_progress(value)
    self.search_duplicates_logger.progress_signal.emit(value)
  
  def _set_search_duplicates_total(self, value):
    self.search_duplicates_logger.set_total(value)
    self.search_duplicates_logger.total_signal.emit(value)
  
  def _clear_search_duplicates_progress(self):
    self.search_duplicates_logger.set_progress(0)
    self.search_duplicates_logger.progress_signal.emit(0)
    self.search_duplicates_logger.set_total(0)
    self.search_duplicates_logger.total_signal.emit(0)
    
  
  def _clear_open_files_progress(self):
    self.open_files_logger.set_progress(0)
    self.open_files_logger.progress_signal.emit(0)
    self.open_files_logger.set_total(0)
    self.open_files_logger.total_signal.emit(0)

  
  def get_file_list_by_path(self, path = default_path, include_subfolders = False):
    self._clear_open_files_progress()
    self._set_log_open_files('Preparing to open files...')
    self._set_open_files_total(self._get_open_files_iteration_count(path, include_subfolders))
    files, subdirs = self._get_file_list_by_path_recursive(path, include_subfolders)
    self.files = files
    self.sub_directories = subdirs
    
  def _get_file_list_by_path_recursive(self, path = default_path, include_subfolders = False):
    files = []
    sub_directories = []
    f_list_paths = []
    
    try:
      f_list_paths = os.listdir(path)
    except PermissionError as e:
      self._set_log_open_files(e.strerror)
      return files, sub_directories
    
    for f in f_list_paths:
      if self.aborted:
        self._set_log_open_files('Opening has been interrupted')
        return [[],[]]

      file_path = os.path.join(path, f)
      normalized_path = os.path.normpath(file_path)

      if not os.path.isfile(normalized_path) and include_subfolders:
          sub_directories.append(normalized_path)
          self._set_log_open_files('Searching in the directory: ' + normalized_path)
          files_from_dir, subdirs_from_dir = self._get_file_list_by_path_recursive(normalized_path, include_subfolders)
          files = [*files, *files_from_dir]

      if os.path.isfile(normalized_path):
          new_file = FileInfo(f, normalized_path, os.path.getsize(normalized_path))
          files.append(new_file)
          self._set_log_open_files('Opened file: ' + new_file.path)

      self._set_open_files_progress(self.open_files_logger.progress + 1)

    return files, sub_directories
    
    
  def _search_duplicates(self, files, prop = 'hash'):
    duplicates = []
    remainingFiles = []
    assumed = []
    if len(files) > 0:
      assumed = files[0]

    for i, f in enumerate(files):
      if self.aborted:
        break
      if(i == 0):
          continue

      self.search_duplicates_logger.log_signal.emit(f'Checking {prop} of {f.path}')
      if getattr(assumed, prop) == getattr(files[i], prop):
          self.search_duplicates_logger.progress_signal.emit(self.search_duplicates_logger.progress + 1)
          self.search_duplicates_logger.log_signal.emit('Found duplicates: ' + assumed.path + ' and ' + files[i].path)
          duplicates.append(assumed)
          duplicates.append(files[i])
      else:
          assumed = files[i]  
          remainingFiles.append(files[i]) 
    return [duplicates, remainingFiles]

  
  def _calculate_hash_file(self, file, algorithm='md5'):
    if algorithm.lower() == 'sha1':
        hash_func = hashlib.sha1()
    elif algorithm.lower() == 'sha256':
        hash_func = hashlib.sha256()
    else:
        hash_func = hashlib.md5()
    
    with open(file.path, 'rb') as file:
        while True and not self.aborted:
          data = file.read(4096)
          if not data:
              break
          hash_func.update(data)
    
    return hash_func.hexdigest()
  
  
  def get_duplicates(self, by_size = False, by_hash = False, by_name = False):
    duplicates = []
    remainingFiles = self.files

    if by_size:
        self._clear_search_duplicates_progress()
        self.search_duplicates_logger.log_signal.emit('Start to search by size...')
        sorted_files = sorted(remainingFiles, key=lambda x: x.size)
        
        self.search_duplicates_logger.log_signal.emit('Searching duplicates...')
        search_result = self._search_duplicates(sorted_files, 'size')
        duplicates = [*duplicates, *search_result[0]]
        remainingFiles = search_result[1]

    if by_hash:
        def extend_file(f):
          self._set_search_duplicates_progress(self.search_duplicates_logger.progress + 1)
          self.search_duplicates_logger.log_signal.emit(f'Calculate hash of file: {f.path}')
          return ExtendedFileInfo(f, self._calculate_hash_file(f))
        
        self._clear_search_duplicates_progress()
        self.search_duplicates_logger.log_signal.emit('Start to search by hash...')
        self._set_search_duplicates_total(len(remainingFiles))
        files_with_hash = [extend_file(f) for f in remainingFiles]
        
        self._clear_search_duplicates_progress()
        self.search_duplicates_logger.log_signal.emit('Searching duplicates...')
        sorted_files = sorted(files_with_hash, key=lambda x: x.hash)

        search_result = self._search_duplicates(sorted_files, 'hash')
        duplicates = [*duplicates, *search_result[0]]
        remainingFiles = search_result[1]
    
    if by_name:
        self.search_duplicates_logger.log_signal.emit('Start to search by name...')
        sorted_files = sorted(remainingFiles, key=lambda x: x.name)
        self.search_duplicates_logger.log_signal.emit('Searching duplicates...')
        search_result = self._search_duplicates(sorted_files, 'name')
        duplicates = [*duplicates, *search_result[0]]
  
    self.duplicate_files = duplicates
  
  
  
  
  
  
  
  
  
  
  
  def _get_open_files_iteration_count(self, path = default_path, include_subfolders = False):
    result = 0
    try:
      f_list_paths = os.listdir(path)
    except PermissionError as e:
      self.open_files_logger.log_signal.emit(f'Permission denied: {e.filename}')
      return 0
      
    for f in f_list_paths:
      if self.aborted:
        return 0
      file_path = os.path.join(path, f)
      normalized_path = os.path.normpath(file_path)
      if not os.path.isfile(normalized_path) and include_subfolders:
        result += self._get_open_files_iteration_count(normalized_path, include_subfolders)
      result += 1
    
    return result
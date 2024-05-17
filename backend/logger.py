from PyQt6.QtCore import pyqtSignal, QObject


class Logger:
    def __init__(self):
      self.is_Develop = False
      self.log = ''

    def log_message(self, message):
        self.log = message
    
    def get_log(self):
        return self.log
    
    def clear(self):
        self.log = ''
        
    def _print_log(self):
        print(self.log)
    
    

class ProgressLogger(QObject, Logger):
    log_signal = pyqtSignal(str)
    total_signal = pyqtSignal(int)
    progress_signal = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.total = 0
        self.progress = 0

    def set_progress(self, value):
      self.progress = value
    
    def progress(self):
      return self.progress
    
    def set_total(self, value):
      self.total = value
      
    def total(self):
      return self.total
    
    def log(self):
      return self.log
    
    def set_log(self, message):
      if(self.is_Develop):
        self._print_log()
        self.log = message

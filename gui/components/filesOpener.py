from PyQt6.QtWidgets import QPushButton, QWidget, QFileDialog, QCheckBox, QVBoxLayout, QHBoxLayout, QLabel
from backend.main import duplicate_finder
from gui.components.searchProgress import ProgressBar
import time
import threading

class FilesOpener(QWidget):

  def __init__(self, parent=None):
    super().__init__(parent)
    self.parent = parent
    duplicate_finder.open_files_logger.progress_signal.connect(self.open_progress)
    duplicate_finder.open_files_logger.total_signal.connect(self.set_progress_total)
    duplicate_finder.open_files_logger.log_signal.connect(self.set_progress_message)
    self.render()
    

  def set_progress_total(self, value):
    self.progress.setRange(0, value)
    
  def set_progress_message(self, message):
    self.progress.setMessage(message)
  
  def open_progress(self, value):
    self.progress.setValue(value)
    
  
  def on_open_folder(self):
    duplicate_finder.abort()
    self.directory = QFileDialog.getExistingDirectory(self, 'Open folder')

    if not self.directory:
      self.parent.is_open_files.emit(False)
      self.directory_label.setText(f'Directory not selected')
      self.progress.hide()
      return
    duplicate_finder.clear_abort()
    self.progress.show()
    
    def open_folder_thread():
      self.parent.is_open_files.emit(True)
      selected_directory_message = f'Selected directory: {self.directory}'
      self.directory_label.setText(selected_directory_message)
      duplicate_finder.get_file_list_by_path(self.directory, self.include_subfolders.isChecked())
      self.progress.hide()
      
    
    thread = threading.Thread(target=open_folder_thread)
    thread.start()


  def render(self):
    self.include_subfolders = QCheckBox('Include subfolders', self)
    self.include_subfolders.setChecked(True)
  
    button = QPushButton('Open folder', self)
    button.clicked.connect(self.on_open_folder)
    button.setObjectName(u'OpenFileButton')
    
    self.directory_label = QLabel('Directory not selected', self)
    self.progress = ProgressBar(self)
    self.progress.hide()

    settings_layout = QHBoxLayout()
    settings_layout.addWidget(self.include_subfolders)
    
    layout = QVBoxLayout()
    layout.addLayout(settings_layout)
    layout.addWidget(button)
    layout.addWidget(self.directory_label)
    layout.addWidget(self.progress)
    
    self.setLayout(layout)

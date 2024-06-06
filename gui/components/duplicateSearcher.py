
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QCheckBox,QLabel, QHBoxLayout
from PySide6.QtCore import Signal
import time
from backend.main import duplicate_finder

import threading

from gui.components.searchProgress import ProgressBar

class DuplicateSearcher(QWidget):

  def __init__(self, parent = 'None'):
    super().__init__(parent)
    self.parent = parent
    self.parent.is_open_files.connect(self.is_open_files_changed)
    duplicate_finder.search_duplicates_logger.progress_signal.connect(self.open_progress)
    duplicate_finder.search_duplicates_logger.total_signal.connect(self.set_progress_total)
    duplicate_finder.search_duplicates_logger.log_signal.connect(self.set_progress_message)
    self.render()

  def set_progress_total(self, value):
    self.progress.setRange(0, value)
  
  def set_progress_message(self, message):
    self.progress.setMessage(message)

  def open_progress(self, value):
    self.progress.setValue(value)


  def search_start(self):
    self.button.setDisabled(True)
    duplicate_finder.abort_controller.clear_abort()
    self.progress.show()
    self.parent.is_search_finished.emit(False)
  
  def search_end(self):
    self.button.setDisabled(False)
    self.progress.hide()
    self.parent.is_search_finished.emit(True)
  
  def is_open_files_changed(self, is_open_files):
    self.button.setDisabled(is_open_files)

  def search_duplicates(self):
    with_hash = self.with_hash.isChecked()
    with_size = not with_hash

    self.search_start()
    def thread_search():
      duplicate_finder.get_duplicates(with_size, with_hash, self.with_name.isChecked())
      self.search_end()

    
    thread = threading.Thread(target=thread_search)
    thread.start()

  def render(self):
    self.button = QPushButton('Search duplicates', self)
    self.button.clicked.connect(self.search_duplicates)
    self.button.setObjectName(u'SearchButton')
    self.button.setDisabled(True)
    self.with_hash = QCheckBox('With hash', self)
    self.with_name = QCheckBox('With name', self)

    self.progress = ProgressBar(self)
    self.progress.hide()
    
    layout = QVBoxLayout()
    settings_layout = QHBoxLayout()
    layout.addWidget(self.button)
    settings_layout.addWidget(self.with_hash)
    settings_layout.addWidget(self.with_name)
    layout.addLayout(settings_layout)
    layout.addWidget(self.progress)

    self.setLayout(layout)
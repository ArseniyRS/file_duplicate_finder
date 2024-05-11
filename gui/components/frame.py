from PyQt6.QtWidgets import QPushButton, QWidget, QFileDialog, QCheckBox, QVBoxLayout, QGridLayout
from PyQt6.QtCore import pyqtSignal

from gui.components.duplicateViewer import DuplicateViewer
from gui.components.filesOpener import FilesOpener
from gui.components.duplicateSearcher import DuplicateSearcher



class Frame(QWidget):
  is_open_files = pyqtSignal(bool)
  is_search_finished = pyqtSignal(bool)
  
  def __init__(self, parent='None'):
    super().__init__(parent)
    self.render()

  def render(self):
    frame_layout = QGridLayout()
    files_opener = FilesOpener(self)
  
    search_duplicate = DuplicateSearcher(self)

    table_viewer = DuplicateViewer(self)

    frame_layout.addWidget(files_opener)
    frame_layout.addWidget(search_duplicate)
    frame_layout.addWidget(table_viewer)

    self.setLayout(frame_layout)



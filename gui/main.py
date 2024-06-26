import sys
from PySide6.QtWidgets import QApplication, QWidget, QGridLayout
from PySide6.QtGui import QIcon
from gui.components.frame import Frame

from qt_material import apply_stylesheet

class MainWindow(QWidget):

  def __init__(self):
    super().__init__()
    self.render()

  def render(self):
    self.setWindowTitle("FDF - Finder duplicate files")
    self.setWindowIcon(QIcon('duplicate.png'))
    self.setFixedSize(800, 600)
    self.setObjectName(u"MainWindow")
    frame = Frame(self)
    layout = QGridLayout(self)
    layout.addWidget(frame)
    self.setLayout(layout)
    self.show()


def startGUI():
  app = QApplication(sys.argv)
  
  # setup stylesheet
  apply_stylesheet(app, theme='dark_purple.xml')

  window = MainWindow()
  window.show()
  sys.exit(app.exec())







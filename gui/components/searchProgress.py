from PySide6.QtWidgets import QWidget, QProgressBar, QVBoxLayout, QLabel

class ProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.render()
    
    def setRange(self, min, max):
      self.progress.setRange(min, max)
      
    def setValue(self, value):
      self.progress.setValue(value)
    
    def setMessage(self, message):
      self.label.setText(message)
    
    
    def render(self):
      self.progress = QProgressBar(self)
    
      self.progress.setRange(0, 100)
      self.progress.setValue(30)
      self.progress.setFormat('%p%')
      self.progress.setStyleSheet('QProgressBar {border-radius: 8px; text-align: center;} QProgressBar::chunk {background-color: #05B8CC; width: 20px;}')

      self.label = QLabel('', self)
      
      layout = QVBoxLayout()
      layout.addWidget(self.progress)
      layout.addWidget(self.label)
      self.setLayout(layout)
      self.hide()
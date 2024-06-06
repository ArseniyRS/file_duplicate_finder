from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QMenu, QHeaderView
from PySide6.QtCore import Qt, QAbstractTableModel, QSortFilterProxyModel
import subprocess
from backend.main import duplicate_finder

class TableModel(QAbstractTableModel):
  def __init__(self, table_data):
    super(TableModel, self).__init__()
    self.table_data = table_data
  
  def rowCount(self, index):
    return len(self.table_data['cells'])
  
  def columnCount(self, index):
    if len(self.table_data['cells']) == 0:
      return 0
    return len(self.table_data['cells'][0])
  
  def data(self, index, role = Qt.ItemDataRole.DisplayRole):
    if role == Qt.ItemDataRole.DisplayRole:
      return self.table_data['cells'][index.row()][index.column()]
    return None
  
  def headerData(self, section, orientation, role):
    if role == Qt.ItemDataRole.DisplayRole:
      if orientation == Qt.Orientation.Horizontal:
        return str(self.table_data['columns'][section])
      if orientation == Qt.Orientation.Vertical and 'index' in self.table_data and  section < len(self.table_data['index']):
        return str(self.table_data['index'][section])
    return None
  


class DuplicateViewer(QWidget):
  def __init__(self, parent=None):
    super().__init__(parent)
    self.parent = parent
    self.files = duplicate_finder.duplicate_files
    self.parent.is_search_finished.connect(self.duplicate_files_changed)
    self.render()


  def duplicate_files_changed(self, value):
    if value:
      self.files = duplicate_finder.duplicate_files
      self.set_table_model()
  
  def set_table_model(self):
    column_names = ['Name', 'Path', 'Size']
    column_values = []

    for file in self.files:
      print(file.name, file.path, file.size)
      column_values.append([file.name, file.path, file.size])
    
    model = TableModel({
      'cells': column_values,
      'columns': column_names,
      })
    proxy_model = QSortFilterProxyModel(model)
    proxy_model.setSourceModel(model)
    self.table_view.setModel(proxy_model)

  def on_click_row(self, index):
    row = index.row()
    path = self.files[row].path
    print(row, path)
    subprocess.Popen(f'explorer "{path}"')

  def create_context_menu(self, pos):
    selected_model = self.table_view.selectionModel()
    if not selected_model or not selected_model.hasSelection():
      return
    selected_rows = selected_model.selectedRows()
    selected_rows = [row.row() for row in selected_rows]
  
    
    def call_action(action):
      for row in selected_rows:
        file = self.files[row]
        if action == 'open':
          file.open_file()
        if action == 'open_folder':
          file.open_file_folder()
        if action == 'delete':
          try:
            file.delete_file()
          except:
            pass
      
    context_menu = QMenu(self)
    context_menu.addAction('Open').triggered.connect(lambda: call_action('open'))
    context_menu.addAction('Open folder').triggered.connect(lambda: call_action('open_folder'))
    context_menu.addAction('Delete').triggered.connect(lambda: call_action('delete'))
    context_menu.exec(self.table_view.mapToGlobal(pos))
  
  def render(self):
    self.table_view = QTableView(self)
    self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    self.table_view.verticalHeader().setVisible(False)
    #self.table_view.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

    self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    self.table_view.customContextMenuRequested.connect(self.create_context_menu)
    
    self.table_view.doubleClicked.connect(lambda index: self.on_click_row(index))
    
    self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
    self.table_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
    self.table_view.setSortingEnabled(True)


    layout = QVBoxLayout()
    layout.addWidget(self.table_view)
    self.setLayout(layout)

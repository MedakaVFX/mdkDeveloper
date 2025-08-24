""" GUIメインアプリケーション

Version:
    * Created : v0.0.1 2025-08-24 Tatsuya YAMAGISHI
    * Coding : Python 3.11.9 & PySide6
    * Author : MEDAKA VFX <medaka.vfx@gmail.com>

Release Note:
    * v0.0.1 2025-08-24 Tatsuya YAMAGISHI
        * New
"""
DESCRIPTION = 'MDK Developer GUI Application'
NAME = 'mdkDeveloper'
VERSION = 'v0.0.2'


print(f'MDK | {NAME} {VERSION} : {DESCRIPTION} for Python')

#=======================================#
# import
#=======================================#
import glob
import logging
import os
import re
import shlex
import subprocess
import sys

from PySide6 import QtCore, QtGui, QtWidgets

sys.path.append(os.path.dirname(__file__)+'./libs')
import mdk_libs as mdk

#=======================================#
# Settings
#=======================================#
global logger

EXIF_OPTIONS = r'-overwrite_original -TagsFromFile'
FILE_FILTER_RAW = re.compile(r'.+\.(cr2|cr3|dng|cr2|cr3|dng|arw)')

GUI_BOLD_FONT = QtGui.QFont('BankGothic Md BT', 15)
GUI_HEADERS = {
    'Status': 100,
    'Path': 300,
}
GUI_WINDOW_SIZE = (1024, 600)

LIBRAW_OPTIONS=r'-v -w -o 0 -6 -W -g 2.2 0 -T'
URL_WEB = 'https://www.notion.so/mdkDeveloper-25926830759c80d784aceea922293257?v=1ec26830759c80389793000c4548293e'


#=======================================#
# Functions
#=======================================#
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    stream_handler = logging.StreamHandler()
    # stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(
        '[%(levelname)s][%(name)s][%(funcName)s:%(lineno)s]| MDK | %(message)s ')
    )
    logger.addHandler(stream_handler)

    return logger


#=======================================#
# Classes
#=======================================#
class MdkDeveloperCore:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.logger.info(f'> Initialize Core')

        self._raw_files = []

    def add_raw_files(self, paths: list[str]) -> None:
        
        _files = []

        for _path in paths:
            self.logger.info(f'path = {_path}')

            if os.path.isdir(_path):
                _paths = glob.glob(_path+'/**', recursive=True)
                _files = [_file for _file in _paths if FILE_FILTER_RAW.match(_file.lower())]
            else:
                if FILE_FILTER_RAW.match(_path.lower()):
                    _files.append(_path)

        self._raw_files.extend(_files)
        self.logger.info(f'> Added raw files: {_files}')

        self._raw_files = list(set(self._raw_files))


    def clear_raw_files(self) -> None:
        self._raw_files = []


    def develop(self, filepath: str) -> None:

        _filepath = filepath.replace('/', '\\')

        self.logger.info('> Develop')
        self.logger.info(f'File = {filepath}')

        # Libraw
        _libraw_cmds = f'dcraw_emu.exe {LIBRAW_OPTIONS} {_filepath}'
        self.logger.info(f'LibRaw Command: {_libraw_cmds}')

        _process = subprocess.Popen(_libraw_cmds, -1, stdout=subprocess.PIPE)
        _process.stdout.close()
        _process.wait()

        self.logger.info(f'LibRaw Process Return Code: {_process.returncode}')

        # ExifTool
        self.logger.info('> Copy Exif Data')
        _dst_filepath = _filepath+'.tiff'
        self.logger.info(f'DstFile = {_dst_filepath}')

        _args = ['exiftool.exe'] + shlex.split(EXIF_OPTIONS) + [_filepath] + [_dst_filepath]
        _process = subprocess.Popen(_args, -1, stdout=subprocess.PIPE)
        _process.stdout.close()
        _process.wait()
        self.logger.info(f'ExifTool Process Return Code: {_process.returncode}')

        return _dst_filepath

    def get_logger(self) -> logging.Logger:
        return self.logger

    def get_raw_files(self) -> list[str]:
        return self._raw_files

    def open_help_website(self) -> None:
        mdk.open_web(URL_WEB)


#=======================================#
# GUI Classes
#=======================================#
class DragAndDropWidget(QtWidgets.QWidget):
    def __init__(self, core: MdkDeveloperCore, parent=None):
        super().__init__(parent)

        self.core = core
        self.logger: logging.Logger = core.get_logger()


        self._label = QtWidgets.QLabel('Drag & Drop\nDirectory or Files')
        self._label.setAlignment(QtCore.Qt.AlignCenter)
        self._label.setFont(GUI_BOLD_FONT)

        self._main_layout = QtWidgets.QVBoxLayout(self)
        self._main_layout.addWidget(self._label)





class FileListItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, core: MdkDeveloperCore, filepath: str, parent=None):
        super().__init__(parent)

        self.core: MdkDeveloperCore = core
        self.logger: logging.Logger = core.get_logger()

        self._path: str = None
        self._status: str = 'Ready'

        self.set_path(filepath)


    def develop(self) -> str:
        _filepath = self.get_path()
        _dst_filepath = _filepath+'.tiff'

        self.logger.info(f'> Develop: {_filepath}')

        if os.path.exists(_dst_filepath):
            self.logger.warning(f'File already exists. Skip. {_dst_filepath}')
            self._status = 'Skipped'
        else:
            self.core.develop(_filepath)
            self._status = 'Done'


        self.update_ui()
        QtWidgets.QApplication.processEvents()


    def get_header_index(self, name: str) -> int:
        return self.treeWidget().get_header_index(name)
    

    def get_path(self) -> str:
        return self._path

    def set_path(self, value: str):
        self._path = value
        self.update_ui()


    def open_in_explorer(self):
        mdk.path.open_in_explorer(self.get_path())


    def update_ui(self):
        _index = self.get_header_index('Status')
        self.setText(_index, self._status)

        _index = self.get_header_index('Path')
        self.setText(_index, self.get_path())


class FileListWidget(mdk.qt.TreeWidget):
    def __init__(self, core, parent=None):
        super().__init__(parent)

        self.core = core
        self.logger: logging.Logger = core.get_logger()

        self.setSortingEnabled(True)
        self._init_context_menu()


    def _init_context_menu(self):
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._setup_context_menu)

    def _setup_context_menu(self, point):
        _menu = QtWidgets.QMenu(self)

        _action = _menu.addAction('Open in Explorer')
        _action.triggered.connect(self._on_open_in_explorer)

        _menu.addSeparator()

        _action = _menu.addAction('Clear')
        _action.triggered.connect(self._on_clear_list)


        _menu.exec(self.mapToGlobal(point))


    def _on_clear_list(self):
        self.core.clear_raw_files()
        self.refresh()

    def _on_open_in_explorer(self):
        _item = self.currentItem()
        if _item:
            _item.open_in_explorer()


    def add_files(self, files: list[str]) -> None:
        self.logger.info('> Add Files')
        
        for _file in files:
            _item = FileListItem(self.core, _file, self)

        _index = self.get_header_index('Path')
        self.sortByColumn(_index, QtCore.Qt.AscendingOrder)# DescendingOrder昇順降順


    def refresh(self):
        self.logger.info('> Refresh List Widget')
        self.clear()
        self.add_files(self.core.get_raw_files())



class MainWidget(QtWidgets.QWidget):
    def __init__(self, core: MdkDeveloperCore, parent=None):
        super().__init__(parent)
        self.core = core
        self.logger: logging.Logger = core.get_logger()

        self._init_ui()
        self._init_signals()


    def _init_signals(self):
        self._button_develop.clicked.connect(self._on_develop_clicked)

    def _init_ui(self):

        self.setAcceptDrops(True)

        
        self._drag_and_drop_widget = DragAndDropWidget(self.core, self)
        
        self._list_widget = FileListWidget(self.core, self)
        self._list_widget.set_headers(GUI_HEADERS)
        
        self._button_develop = QtWidgets.QPushButton('Develop')
        self._button_develop.setFont(GUI_BOLD_FONT)
        self._button_develop.setFixedHeight(40)

        self._stacked_widget = QtWidgets.QStackedWidget(self)
        self._stacked_widget.addWidget(self._drag_and_drop_widget)
        self._stacked_widget.addWidget(self._list_widget)

        self._main_layout = QtWidgets.QVBoxLayout(self)
        self._main_layout.addWidget(self._stacked_widget)
        self._main_layout.addWidget(self._button_develop)


    def _on_develop_clicked(self):
        self.logger.info('=========================================')
        self.logger.info('> Develop')
        self.logger.info('=========================================')
        _items = self._list_widget.get_all_items()

        if not _items:
            self.logger.warning('No files to develop')
            return
        
        else:
            for _item in _items:
                _item.develop()


    def dragEnterEvent(self,event):
        mime = event.mimeData()
        if mime.hasUrls() is True:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
    
    def dropEvent( self, event ):
        mimedata = event.mimeData()

        if mimedata.hasUrls():
            urllist = mimedata.urls()
            _paths = [re.sub('^/', '', url.path()) for url in urllist]
            self.core.add_raw_files(_paths)

            self._list_widget.refresh()
            self._stacked_widget.setCurrentIndex(1)
            


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, core: MdkDeveloperCore, parent=None) -> None:
        super().__init__(parent)

        self.core = core
        self.logger = core.get_logger()

        # Menu
        _help_menu: QtWidgets.QMenu = mdk.qt.create_menu(self, 'Help')
        _action = QtGui.QAction('Web', self)
        _action.triggered.connect(self.core.open_help_website)
        _help_menu.addAction(_action)

        # MainWidget
        self.ui = MainWidget(core)
        self.setCentralWidget(self.ui)
        
        # Status Bar
        _status_Bar = self.statusBar()

        self.resize(*GUI_WINDOW_SIZE)
        self.setWindowTitle(f'{NAME} {VERSION}')




#=======================================#
# Main
#=======================================#
if __name__ == "__main__":
    _logger = get_logger(__name__)
    _core = MdkDeveloperCore(_logger)


    _app = mdk.qt.get_application(darkcolor=True)
    _main_window = MainWindow(_core)
    _main_window.show()
    _app.exec()

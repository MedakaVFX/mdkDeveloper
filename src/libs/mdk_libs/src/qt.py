""" mdklibs.data
 
* データ管理用モジュール

Info:
    * Created : 2024-11-10 Tatsuya YAMAGISHI
    * Coding : Python 3.12.4 & PySide6
    * Author : MedakaVFX <medaka.vfx@gmail.com>


Release Note:
    * LastUpdated : 2025-08-24 Tatsuya Yamagishi
"""
import os
import pathlib
import re
import sys


try:
    from PySide6 import QtCore, QtGui, QtWidgets
except:
    from qtpy import QtCore, QtGui, QtWidgets
import qdarktheme


import mdk_libs as mdk
#=======================================#
# Settings
#=======================================#


#=======================================#
# Funcsions
#=======================================#
def create_menu(view, menu_name):
    _main_menu = view.menuBar()

    if _main_menu:
        _menu = get_menu_from_menubar(view.menuBar(), menu_name)

        if _menu:
            return _menu
        
        else:
            _menu = QtWidgets.QMenu(_main_menu)
            _menu.setTitle(menu_name)
            _main_menu.addAction(_menu.menuAction())

            return _menu
        
def get_application(darkcolor=True) -> QtWidgets.QApplication:
    """
    QApplication の取得
    """
    _app = QtWidgets.QApplication.instance()

    if _app is None:
        _app = QtWidgets.QApplication(sys.argv)

        if darkcolor:
            qdarktheme.setup_theme()

        return _app
    
    else:
        return None
    

def get_hspacer():
    _hspacer = QtWidgets.QSpacerItem(
        40, 20, 
        QtWidgets.QSizePolicy.Expanding,
        QtWidgets.QSizePolicy.Minimum
    )
    
    return _hspacer


def get_menu_from_menubar(menubar, menu_name):
    """
    メニューバーからメニューを名前で取得
    """
    _menus = menubar.findChildren(QtWidgets.QMenu)
    for _menu in _menus:
        if _menu.title() == menu_name:
            return _menu
        
    return None


def get_qaction(name: str, parent: QtWidgets.QWidget):
    """ Qt5、Qt6 互換用関数
    
    * QActionのパッケージ場所が Qt5(PySide2) と Qt6(PySide6) で異なるため
    """
    try:
        return QtGui.QAction(name, parent)
    except:
        return QtWidgets.QAction(name, parent)


def get_vspacer():
    _vspacer = QtWidgets.QSpacerItem(
        40, 20, 
        QtWidgets.QSizePolicy.Minimum,
        QtWidgets.QSizePolicy.Expanding
    )
    
    return _vspacer


def file_overwrite_dialog(parent=None):
    _result = QtWidgets.QMessageBox.information(
        parent, # Parent
        'Warning', # Title
        'The file already exists. Do you want to overwrite it?', # Massage
        QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel, # Button
        QtWidgets.QMessageBox.Save # Default
    )

    if _result == QtWidgets.QMessageBox.StandardButton.Save:
        return True
    elif _result == QtWidgets.QMessageBox.StandardButton.Discard:
        return False
    elif _result == QtWidgets.QMessageBox.StandardButton.Cancel:
        return False


def input_dialog(title, label, text='', parent=None ):    
    _result = QtWidgets.QInputDialog.getText(
                    parent, title, label, text=text)

    return _result



def warning_dialog(text, darkcolor=True, parent=None):
    _app = get_application(darkcolor=darkcolor)
    
    _result = QtWidgets.QMessageBox.information(
                    parent, 'Warning', text, )

    return _result


def file_already_waning_dialog(darkcolor=True, parent=None):
    _message = 'FIle is already exists.'
    return warning_dialog(
        _message,
        darkcolor=darkcolor,
        parent=parent
    )


def set_clipoboard_str(value: str):
    _qb = QtGui.QClipboard()
    _qb.setText(str(value))

#=======================================#
# Class
#=======================================#
class Splitter(QtWidgets.QSplitter):
    """ Splitter 基底クラス """
    def __init__(self, parent=None):
        super().__init__(parent)


    def init_print_signal(self):
        self.splitterMoved.connect(self.print_sizes)


    def print_sizes(self):
        print(f'{self.objectName()}:{self.sizes()}')
        set_clipoboard_str(self.sizes())
    

class HSplitter(Splitter):
    """ Vertical Splitter """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setOrientation(QtCore.Qt.Horizontal)


class VSplitter(Splitter):
    """ Horizontal Splitter """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setOrientation(QtCore.Qt.Vertical)


class ComboBox(QtWidgets.QComboBox):
    """ カスタムコンボボックス
    
    Signals:
        * activated(int index) : Only User
        * currentIndexChanged(int index) : Any
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    # ----------------------------------
    # Methods
    # ----------------------------------
    def select(self, name: str):
        """ 名前でアイテムを選択 """
        num = self.findText(name)
        if num == -1:
            num = 0
            
        self.setCurrentIndex(num)


    def set_font(self, font: QtGui.QFont):
        self.setFont(font)





class ListWidget(QtWidgets.QListWidget):
    """ TyListWidget 基底クラス 
    
    Attributes:
        setSortingEnabled(bool)
    
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSortingEnabled(True)

    # ----------------------------------
    # Get
    # ----------------------------------
    def get_all_items(self):
        return [self.item(index) for index in range(self.count())]


    def get_name_list(self) -> list[str]:
        return [item.text() for item in self.get_all_items()]


    def get_selected_name_list(self) -> list[str]:
        return [item.text() for item in self.selectedItems()]
    
    
    # ----------------------------------
    # Set
    # ----------------------------------
    def set_editable(self):
        for _index in range(self.count()):
            _item = self.item(_index)
            _item.setFlags(_item.flags() | QtCore.Qt.ItemIsEditable)


    def set_multi_selection(self):
        self.setSelectionMode(
		        QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        

    # ----------------------------------
    # Methods
    # ----------------------------------
    def add_items(self, items: list[str]):
        self.clear()
        self.addItems(items)
    
    
    def append_items(self, items: list[str]):
        _name_list = self.get_name_list()
        _name_list.extend(items)

        self.clear()
        self.addItems(sorted(list(set(_name_list))))


    def item_exists(self, value: str):
        if self.find_items(value):
            return True
        else:
            return False


    def find_items(self, value:str):
        """
        Reference form : https://doc.qt.io/qtforpython-5/PySide2/QtCore/Qt.html

        Qt.MatchExactly : Performs QVariant -based matching.
        Qt.MatchFixedString : Performs string-based matching. String-based comparisons are case-insensitive unless the MatchCaseSensitive flag is also specified.
        Qt.MatchContains : The search term is contained in the item.
        Qt.MatchStartsWith : The search term matches the start of the item.
        Qt.MatchEndsWith : The search term matches the end of the item.
        Qt.MatchCaseSensitive : The search is case sensitive.
        Qt.MatchRegExp : Performs string-based matching using a regular expression as the search term. Uses the deprecated QRegExp class. This enum value is deprecated since Qt 5.15.
        Qt.MatchRegularExpression : Performs string-based matching using a regular expression as the search term. Uses QRegularExpression . When using this flag, a QRegularExpression object can be passed as parameter and will directly be used to perform the search. The case sensitivity flag will be ignored as the QRegularExpression object is expected to be fully configured. This enum value was added in Qt 5.15.
        Qt.MatchWildcard : Performs string-based matching using a string with wildcards as the search term.
        Qt.MatchWrap : Perform a search that wraps around, so that when the search reaches the last item in the model, it begins again at the first item and continues until all items have been examined.
        Qt.MatchRecursive : Searches the entire hierarchy.
        """

        return self.findItems(value, QtCore.Qt.MatchCaseSensitive)
            

    def remove_selected(self):
        _items = self.selectedItems()

        if _items is None:
            return
        
        for _item in _items:
            self.takeItem(self.row(_item))


    def select(self, item_name):
        """ Select item by name. """
        # print(item_name)
        # raise RuntimeError(item_name)

        _items = (self.findItems(item_name, QtCore.Qt.MatchContains))           
        if _items:
            self.setCurrentItem(_items[0])




class FileListWidgetItem(QtWidgets.QListWidgetItem):
    """ ファイルリストアイテム """
    def __init__(self, filepath: str, parent=None):
        super().__init__(parent)

        self._value = None

        self.set_value(filepath)

    #---------------------------------#
    # Get
    #---------------------------------#
    def get_value(self):
        return self._filepath

    #---------------------------------#
    # Set
    #---------------------------------#
    def set_value(self, value: str):
        self._filepath = value

        if value:
            self.setText(os.path.basename(value))



class FileListWidget(ListWidget):
    """ ファイルリストウィジェット """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSortingEnabled(True)

    #---------------------------------#
    # Methods
    #---------------------------------#
    def add_items(self, items: list[str]):
        """
        Args:
            items (list[str]): ファイルパスリスト
        """
        self.clear()
        
        for _item in items:
            _new_item = FileListWidgetItem(_item)
            self.addItem(_new_item)


    def enable_file_drag_and_drop(self):
        self.setAcceptDrops(True)


    def dragEnterEvent(self, event):
        """ ドラッグされたオブジェクトがファイルなら許可する """
        mime = event.mimeData()

        if mime.hasUrls() == True:
            event.accept()
        else:
            event.ignore()

    def dropEvent( self, event ):
        mimedata = event.mimeData()

        if mimedata.hasUrls():
            urllist = mimedata.urls()
            files = [re.sub('^/', '', url.path()) for url in urllist]			
            self.add_items(files)

   
    def dragMoveEvent(self, event):
        """ ドロップアクション設定 """
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()


    def get_all_filepath_list(self) -> list[str]:
        return [item.get_filepath() for item in self.get_all_items()]


    def get_selected_filepath_list(self) -> list[str]:
        return [item.get_filepath() for item in self.selectedItems()]


    def remove_selected(self):
        _items = self.selectedItems()

        if _items is None:
            return
        
        for _item in _items:
            self.takeItem(self.row(_item))


    def select(self, item_name):
        """ Select item by name. """
        _items = (self.findItems(item_name, QtCore.Qt.MatchContains))           
        if _items:
            self.setCurrentItem(_items[0])



class Imagelabel(QtWidgets.QLabel):
    """ イメージラベル """

    def __init__(self, text='Image', parent=None):
        super().__init__(parent)

        # Private Variables
        self._imagefile: str = None
        self._height: int = 160
        self._width: int = 90

        self.setText(text)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setAutoFillBackground(False)
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setLineWidth(3)

    #---------------------------------#
    # Get
    #---------------------------------#
    def get_height(self) -> int:
        return self._height
    
    def get_width(self):
        return self._width
    
    #---------------------------------#
    # Set
    #---------------------------------#       
    def set_height(self, value: int):
        self._height = int(value)


    def set_imagefile(self, filepath: str):
        self._imagefile = filepath

        if (filepath is not None) and (os.path.exists(filepath)):
            qimage = QtGui.QImage(filepath)
            pixmap = QtGui.QPixmap(
                qimage.scaledToWidth(self.get_width(), mode=QtCore.Qt.SmoothTransformation))
            self.setPixmap(pixmap)


    def set_line_width(self, value: int):
        self.setLineWidth(value)


    def set_size(self, width: int, height: int):
        self.set_width(width)
        self.set_height(height)

        self.setFixedSize(width, height)
        # self.setFixedSize(width+4, height+4)


    def set_text(self, value: str):
        self.setText(str(value))


    def set_width(self, value: int):
        self._width = int(value)






class ProgressDialog(QtWidgets.QProgressDialog):
    def __init__(self, logger=None, parent=None):
        # super().__init__(spp, parent)

        super().__init__(parent)
        self.logger = logger

        self.total_steps = None
        self.steps = 0
        self.setMaximum(100)

        self.setAutoReset(False)
        self.setAutoClose(False)

    # ----------------------------------
    # Get
    # ----------------------------------
    @staticmethod
    def get(title: str, view: QtWidgets.QWidget, total_steps: int, width=400, height=150, logger=None):
        """
        プログレスバーの取得
        """
        pbar = ProgressDialog(logger=logger, parent=view)
        pbar.setWindowTitle(title)
        pbar.set_total_steps(total_steps)
        pbar.setFixedSize(width, height)
        pbar.open()

        QtWidgets.QApplication.processEvents()

        return pbar
    
    # ----------------------------------
    # Set
    # ----------------------------------
    def set_label(self, label):
        self.setLabelText(f'[{self.steps+1}/{self.total_steps}]\n{label}')


    def set_total_steps(self, value: int):
        self.total_steps = value

    # ----------------------------------
    # Methods
    # ----------------------------------
    def add_steps(self, value: int):
        self.steps += value

        self.setValue((self.steps/self.total_steps)*100)



class SnapShot(QtWidgets.QWidget):
    def __init__(self, filepath, app_name:str=None, size: tuple=None, parent=None):
        super().__init__(parent)

        self.path: pathlib.Path = pathlib.Path(filepath)
        self.path.parent.mkdir(parents=True, exist_ok=True)    
        self.image_size: tuple = size
        screen = QtWidgets.QApplication.primaryScreen()

        if app_name == 'nuke':
            # PySide2 対応
            self.originalPixmap = QtGui.QPixmap.grabWindow(
                        QtWidgets.QApplication.desktop().winId())
        else:
            # self.originalPixmap = screen.grabWindow(QtWidgets.QApplication.desktop().winId())
            self.originalPixmap = screen.grabWindow(0)

            
        self.endpos = None
        self.stpos = None

    # ----------------------------------
    # Get / Set
    # ----------------------------------
    def get_path(self):
        return self.path.as_posix()


    def get_image_size(self):
        return self.image_size

    # ----------------------------------
    # Methods
    # ----------------------------------
    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setPen(QtCore.Qt.NoPen)

        # rectSize = QtWidgets.QApplication.desktop().screenGeometry()
        rectSize = QtWidgets.QApplication.primaryScreen().geometry()
        painter.drawPixmap(rectSize, self.originalPixmap)

        if self.endpos and self.stpos:

            painter_path = QtGui.QPainterPath()
            painter_path.addRect(rectSize)
            try:
                painter_path.addRoundRect(QtCore.QRect(self.stpos, self.endpos), 0, 0)
            except:
                painter_path.addRoundedRect(QtCore.QRect(self.stpos, self.endpos), 0, 0)

            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 100, 100)))
            painter.drawPath(painter_path)

        painter.end()


    def mouseMoveEvent(self, event):
        self.endpos = event.pos()
        self.repaint()


    def mousePressEvent(self, event):
        self.stpos = event.pos()


    def mouseReleaseEvent(self, event):
        self.endpos = event.pos()
        self.screenShot()


    def screenShot(self):
        filepath = self.get_path()
        size = self.get_image_size()


        pixmap = self.originalPixmap.copy(QtCore.QRect(self.stpos, self.endpos))
        # if size:
        #     pixmap = pixmap.scaled(size[0], size[1], QtCore.Qt.KeepAspectRatio) 
        
        pixmap.save(filepath)
        print('snapshot = {}'.format(filepath))
        

        self.close()





class FixedHeightDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, height, parent=None):
        super().__init__(parent)
        self.fixed_height = height


    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        return QtCore.QSize(size.width(), self.fixed_height)


class TreeWidget(QtWidgets.QTreeWidget):
    """Class Description
 
    * カスタムTreeWidget

    Signals:
        * currentItemChanged
        * itemClicked
        * itemDoubleClicked
        *  itemPressed

    Examples:
        >>> self.setAlternatingRowColors(True)
        >>> self.setRootIsDecorated(False)
        >>> self.setSortingEnabled(True)
        >>> self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        >>> 
        >>> self.setColumnCount(len(TASK_HEADERS))
        >>> self.setHeaderLabels(list(TASK_HEADERS))
        >>> 
        >>> for i, key in enumerate(TASK_HEADERS):
        >>>     self.header().resizeSection(i, TASK_HEADERS.get(key))
        >>> setSelectionMode(
        >>>     QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

    """
    def __init__(self, parent=None) -> None:

        super().__init__(parent)

        self._headers = None
        
    #---------------------------------#
    # Init
    #---------------------------------#
    #---------------------------------#
    # Setup
    #---------------------------------#
    #---------------------------------#
    # Get
    #---------------------------------#
    def get_all_items(self):
        # all_items = self.findItems(
        #         '*', QtCore.Qt.MatchWrap |QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive,)

        # return all_items
    
        """Returns all QTreeWidgetItems in the given QTreeWidget."""
    
        _all_items = []
        for _i in range(self.topLevelItemCount()):
            _top_item = self.topLevelItem(_i)
            _all_items.extend(self.get_subtree_items(_top_item))
        
        return _all_items
    

    def get_header_index(self, name: str):
        if self._headers:
            for _i, key in enumerate(self._headers):
                if key == name:
                    return _i
            return None
        else:
            return None
    

    def get_item(self, index, name, create=True):
        """ Item を名前で取得 """
        _items = self.get_all_items()
        _result = None

        for _item in _items:
            if _item.text(index) == name:
                _result = _item

        if _result is None and create:
            _result = QtWidgets.QTreeWidgetItem(self)
            _result.setText(0, name)

        return _result
               

    def get_subtree_items(self, tree_widget_item):
        """Returns all QTreeWidgetItems in the subtree rooted at the given node."""
    
        _items = []
        _items.append(tree_widget_item)
        for i in range(tree_widget_item.childCount()):
            _items.extend(self.get_subtree_items(tree_widget_item.child(i)))
        
        return _items


    def get_top_item(self, name):
        _num = self.topLevelItemCount()
        _result = None

        if _num:
            for i in range(_num):
                _item = self.topLevelItem(i)
                if _item.text(0) == name:
                    _result = _item
                    break
        
        return _result


    #---------------------------------#
    # Set
    #---------------------------------#
    def set_fixed_height(self, value: int):
        """ TreeWidgetItemの高さを固定
        
        """
        _delegate = FixedHeightDelegate(value)
        self.setItemDelegate(_delegate)


    def set_font(self, font: QtGui.QFont):
        self.setFont(font)


    def set_headers(self, headers: dict):
        """ 辞書型でヘッダーを設定

        headers = {
            'Type:': <header_width: int>,
        }

        """
        self._headers = headers

        self.setColumnCount(len(headers))
        self.setHeaderLabels(headers)

        for _i, _key in enumerate(headers):
            self.header().resizeSection(_i, headers.get(_key)) 


    def set_multi_selection(self):
        self.setSelectionMode(
                QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)


    #---------------------------------#
    # Methods
    #---------------------------------#
    def add_item(self, name: str, parent=None):
        if parent is None:
            _parent = self
        else:
            _parent = self.get_item(0, parent, create=True)


        _item = QtWidgets.QTreeWidgetItem(_parent)
        _item.setText(0, name)

        return _item


    def add_items(self, items: list):
        self.clear()

        if type(items) == list:
            for _item in items:
                _new_item = QtWidgets.QTreeWidgetItem(self)
                _new_item.setText(0, _item)


    def hide_header(self):
        self.header().hide()


    def remove_selected(self):
        _items = self.selectedItems()

        for _item in _items:
            _index = self.indexFromItem(_item)
            self.takeTopLevelItem(_index.row())


    def select(self, index, name):        
        _cur_item = self.get_item(index, name, create=False)

        if _cur_item:
            self.setCurrentItem(_cur_item)




class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    
    def get_tab_text(self):
        _index = self.currentIndex()
        return self.tabText(_index)
    

    def select(self, name: str):
        for _i in range(self.count()):
            try:
                if self.tabText(_i).lower() == name.lower():
                    self.setCurrentIndex(_i)
            except:
                pass


#=======================================#
# QtTools
#=======================================#
class DictEditWidget(TreeWidget):
    """ 辞書型データ編集用TreeWidget
 
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.HEADERS = {'Key': 160, 'Value': 0}

        self.setSortingEnabled(True)
        self.setAlternatingRowColors(False)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.setRootIsDecorated(False)

        self.setColumnCount(len(self.HEADERS))
        
        self.set_headers(self.HEADERS)


    #---------------------------------#
    # Init Context Menu
    #---------------------------------#
    def init_context_menu(self):
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._setup_context_menu)


    def _setup_context_menu(self, point):
        _menu = QtWidgets.QMenu(self)

        _action = QtGui.QAction('Add new', self)
        _action.triggered.connect(self._on_add_new)
        _menu.addAction(_action)

        _menu.exec_(self.mapToGlobal(point))

    
    #---------------------------------#
    # Methods
    #---------------------------------#
    def _on_add_new(self):
        self.add_item('key', 'value')

    #---------------------------------#
    # Get
    #---------------------------------#
    def get_value(self):
        return {item.text(0): item.text(1) for item in self.get_all_items()}


    #---------------------------------#
    # Set
    #---------------------------------#
    def set_value(self, data: dict):
        self.clear()

        if type(data) == dict:

            for key, value in data.items():
                self.add_item(key, value)

        else:
            _message = 'MDK | "data" type is not dict.'
            print(_message)
            print(data)


    #---------------------------------#
    # Method
    #---------------------------------#
    def add_item(self, key: str, value: str):
        item = QtWidgets.QTreeWidgetItem(self)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

        item.setText(0, str(key))
        if value is not None:
            item.setText(1, str(value))




if __name__ == '__main__':
    pass

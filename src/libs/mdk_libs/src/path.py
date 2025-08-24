""" mdklibs.path
 
* path管理用モジュール
* ファイルパスは基本的にposix_pathで処理

Info:
    * Created : 2024-11-07 Tatsuya YAMAGISHI
    * Coding : Python 3.12.4 & PySide6
    * Author : MedakaVFX <medaka.vfx@gmail.com>

Release Note:
    * LastUpdated : 2025-08-24 Tatsuya Yamagishi
"""
import datetime
import glob
import os
import pathlib
import platform
import pprint
import re
import subprocess
import shutil


import mdk_libs as mdk

#=======================================#
# Settings
#=======================================#
FILE_FILTER_USD = re.compile(r'.+\.(usd|usdc|usda)')
FILE_FILTER_IMAGE = re.compile(r'.+\.(bmp|gif|png|jpeg|jpg|svg|tif|tiff|exr)')
FILE_FILTER_IMAGE_SDR = re.compile(r'.+\.(bmp|gif|png|jpeg|jpg|svg|tif|tiff)')
# FILE_FILTER_IMAGE = re.compile(r'.+\.(bmp|gif|png|jpeg|jpg|svg|tif|tiff)')
FILE_FILTER_MAYA = re.compile(r'.+\.(ma|mb)')
FILE_FILTER_MEDIA = re.compile(r'.+\.(bmp|png|jpeg|jpg|svg|tif|tiff|exr|mp4|mp3|pdf|mov|mkv)')
FILE_FILTER_RAW = re.compile(r'.+\.(cr2|cr3|dng|cr2|cr3|dng|arw)')
FILE_FILTER_TEXT = re.compile(r'.+\.(doc|txt|text|json|py|usda|nk|sh|zsh|bat|md)')



#=======================================#
# Funcsions
#=======================================#
def as_posix(filepath: str) -> str:
    """ 
    Args:
        filepath(str): ファイルパス

    Retuns:
        str : posix_path
    """

    return pathlib.Path(filepath).as_posix()


def get_current_version_num(filepath) -> int:
    """

    <filepath> から現在のバージョン番号を取得（最大のバージョン番号）
    
    * 同じ階層内のバージョンを探索
    * ファイルパスの最後のバージョンをバージョンNoとして使用。

    Args:
        filepath (:obj:`str or pathlib.Path`): ファイルパス

    Returns:
        int: 現在のバージョン番号

    Raises:
        例外の名前: 例外の説明 (例 : 引数が指定されていない場合に発生 )

    Examples: 
        >>> mdk.path.get_new_version('Y:/test_project/assets/v001/CharaB_Model_v001.dat')
        4

    Note:
        * ファイルパスに複数バージョンが含まれる場合、一番大きなバージョンが最大のバージョンとして扱われる。

    """
    _versions = get_versions(filepath)

    if _versions:
        _items = filepath.split(_versions[-1])
        _filepath_list = glob.glob(_items[0]+'v*')
        # result = get_version_num(filelist[-1])

        # --------
        # Updated 2024/03/12
        _version_list = [ get_version_num(_filepath)  for _filepath in _filepath_list]
        if _version_list:
            return max(_version_list)
        else:
            return 0

    else:
        return 0



def get_current_version_path(filepath) -> str:
    """

    <filepath> から最新のバージョンパスを生成

    Args:
        filepath (:obj:`str or pathlib.Path`): ファイルパス

    Returns:
        str: 最新のバージョンパス

    Raises:
        例外の名前: 例外の説明 (例 : 引数が指定されていない場合に発生 )

    Examples: 
        >>> mdk.path.get_new_version('Y:/test_project/assets/v001/CharaB_Model_v001.dat')
        `Y:/test_project/assets/v002/CharaB_Model_v002.dat`

    Note:
        * ファイルパスに複数バージョンが含まれる場合、一番大きなバージョンが最大のバージョンとして扱われる。

    """
    _cur_num = get_current_version_num(filepath)
    _src_num = get_version_num(filepath)
    
    return version_up(filepath, _cur_num - _src_num)


def get_new_version_path(filepath, up_num=1) -> str:
    """

    <filepath> から最新のバージョンパスを生成

    Args:
        filepath (:obj:`str or pathlib.Path`): ファイルパス

    Returns:
        str: 最新のバージョンパス

    Raises:
        例外の名前: 例外の説明 (例 : 引数が指定されていない場合に発生 )

    Examples: 
        >>> tylibs.path.get_new_version('Y:/test_project/assets/v001/CharaB_Model_v001.dat')
        `Y:/test_project/assets/v002/CharaB_Model_v002.dat`

    Note:
        * ファイルパスに複数バージョンが含まれる場合、一番大きなバージョンが最大のバージョンとして扱われる。

    """
    latest_version = get_current_version_path(filepath)   
    result = version_up(latest_version)
        
    return result


def get_version(filepath):
    versions = get_versions(filepath)

    if versions:
        return versions[-1]
    
    

def get_version_num(filepath):
    """

    <filepath> からバージョン番号を取得（最大のバージョン番号）
        - パスにバージョンが複数含まれる場合は最大値を取得

    Args:
        filepath (:obj:`str or pathlib.Path`): ファイルパス

    Returns:
        int: 現在のバージョン番号

    Raises:
        例外の名前: 例外の説明 (例 : 引数が指定されていない場合に発生 )

    Examples: 
        >>> mdk.path.get_new_version('Y:/test_projectv002/assets_V01/v003/CharaB_Model_v0004.v001.dat')
        4

    Note:
        * ファイルパスに複数バージョンが含まれる場合、一番大きなバージョンが最大のバージョンとして扱われる。

    """
    return max(int(_version[1:]) for _version in get_versions(filepath))


def get_versions(filepath) -> list:
    """
    <filepath> に含まれるバージョンを全て取得

    Args:
        filepath (:obj:`str or pathlib.Path`): ファイルパス

    Returns:
        list: バージョンリスト

    Raises:
        例外の名前: 例外の説明 (例 : 引数が指定されていない場合に発生 )

    Examples: 
        >>> mdk.path.get_new_version('Y:/test_project/assets/v003/CharaB_Model_v0004.v001.dat')
        ['v003', 'v0004', 'v001']
        >>> mdk.path.get_new_version('Y:/test_projectv002/assets_V01/v003/CharaB_Model_v0004.v001.dat')
        ['v003', 'v0004', 'v001']

    Note:
        * バージョンは `._/` で区切られ、小文字の `v` から始まる数字の連続

    """
    if type(filepath) == str:
        _path = as_posix(filepath)
        _items = re.split(r'[._/]+', _path)
        _result = [_item for _item in _items if re.match(r'(v\d+)', _item)]

        return _result



def mapping(path_substitutions: list[dict], filepath: str):
    """ Filepath をマッピングする。

    Examples:
        >>> PATH_SUBSTITUTIONS = [
        >>> {
        >>>     'Darwin': '.zsh',
        >>>     'Linux': '.sh',
        >>>     'Windows': '.bat',
        >>> },
        >>> {
        >>>     'Darwin': '/Volumes/KHAKI-SHARE',
        >>>     'Linux': '/mnt/KHAKI-SHARE',
        >>>     'Windows': 'X:',
        >>> },
    """
    _platform = platform.system()

    for _path_dict in path_substitutions:
        _linux_path = _path_dict.get('Linux')
        _mac_path = _path_dict.get('Darwin')
        _windows_path = _path_dict.get('Windows')

        if _platform == 'Darwin':
                filepath = filepath.replace(_linux_path, _mac_path).replace(_windows_path, _mac_path)
        elif _platform == 'Linux':
            filepath = filepath.replace(_mac_path, _linux_path).replace(_windows_path, _linux_path)
        elif _platform == 'Windows':
            filepath = filepath.replace(_mac_path, _windows_path).replace(_linux_path, _windows_path)


    return filepath


def mkdir(filepath: str, parents: bool = True, exists_ok: bool = True):
    pathlib.Path(filepath).mkdir(
            exist_ok=exists_ok,
            parents=parents,
    )


def move(src, dst):
    """ ファイル移動 """
    if os.path.isfile(src):
        dst_dir = os.path.dirname(dst)

        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

    shutil.move(src, dst)

    

def name(filepath: str) -> str:
    return pathlib.Path(filepath).name


def open_dir(filepath) -> None:
    """
    フォルダを開く
    """
    _filepath = pathlib.Path(filepath)
    OS_NAME = platform.system()

    if _filepath.exists():
        if _filepath.is_file():
            _filepath = _filepath.parent

        if OS_NAME == 'Windows':
            cmd = 'explorer {}'.format(str(_filepath))
            subprocess.Popen(cmd)

        elif OS_NAME == 'Darwin':
            subprocess.Popen(['open', _filepath])

        else:
            subprocess.Popen(["xdg-open", _filepath])



def parent(filepath: str) -> str:
    _path = Path(filepath)
    
    return _path.parent().get_value()


def open_in_explorer(filepath: str):
    """
    Explorerでフォルダを開く
    """
    if os.path.exists(filepath):
        if platform.system() == 'Windows':
            filepath = str(filepath)
            filepath = filepath.replace('/', '\\')

            filebrowser = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
            subprocess.run([filebrowser, '/select,', os.path.normpath(filepath)])
        
        elif platform.system() == 'Darwin':
            subprocess.call(['open', filepath])
        
        else:
            subprocess.Popen(["xdg-open", filepath])
    else:
        raise FileNotFoundError(f'File is not found.')


def split(filepath: str) -> tuple:
    """ Split a file path into root, basename, and extension. 
    
    Examples:
        >>> mdk.path.split(r'/mnt/users/yamagishi.txt')
        >>> ('/mnt/users', 'yamagishi', 'txt')
    """
    _root, _filename = os.path.split(filepath)
    _basename, _ext = os.path.splitext(_filename)

    return _root, _basename, _ext


def stem(filepath: str) -> str:
    return pathlib.Path(filepath).stem


def suffix(filepath: str):
    return pathlib.Path(filepath).suffix


def version_up(filepath, num: int=1) -> str:
    """

    `filepath` の バージョンを `num` 分加算する
    
    * マイナスも対応しているが、トータルが0以下になるとバグると思う。

    Args:
        filepath (:obj: `str or pathlib.Path`): ファイルパス
        num (:obj:`int`, num=1): カウントアップ数。

    Returns:
        str: カウントアップしたパス

    Examples: 
        >>> path = 'Y:/test_projectv002/assets_V01/v003/CharaB_Model_v0004.v001.dat'
        >>> mdk.path.version_up(path, num = 2)
        `Y:/test_projectv002/assets_V01/v005/CharaB_Model_v0006.v003.dat`
        >>> path = 'Y:/test_projectv002/assets_V01/v003/CharaB_Model_v0004.v001.dat'
        >>> mdk.path.version_up(path, num = -1)
        `Y:/test_projectv002/assets_V01/v002/CharaB_Model_v0003.v000.dat`
    Note:
        注意事項などを記載

    """
    _path = as_posix(filepath)
    _versions = get_versions(_path)

    _result = _path
    
    for _version in _versions:
        _pad = len(_version[1:])
        _count = int(_version[1:])

        _new_version = 'v' + str(max(0, _count+num)).zfill(_pad)
        _result = _result.replace(_version, _new_version)

    return _result






#=======================================#
# Class
#=======================================#
class Path:
    """ パス管理用モジュール 
    
    * Expression 機能
    * pathlib.Pathがあるが、関数の仕様が思った通りで無い事もあり、専用のパス管理クラスを実装
    * パスはposix_pathで管理

    Attributes:
        _value(str): ファイルパス
        _variables(list[str]): 変数管理用

    """

    def __init__(self, filepath: str=None, mkdir: bool=False) -> None:
        """
        
        Args:
            filepath(str): ファイルパス
            mkdir(bool): ディレクトリが無ければ作成
        
        """
        # Settings
        self._EXPR_FILTER = re.compile(r'{([@&$\w]+)}')
        self._EXEC_FILTER = re.compile(r'%(.*?)%')


        # ファイルパス管理変数
        self._exprs: list = []
        self._value: str = None # パスの値管理用
        self._vars: dict = {} # 変数管理用
        self._version_digits = 3
        

        # ファイルパスをセット
        if filepath:
            self.set_value(filepath)


        # ディレクトリ作成
        if mkdir is True:
            pathlib.Path(self.get_value()).mkdir(parents=True, exist_ok=True)


    def __str__(self):
        return f'Class <mdklibs.Path>: {self.get_value()}'
    


    def add_dir(self, dirname: str) -> None:
        """ フォルダを追加する 
        
        Args:
            dirname(str): 追加するディレクトリ名

        """
        if os.path.isdir(self.get_value()):

            if dirname:
                pathlib.Path(f'{self.get_value()}/{dirname}').mkdir(parents=True, exist_ok=True)
            else:
                raise ValueError(f'dirname = {dirname}')
            
        else:
            print(f'filepath={self.get_value()}')
            raise TypeError(f'"filepath" is not directory.')


        

    def delete(self):
        mdk.file.delete(self.get_value())


    def delete_files(self):
        """ ファイルパス内の全てのファイルを削除 """
        if self.exists():
            _folder_path = self.get_value()

            # フォルダ内のファイルを取得
            _files = os.listdir(_folder_path)

            # 各ファイルを削除
            for _file_name in _files:
                _file_path = os.path.join(_folder_path, _file_name)

                try:
                    if os.path.isfile(_file_path):
                        os.unlink(_file_path)

                    # もしファイルがディレクトリなら再帰的に削除        
                    elif os.path.isdir(_file_path):
                        shutil.rmtree(_file_path)

                except Exception as e:
                    print(f"ファイル {_file_path} を削除中にエラーが発生しました: {e}")



    def exec_cmd(self, path):

        _exec_list = self._EXEC_FILTER.findall(path)
        
        for _cmd in _exec_list:
            _func = getattr(self, _cmd)
            _result = _func(path)
            
        return _result
    


    def eval(self, *args):
        """
        Expressionの評価
        """
        # print('Path.eval')
        _result = self.eval_expression(*args)

        if self._EXEC_FILTER.findall(_result):
            _result = self.exec_cmd(_result)

        return _result
        

    def eval_expression(self, *args):
        """
        Expressionの評価
        """
        _context_path = args[0]
        _items = self._EXPR_FILTER.findall(_context_path)
        _cmds = list(set(_items))
        

        for _cmd in _cmds:
            try:
                _result = self.eval_command(_cmd, *args[1:])
            except Exception as ex:
                print(f'cmd = {_cmd}')
                print(f'args = {args}')

                raise RuntimeError(ex)

            _src = '{'+_cmd+'}'
            _dst = str(_result)

            _context_path = _context_path.replace(_src, _dst)

        return _context_path




    def eval_command(self, *args) -> str:
        """Description

        * コマンドの評価メイン関数。
 
        Args:
            *args (*args): 可変長引数。第一引数はfile_path。コマンドによって引数は異なる。
 
        Returns:
            str: 生成されたファイルパス。
        """
        _cmd = args[0]
        _result = _cmd

        if _cmd.startswith('@'):
            _expr = self.get_expr(_cmd[1:])
            _result = self.eval_expression(_expr)

        elif _cmd.startswith('&'):
            expr = self._exprs.get(_cmd[1:])
            _result = self.eval_expression(expr)

        elif _cmd.isdigit():
            _result = args[int(_cmd)]

        elif _cmd == 'YYYY':
            dt = datetime.datetime.today()
            _result = dt.strftime('%Y')
            
        elif _cmd == 'YY':
            dt = datetime.datetime.today()
            _result = dt.strftime('%y')

        elif _cmd == 'MM':
            dt = datetime.datetime.today()
            _result = dt.strftime('%m')

        elif _cmd == 'DD':
            dt = datetime.datetime.today()
            _result = dt.strftime('%d')

        elif re.match('[0-9A-Z]+', _cmd):
            try:
                _result = self.get_var(_cmd)

            except Exception as ex:
                raise ValueError(ex)


            if not _result:
                _result = 'None'
                _message = f'Command "{_cmd}" is not found.'

                raise ValueError(_message)

        else:
            _func = getattr(self, _cmd)
            _result = _func(*args[1:])

        
        self.set_value(_result)

        return as_posix(_result)
    


    def exists(self) -> bool:
        """ ファイルが存在するかどうか？ """
        return os.path.exists(self.get_value())
    

    def get_expr(self, key):
        return self._exprs[key]
    

    def get_exprs(self) -> dict:
        return self._exprs
    

    def get_path(self, key: str, *args):
        _expr = self.get_expr(key)
        try:
            return self.eval(_expr, *args)
        
        except Exception as ex:
            print(f'key=  "{key}"')
            print(f'expr = "{_expr}"')
            print('vars =')
            pprint.pprint(self._vars)
            print(self._exprs)
            raise KeyError(ex)
    
    

    def get_var(self, key: str):
        # print(f'key = {key}: {self._vars}')
        # print(self._vars.get(key))
        return self._vars.get(key)


    def get_value(self) -> str:
        """ パスを取得 """
        return self._value
    

    def get_vars(self) -> dict:
        """ 変数を返す """
        return self._vars
    

    def get_version_digits(self) -> int:
        return self._version_digits
    

    def is_file(self) -> bool:
        """ ファイル判定 """
        return os.path.isfile(self.get_value())
    

    def is_dir(self) -> bool:
        """ ディレクトリ判定 """
        return os.path.isdir(self.get_value())
    

    def join(self, value: str) -> str:
        return Path(f'{self.get_value()}/{value}')


    def listdir(self, ext=None, is_file=False, is_dir=False) -> list:
        """ ディレクトリ内のファイルリストを返す """
        if self.exists() and self.is_dir():
            result = [Path(_path.as_posix())  for _path in pathlib.Path(self.get_value()).iterdir()
                if not _path.name.startswith('.')
                if not _path.name.endswith('.nk~')
                if not _path.name.endswith('.autosave')
            ]

            if is_file:
                return [_filepath for _filepath in result if _filepath.is_file()]

            elif is_dir:
                return [_filepath for _filepath in result if _filepath.is_dir()]
            
            elif ext:
                return [_filepath for _filepath in result if _filepath.get_value().endswith(ext)]
            
            else:
                return result
            
        else:
            return []
        

    def load_json(self):
        _filepath = self.get_value()
        
        return mdk.file.load_json(_filepath)
    
        
    def mkdir(self, parents=True, exists_ok=True):
        """ ディレクトリ作成 """
        mkdir(self.get_value(), parents=parents, exists_ok=exists_ok)


    def name(self):
        return name(self.get_value())
    

    def new_version(self, path):
        """ 新規バージョンパスを取得
        
        Args:
            path(str): 置き換える前のパス
        """
        _version_digits = self.get_version_digits()
        _version = 'v'+str(0).zfill(_version_digits)
        _path = path.replace(r'%new_version%', _version)

        return get_new_version_path(_path)
        

    def open_dir(self) -> None:
        open_dir(self.get_value())


    def parent(self) -> object:
        """ 親ディレクトリパスを返す """
        return Path(os.path.dirname(self.get_value()))
    

    def parse_string_to_dict(self, expr, value) -> dict:
        # exprの {} を除去
        _temp = re.sub(r'{|}', '', expr)
        
        # 辞書型のKEYとなるリストを作成
        _key_list = _temp.split('_')
        
        # 辞書型のVALUEとなるリストを作成
        _value_list = value.split('_')
        
        # ２つのリストから辞書を作成
        return dict(zip(_key_list, _value_list))


    def replace_text(self, replace_list: list[str]):
        mdk.file.replace_text(self.get_value(), replace_list)


    def relative_to(self, filepath: str):
        """ 相対パスを返す """
        return Path(os.path.relpath(self.get_value(), str(filepath)))
    

    def set_exprs(self, values: dict):
        """ エクスプレションをセット """
        if type(values) == dict:
            self._exprs = values

        else:
            raise TypeError('Type is not dict.')


    def set_value(self, value: str) -> str:
        if value is None:
            self._value = value
        else:
            self._value = as_posix(str(value))

        return self.get_value()
    

    def set_var(self, key: str, value):
        """ 変数名で変数をセット """
        if type(key) == str:
            self._vars[key] = value
        else:
            raise TypeError('Type is not str.')

    def set_vars(self, values: dict):
        """ 変数をセット """
        if type(values) == dict:
            self._vars = values

        else:
            raise TypeError('Type is not dict.')
        

    def set_version_digits(self, value: int):
        if type(value) == int:
            self._version_digits = value
        else:
            raise TypeError()



    def suffix(self) -> str:
        return suffix(self.get_value())
    

    def stem(self) -> str:
        """ 拡張子を取り除いた名前部分を取得
        
        Examples:
            >>> path = tylibs.path.TyPath(r'/typ14/typmgrs/PluginManager.py')
            >>> print(path.stem())
                PluginManager
        
        """
        return stem(self.get_value())
    

    def version_up(self, num=1):
        _result = version_up(self.get_value, num=num)

        self.set_value(_result)

        return _result
    
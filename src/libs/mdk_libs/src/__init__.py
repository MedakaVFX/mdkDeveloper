""" mdklibs
 
* VFX用Pythonパッケージ

Info:
    * Created : v0.0.1 2024-11-01 Tatsuya YAMAGISHI
    * Coding : Python 3.12.4 & PySide6
    * Author : MedakaVFX <medaka.vfx@gmail.com>
 
Release Note:
    * v0.0.1 2024-12-19 Tatsuya Yamagishi
        * added: fpt
        * added: path
"""
VERSION = 'v0.0.1'
NAME = 'mdklibs'


import datetime
import logging
import os
import pathlib
import platform
import webbrowser


if os.environ.get('MDK_DEBUG'):
    print('MDK | ---------------------------')
    print('MDK | [ import mdklibs package]')
    print(f'MDK | {NAME} {VERSION}')
    print('MDK | ---------------------------')


#=======================================#
# Import Modules
#=======================================#
from . import data
from . import file
from . import fpt
from . import path
from . import qt
from . import time


from .data import Data
from .path import Path


#=======================================#
# Functions
#=======================================#
def get_env_username() -> str:
    """
    OSログインユーザー名を取得

    Returns:
        str: OSログインユーザー名

    Examples: 
        >>> user_name = sppibs.user.get_os_username()
        ta_yamagishi

    Note:
        注意事項などを記載
 
    """
    for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
        user = os.environ.get(name)
        if user:
            return user
        
    return None


def get_logger() -> logging.Logger:
    _logger = logging.getLogger(__name__)

    if os.environ.get('MDK_DEBUG'):
        _logger.setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.INFO)
    
    _logger.propagate = False
    _stream_handler = logging.StreamHandler()
    _stream_handler.setFormatter(logging.Formatter(
        '[%(levelname)s][%(name)s][%(funcName)s:%(lineno)s] %(message)s')
    )
    _logger.addHandler(_stream_handler)

    return _logger


def get_today(separate='-') -> str:
    """ 今日の日付を取得
    Examples:
        >>> tylibs.time.get_today(separate)
        >>> 2022{separate}07{separate}18
        >>> tylibs.time.get_today('-')
        >>> 2022-07-18
    """
    dt = datetime.datetime.today()
    result = dt.strftime(f'%Y{separate}%m{separate}%d')

    return result


def get_user_document_dir() -> str:
    """ ユーザーのホームドキュメントディレクトリパス取得
    
    """
    user_dir = get_user_home_dir()

    if platform.system == 'Darwin':
        raise RuntimeError('Unimplemented')
    elif platform.system == 'Linux':
        raise RuntimeError('Unimplemented')
    elif platform.system == 'Windows':
        return f'{user_dir}/Documents'
    

def get_user_home_dir() -> str:
    """ カレントユーザのホームディレクトリのパスの取得

    * `pathlib.Path(os.path.expanduser('~'))`
      でもローカルのユーザーディレクトリの取得は可能だが
      Windows Houdiniなどでドキュメントフォルダが重複してしまう問題がある。

    * 現在、WindowsのOSディレクトリがC以外に非対応

    Returns:
        str: ローカルユーザーディレクトリ

    Refrence From:
        * https://www.lifewithpython.com/2015/10/python-get-current-user-home-directory-path.html

    Examples: 
        >>> tylibs.path.get_local_user_path()
            C:/Users/ta_yamagishi

    Examples:
        >>> print(os.path.expanduser('~'))
        >>> # => /Users/ユーザー名
        >>> print(os.path.expanduser('~/.bashrc'))
        >>> # => /Users/ユーザー名/.bashrc
    """
    # return os.path.expanduser('~')

    username = get_env_username()
    
    os_name = platform.system()
    if os_name == 'Windows':
        path = f'C:/Users/{username}'
    elif platform.system() == 'Darwin':
        path = f'/Users/{username}'
    elif  platform.system() == 'Linux':
        path = f'/home/{username}'

    return pathlib.Path(path).as_posix()



def name() -> str:
    return NAME


def open_web(url: str):
    """ URLをWebBrowserで開く """
    webbrowser.open(url, new=2)


def version() -> str:
    return VERSION
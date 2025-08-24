""" mdklibs.path
 
* path管理用モジュール
* ファイルパスは基本的にposix_pathで処理

Info:
    * Created : 2024-11-01 Tatsuya YAMAGISHI
    * Coding : Python 3.12.4 & PySide6
    * Author : MedakaVFX <medaka.vfx@gmail.com>


Release Note:
    * LastUpdated : 2024-11-08 Tatsuya Yamagishi
"""
import csv
import urllib.request
import json
import os
import pathlib
import platform
import subprocess
import shutil


#=======================================#
# Settings
#=======================================#


#=======================================#
# Funcsions
#=======================================#
def copy(src_filepath, dst_filepath, exists=False):
    """
 
        <src> を <dst> にコピーする
 
        Args:
            srt (str or pathlib.Path): コピー元
            dst (str or pathlib.Path): コピー先
            exists=False (bool): 上書き, exists=newer 新しかったら上書き

         Raises:
            Exception: khLibs.file.copy()のエラーで発生
   
        Examples: 
            >>> mdklibs.file.copy( <src>, <dst>, extists=False )
    """

    if src_filepath is None:
        raise FileNotFoundError()
    
    if dst_filepath is None:
        raise FileNotFoundError()
    

    _src_filepath = pathlib.Path(src_filepath)
    _dst_filepath = pathlib.Path(dst_filepath)

    if _src_filepath.is_dir():
        _dst_filepath.mkdir(parents=True, exist_ok=True)

    elif not _dst_filepath.exists():
        _dst_filepath.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(_src_filepath, _dst_filepath)
    

    elif exists == 'newer':
        _src_stat = _src_filepath.stat()
        _dst_stat = _dst_filepath.stat()

        if _src_stat.st_mtime > _dst_stat.st_mtime:

            shutil.copy2(_src_filepath, _dst_filepath)

    elif exists == True:

        shutil.copy2(_src_filepath, _dst_filepath)



def delete(filepath):
    """ ファイルを削除 """
    if os.path.exists(filepath):
        # os.chmod(filepath, 0755)
        shutil.rmtree(filepath)

    else:
        raise FileNotFoundError(f'File is not found.\nfilepath={filepath}')
    


def download_url_imagefile(url, dst_path):
    try:
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(dst_path, mode='wb') as local_file:
                local_file.write(data)
                
    except urllib.error.URLError as ex:
        raise urllib.error.URLError(ex)
    
    
def move(src, dst):
    """ ファイル移動 """
    if os.path.isfile(src):
        dst_dir = os.path.dirname(dst)

        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

    shutil.move(src, dst)



def replace_text(filepath: str, replace_list: list[str]):
    """ 
    
    Args:
        replcae_list(list): 置き換える文字リスト（['test', 'hoge'], ['moji', 'string']）
    """
    _lines = load_lines(filepath)

    # pprint.pprint(_lines)

    for _i, _line in enumerate(_lines):
        for _replace in replace_list:
            _src, _dst = _replace

            if _src in _line:
                _src_text = f'{_i}: {_line}'

                try:
                    _line = _line.replace(_src, _dst)

                except Exception as ex:
                    print(ex)

                    print(f'MDK | line = {_line}')
                    print(f'MDK | _src = {_src}')
                    print(f'MDK | _dst = {_dst}')

                    raise RuntimeError(ex)


                _dst_text = f'{_line}'

                print(f'{_src_text} => {_dst_text}')

            _lines[_i] = _line

    save_lines(filepath, _lines)


#=======================================#
# I/O
#=======================================#
def open_file(filepath):
    """ <filepath>をOSで開く """
    if os.path.isfile(filepath):

        if platform.system() == 'Windows':
            cmd = 'explorer {}'.format(filepath.replace('/', '\\'))
            subprocess.Popen(cmd)
        
        elif platform.system() == 'Darwin':
            subprocess.call(['open', filepath])
        
        else:
            subprocess.Popen(["xdg-open", filepath])

    else:
        raise TypeError('"filepath" is not file.')
    

#----------------------------
# CSV
#----------------------------
def load_csv(filepath) -> dict:
    """ CSVファイルを開く """
    _result = []

    with open(filepath, 'r') as _f:
        _reader = csv.reader(_f)
        _header = next(_reader)

        for _row in _reader:
            _value = {}
            for _name, _data in zip(_header, _row):
                try:
                    _value[_name] = _data.encode()
                except:
                    _value[_name] = _data

            #print(value)
            _result.append(_value)

    return _result


def save_csv(filepath, data: list[str]):
    """ CSVファイルを保存する """
    with open(filepath, 'w') as _f:
        _writer = csv.writer(_f, lineterminator='\n') # 改行コード（\n）を指定しておく
        _writer.writerows(data)



#----------------------------
# JSON
#----------------------------
def load_json(json_file_path: str) -> dict:
    """
    Windows版 Blender 対策でencodeを'cp932'に。
        * Blender依存なのか？Python 3.10のせいか？理由は不明

        
    Todo:
        * CP932がDOS用のJISコードであるため、将来的にOS判定が必要かも by Yamagishi

    """
    try:
        with open(json_file_path, encoding='UTF-8') as f:
            result = json.load(f)

        return result

    except:
        with open(json_file_path, encoding='CP932') as f:
            result = json.load(f)

        return result


def save_json(json_file_path: str, dict_data: dict):
    """
    Jsonファイルの保存

    Args:
        json_file_path (str): 保存先
        dict_data (dict): 保存するデータ
    """
    with open(json_file_path, 'w', encoding='UTF-8') as f:
        json.dump( dict_data, f, indent=4, sort_keys=True, ensure_ascii=False)

        
#----------------------------
# TEXT
#----------------------------
def load_lines(filepath) -> list:
    """
    <file_path> のテキストをlinesで開く
    """
    with open(filepath, encoding='utf8', errors='ignore') as _f:
        _result = _f.readlines()

    return _result



def load_text(filepath):
    return pathlib.Path(filepath).read_text(encoding='utf8')
 


def save_lines(filepath, lines: list[str]):
    """
    lines を <file_path> で保存

    Args:
        * lines<list> : 文字列リスト
    """

    with open(filepath, mode='w', encoding='utf8') as _f:
        _f.writelines(lines)


def save_text(filepath, data):
    _path = pathlib.Path(filepath)
    _path.parent.mkdir(parents=True, exist_ok=True)
    _path.write_text(data, encoding='utf8')




#----------------------------
# Image
#----------------------------
def save_image_from_url(url, image_filepath):
    """ urlで指定された画像ファイルを保存する """
    try:
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(image_filepath, mode='wb') as local_file:
                local_file.write(data)
                
    except urllib.error.URLError as ex:
        raise urllib.error.URLError(ex)
""" mdklibs.data
 
* データ管理用モジュール

Info:
    * Created : 2024-11-10 Tatsuya YAMAGISHI
    * Coding : Python 3.12.4 & PySide6
    * Author : MedakaVFX <medaka.vfx@gmail.com>


Release Note:
    * LastUpdated : 2024-11-10 Tatsuya Yamagishi
"""

import dataclasses
import pprint


import mdk_libs as mdk
#=======================================#
# Settings
#=======================================#


#=======================================#
# Funcsions
#=======================================#
   
#=======================================#
# Class
#=======================================#
   
@dataclasses.dataclass
class Data:
    """ Data
 
    * データ管理用クラスの基底クラス
    
        >>> _value: dict = dataclasses.field(default_factory=dict(), init = False)
        >>> _value: list = dataclasses.field(default_factory=list(), init = False)
    """

    id: int = None


    def get_dict(self, *args):
        if args:
            if len(args) == 1:
                return self.get_attr(args[0])
            
        else:
            return dataclasses.asdict(self)


    def get_attr(self, key):
        return getattr(self, key)
    

    def get_id(self) -> int:
        return self.id
    


    def set_attr(self, key, value):
        setattr(self, key, value)


    def set_dict(self, data: dict):
        if type(data) == dict:
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        else:
            raise TypeError('Value is not dict.')
        

    def set_id(self, value: int):
        self.id = value


    def set_values(self, **kwargs):
        """
        Examples:

            >>> TyData.set_calues(name='yamagishi', age='20')

        """        
        self.set_dict(kwargs)
   
    
    #----------------------------------
    # Methods
    #----------------------------------
    def show(self):
        pprint.pprint(self.get_dict())


    #----------------------------------
    # Save / Load
    #----------------------------------
    def save(self, json_filepath:str):
        _value = self.get_dict()
        try:
            mdk.file.save_json(json_filepath, _value)
        except Exception as e:
            print(f'json_filepath = {json_filepath}')
            print(f'value = \n{_value}')
            raise e

        
    def load(self, json_filepath) -> dict:
        _value = mdk.file.load_json(json_filepath)
        self.set_dict(_value)

        return _value



if __name__ == '__main__':
    pass

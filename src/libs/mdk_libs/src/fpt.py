""" mdklibs.fpt
 
* Flow PT Python API

Info:
    * Created : 2024-12-15 Tatsuya YAMAGISHI
    * Coding : Python 3.12.4 & PySide6
    * Author : MedakaVFX <medaka.vfx@gmail.com>


Release Note:
    * LastUpdated : 2025-01-20 Tatsuya Yamagishi
        * added : get_asset
        * added : add_filter
"""
import datetime
import functools
import webbrowser

try:
    import shotgun_api3
except:
    pass


import mdk_libs as mdk

#=======================================#
# Settings
#=======================================#


#=======================================#
# Decolator
#=======================================#
def login_required(func):
    """ FPTログイン確認用デコレータ """

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        sg = args[0]
        logger = sg.logger

        logger.debug('UNF | [fpt Loggin required]')

        sg.login()
        
        return func(*args, **kwargs)
    return _wrapper


#=======================================#
# Functions
#=======================================#
def refine_fpt_data(fpt_entity: dict):
    """ FPT データをリファイン 
    
    * dataTime型を文字列に変換

    """

    if fpt_entity:
        _time_fields = ['created_at', 'updated_at']

        for _time_field in _time_fields:
            _dt = fpt_entity.get(_time_field)
            
            if type(_dt) == datetime.datetime:
                fpt_entity[_time_field] = _dt.strftime('%Y-%m-%d %H:%M:%S')


        return fpt_entity
        

def refine_fpt_entity_list(fpt_entity_list: list[dict]):
    """ FPT データリストをリファイン"""
    for _fpt_entity in fpt_entity_list:
        refine_fpt_data(_fpt_entity)


#=======================================#
# Class
#=======================================#
class Fpt:
    """ FPT用クラス
 
    ShotGrid Python APIラッパークラス
 
    Attributes:
        core (:obj:`core`): パイプラインコア
        logger (:obj:`logging.logger`): パイプラインロガー
 
    """
    def __init__(self, logger) -> None:
        self.logger = logger

        self._fpt = None

        self._project: dict = None
        self._user: dict = None

        self._url: str = None


    def exists(self):
        """  
        fpt インスタンスオブジェクトの有無。ログイン判定に使用
        """
        return self._fpt
    

    def login(
        self, url: str=None, script_name: str=None, api_key: str=None, ) -> None:
        """
        
        ShotGrid ログイン

        Args:
            url (str): ShotGrid ホーム URL
            script_name (str): Script名
            api_key (str): Script名に紐づくSgトークン
            
        """
        # CA_CERTS_PATH = self.spp.get_setting('SG_SHOTGUN_API_CACERTS')

        # if not CA_CERTS_PATH.exists():
        #     message = f'File is not found\nfile = {CA_CERTS_PATH.as_posix()}'
        #     raise FileNotFoundError(message)

        self._url = url

        self._fpt = shotgun_api3.Shotgun(
            url,
            script_name,
            api_key,
            # ca_certs=CA_CERTS_PATH.as_posix(),
        )




    # ----------------------------------
    # Methods
    # ----------------------------------
    def add_filter(self, filters: list, key: str, operator: str, value):
        """ フィルターを追加 
        
        Examples:
            >>> _fpt.add_filter(filters, 'project', 'is', self._project)
            >>> _fpt.add_filter(filters, 'sg_asset_type', 'is', 'Character')
            >>> _fpt.add_filter(filters, 'sg_name', 'is', name)
        """
        if filters is None:
            filters = []

        filters.append([key, operator, value])
        
        return filters



    def create_entity(self, entity_type: str, fpt_dict: dict) -> dict:
        fpt_dict['project'] = self._project

        if self._user:
            fpt_dict['created_by'] = self._user

        try:
            return self._fpt.create(entity_type, fpt_dict)
        
        except Exception as ex:
            self.logger.error(fpt_dict)  

            raise RuntimeError(ex)
    

    def create_playlist(self, fpt_dict: dict) -> dict:
        """ プレイリストを作成
        'Playlist': {
            'code': None,
            'description': None,
        }
        """
        fpt_dict['project'] = self._project
        if self._user:
            fpt_dict['created_by'] = self._user

        return self._fpt.create('Playlist', fpt_dict)


    def create_timelog(self, fpt_dict: dict):
        """ タイムログを作成
        
        fpt_dict = {
            'entity': sg_task,
            'user': {'type': 'HumanUser', 'id': int(user_id)},
            'date': 2024-05-28,
            'duration': float(value)*60, # HtoM
            'description': description,
        }
        """

        fpt_dict['project'] = self._project

        return self._fpt.create('TimeLog', fpt_dict)
        

    def create_version(self, fpt_dict: dict):
        """ Versionを作成

        Examples:
            >>> _sg_dict = {
            >>>     'code': _code,
            >>>     'entity': _sg_liveplate,
            >>>     'description': '',
            >>>     'sg_path_to_movie': self.get_movie(),
            >>>     'sg_path_to_frame': self.get_filepath(),
            >>>     'playlists': [sg_playlist,]
            >>> }

        """
        fpt_dict['project'] = self._project

        if self._user:
            fpt_dict['user'] = self._user

        try:
            _fpt_version = self._fpt.create('Version', fpt_dict)
        except Exception as ex:
            self.logger.error(fpt_dict)

            raise ValueError(ex)

        
        _upload_movie = self._fpt.upload(
                'Version', _fpt_version.get('id'),
                fpt_dict.get('sg_path_to_movie'),
                'sg_uploaded_movie'
        )

        return _fpt_version
    

    def get_url_by_entity(self, entity: dict):
        _sg_url = self.get_url()
        _id = entity['id']
        _type = entity['type']

        return f'{_sg_url}detail/{_type}/{_id}'
    

    def open_in_web(self, entity: dict):
        # _sg_url = self.get_url()
        # _id = entity['id']
        # _type = entity['type']

        # _url = f'{_sg_url}detail/{_type}/{_id}'

        _url = self.get_url_by_entity(entity)
        webbrowser.open(_url, new=2)


    def update(self, entity_type: str, entity_id: int, sg_dict: dict) -> dict:
        """ Shotgridのエンティティをアップデート

        Args:
            entity_type(str): エンティティタイプ名（Project, Asset, Shot, Task, Version等）
            entity_id(int): 更新したいエンティティのID
            sg_dict(dict): アップデートしたいパラメータを辞書型で設定

        Returns:
            dict: アップデートしたFPTエンティティ

        Examples:
            >>> _fpt_dict = {
            >>>    'description': 'キャラA',
            >>>    'sg_status_list': 'ip',}
            >>> _fpt_asset = fpt.update('Asset', 10658, _sg_dict)        
        """

        return self._fpt.update(entity_type, entity_id, sg_dict)
    

    
    def upload(self, entity_type: str, index: int, filepath: str, field_name: str):
        try:
            # ShootdayエンティティにPDFをアップロード
            uploaded_file = self._fpt.upload(
                entity_type,  # エンティティタイプ
                index,  # エンティティID
                filepath,  # ファイルパス
                field_name= field_name  # Call Sheetを格納するフィールド名
            )
            
        except Exception as e:
            print("PDFのアップロード中にエラーが発生しました:", e)

    # ----------------------------------
    # Get
    # ----------------------------------
    def get_all_assets(self, filters=None, fields=None, mytask=False) -> dict:

        filters = self.add_filter(filters, 'project', 'is', self._project)

        self.logger.debug(filters)


        if mytask:
            filters = self.add_filter(
                filters, 'tasks.Task.task_assignees', 'is', self._user)

        return self._fpt.find('Asset', filters, fields)
    

    def get_all_episodes(self, filters=None, fields=None, mytask=False) -> dict:
        """ 全てのエピソードを取得 """
        filters = self.add_filter(filters, 'project', 'is', self._project)
        self.logger.debug(filters)

        if mytask:
            filters.append(
                ['sequences.Sequence.shots.Shot.tasks.Task.task_assignees', 'is', self._user])

    
        return self._fpt.find('Episode', filters, fields)
    

    def get_all_playlists(self, filters=None, fields=None, myversion=False):
        # if filters is None:
        #     filters = []

        # filters.append(['project', 'is', self._project])
        filters = self.add_filter(filters, 'project', 'is', self._project)

        return self._fpt.find('Playlist', filters, fields)


    def get_all_projects(self, filters=None, fields=None, mytask=False) -> dict:
        """ 全てのプロジェクトを取得 """
        # if filters is None:
        #     filters = []

        # filters.extend(
        #     [
        #         ['is_demo', 'is', False],
        #         ['is_template', 'is', False]
        #     ]
        # )
        filters = self.add_filter(filters, 'is_demo', 'is', False)
        filters = self.add_filter(filters, 'is_template', 'is', False)
        filters = self.add_filter(filters, 'sg_status', 'is', 'Active')

        if mytask:
            filters = self.add_filter(
                filters, 'users', 'is', self._user)
            # filters.append(
            #     ['users', 'is', self._user])

        if fields is None:
            fields = []

        return self._fpt.find('Project', filters, fields)
    

    def get_all_shootdays(self, filters=None, fields=None, mytask=False) -> dict:

        # if filters is None:
        #     filters = []

        # filters.append(['project', 'is', self._project])
        filters = self.add_filter(filters, 'project', 'is', self._project)

        self.logger.debug(filters)


        if mytask:
            filters.append(
                ['tasks.Task.task_assignees', 'is', self._user])

        return self._fpt.find('ShootDay', filters, fields)


    def get_all_scequences(self, filters=None, fields=None, mytask=False) -> dict:
        """ 全てのシーケンスを取得
        
        """
        filters = self.add_filter(filters, 'project', 'is', self._project)
        
        if mytask:
            filters = self.add_filter(
                    filters, 'shots.Shot.tasks.Task.task_assignees', 'is', self._user)

        # if mytask:
        #     filters.append(
        #         ['shots.Shot.tasks.Task.task_assignees', 'is', self._user])
            
        self.logger.debug(filters)

        return self._fpt.find('Sequence', filters, fields)


    def get_all_shots(self, filters=None, fields=None, mytask=False) -> dict:
        """ 全てのショットを取得
        
        """

        # if filters is None:
        #     filters = []

        # filters.append(['project', 'is', self._project])
        # if mytask:
        #     filters.append(
        #         ['tasks.Task.task_assignees', 'is', self._user])
        filters = self.add_filter(filters, 'project', 'is', self._project)
        if mytask:
            filters = self.add_filter(
                filters, 'tasks.Task.task_assignees', 'is', self._user)
            
        self.logger.debug(filters)


        return self._fpt.find('Shot', filters, fields)
    


    def get_all_task_template(self, filters=None, fields=None):
        """ 全てのタスクテンプレートを取得 """
        if filters is None:
            filters = []

        if fields is None:
            fields=[]

        return self._fpt.find('TaskTemplate', filters, fields)
    

    def get_all_tasks(
                self,
                entity:dict = None,
                filters: list[list] = None,
                fields: list[str] = None,
                mytask: bool = False) -> list[dict]:

        """ プロジェクト内の全てのタスクを取得 """        

        # if filters is None:
        #     filters = []
        # filters.append(['project', 'is', self._project])
        filters = self.add_filter(filters, 'project', 'is', self._project)

        if entity:
            filters.append(['entity', 'is', entity])

        if mytask:
            filters.append(['task_assignees', 'is', self._user])

        if fields is None:
            fields = ['content',]


        return self._fpt.find('Task', filters, fields)


    def get_all_task_template(self, filters=None, fields=None):
        """ 全てのタスクテンプレートを取得 """
        if filters is None:
            filters = []

        if fields is None:
            fields=[]

        return self._fpt.find('TaskTemplate', filters, fields)
    

    def get_all_users(self, filters: list=None, fields: list=None) -> dict:
        """ 全てのユーザーを取得 """
        if filters is None:
            filters = []

        
        if fields is None:
            fields = []


        return self._fpt.find('HumanUser', filters, fields)
    
    
    def get_all_versions(self, filters=None, fields=None) -> dict:
        """ 全てのバージョンを取得 """
        if filters is None:
            filters = []

        
        if fields is None:
            fields = []


        return self._fpt.find('Version', filters, fields)
    

    def get_asset(self, code: str, filters=None, fields=None, mytask=False):
        """ Asset をコードで取得
        

        """
        filters = self.add_filter(filters, 'project', 'is', self._project)
        filters = self.add_filter(filters, 'code', 'is', code)

        if fields is None:
            fields = []

        return self._fpt.find_one('Asset', filters, fields)

    def get_asset_type_list(self):
        """ アセットタイプリストを取得 """
        return self.get_field_data('Asset', 'sg_asset_type')
    

    def get_entity(
                self,
                entity_type: str,
                code: str,
                filters:list = None,
                fields=None) -> dict:
        
        """ エンティティをコードで取得 """
        
        # filters = [
        #     ['project', 'is', self._project],
        #     ['code', 'is', code],
        # ]

        filters = self.add_filter(filters, 'project', 'is', self._project)
        filters = self.add_filter(filters, 'code', 'is', code)

        if fields is None:
            fields = []

        return self._fpt.find_one(entity_type, filters, fields)
    

    def get_entity_by_id(self, entity_type: str, entity_id: int, filters=None, fields=None) -> dict:
        """ idでエンティティを取得 
        
        Args:
            entity_type(str): エンティティタイプ = Asset | Shot | Task | Project | etc.
            entity_id(int): エンティティID
        """

        # if filters is None:
        #     filters = [
        #         ['id', 'is', entity_id],
        #     ]

        filters = self.add_filter(filters, 'id', 'is', entity_id)

        if fields is None:
            fields = []


        return self._fpt.find_one(entity_type, filters, fields)
    


    def get_episode(self, code: str, filters: list = None, fields=None) -> dict:
        """ エピソードを取得
        
        * 2025-01-01 Yamagishi

        """
        # filters = [
        #     ['project', 'is', self._project],
        #     ['code', 'is', code],
        # ]

        filters = self.add_filter(filters, 'project', 'is', self._project)
        filters = self.add_filter(filters, 'code', 'is', code)

        if fields is None:
            fields = []

        return self._fpt.find_one('Episode', filters, fields)
    

    def get_field_data(self, entity: dict, field_name: str):
        """ フィールドデータを取得 """
        _context = self._fpt.schema_field_read(
                    entity,
                    field_name=field_name,
                    project_entity=self._project)
        
        return _context[field_name]['properties']['valid_values']['value']
    

    def get_playlist(self, code, filters: list = None, fields=None):
        """ プレイリストをコードで取得
        
        """
        filters = self.add_filter(filters, 'project', 'is', self._project)
        filters = self.add_filter(filters, 'code', 'is', code)

        if fields is None:
            fields = []

        return self._fpt.find_one('Playlist', filters, fields)
    

    def get_scene(self, code, filters=None, fields=None):
        """ シーン（撮影日）をコードで取得
        
        """
        filters = self.add_filter(filters, 'project', 'is', self._project)
        filters = self.add_filter(filters, 'code', 'is', code)

        # filters = [
        #     ['project', 'is', self._project],
        #     ['code', 'is', code],
        # ]

        if fields is None:
            fields = []


        return self._fpt.find_one('Scene', filters, fields)
    

    def get_sequence(self, episode_code: str, code: str=None, filters=None, fields=None):
        _episode = self.get_episode(episode_code)

        filters = self.add_filter(filters, 'project', 'is', self._project)
        filters = self.add_filter(filters, 'code', 'is', code)
        filters = self.add_filter(filters, 'episode', 'is', _episode)

        if fields is None:
            fields = []

        return self._fpt.find_one('Sequence', filters, fields)
    

    def get_shootday(self, code: str, filters=None, fields=None):
        # if filters is None:
        #     filters = []

        # filters = [
        #     ['project', 'is', self._project],
        #     ['code', 'is', code],]

        filters = self.add_filter(filters, 'project', 'is', self._project)
        filters = self.add_filter(filters, 'code', 'is', code)

        if fields is None:
            fields = []


        return self._fpt.find_one('ShootDay', filters, fields)
    

    def get_shot(self, name: str, filters=None, fields=None, mytask=False):
        """ Shotを名前で取得 
        
        * nameはカスタムフィールド: sg_name

        """
        # if filters is None:
        #     filters = []


        # filters.append(['project', 'is', self._project])
        # filters.append(['sg_name', 'is', name])

        filters = self.add_filter(filters, 'project', 'is', self._project)
        filters = self.add_filter(filters, 'sg_name', 'is', name)

        if fields is None:
            fields = []

        return self._fpt.find_one('Shot', filters, fields)
    

    def get_task(
                self,
                task_name: str,
                sg_entity: dict,
                filters: list = None,
                fields: list = None,
                mytask: bool = False):
        
        # filters = [
        #     ['project', 'is', self._project],
        #     ['entity', 'is', sg_entity],
        #     ['content', 'is', task_name],
        # ]

        filters = self.add_filter(filters, 'project', 'is', self._project)
        filters = self.add_filter(filters, 'entity', 'is', sg_entity)
        filters = self.add_filter(filters, 'content', 'is', task_name)

        if mytask:
            filters.append(['task_assignees', 'is', self._user])


        result = self._fpt.find_one('Task', filters, fields)

        return result



    def get_url(self) -> str:
        return self._url
    

    def get_version(self, code: str, filters: list =None, fields: list[str]=None) -> dict:
        """ バージョンを名前で取得 """

        filters = self.add_filter(filters, 'project', 'is', self._project)
        filters = self.add_filter(filters, 'code', 'is', code)

        return self._fpt.find_one('Version', filters, fields)
    

    # --------------------------------- #
    # Set
    # --------------------------------- #
    def set_project(self, project: dict):
        self._project = project

    def set_url(self, value: str):
        self._url = value

    def set_user(self, entity: dict):
        self._user = entity





if __name__ == '__main__':
    pass

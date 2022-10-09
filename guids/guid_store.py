#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2022 https://github.com/Oops19
#


import ast
import base64
import os
from typing import Dict, Union, Set, List, Any

from guids.libraries.ts4folders import TS4Folders
from s4cl.utils.common_enum import CommonEnum

from s4cl.utils.uncommon_log import UnCommonLog  # TODO
from guids.modinfo import ModInfo  # TODO
log: UnCommonLog = UnCommonLog(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name)  # TODO


class GUIDStoreType(CommonEnum):
    MODS: 'GUIDStoreType' = 'mods'
    GAME: 'GUIDStoreType' = 'game'

class GUIDStore:
    """
    This class provides random access to the GUIDs of the 'Game' and 'Mods' folder.
    cached_packages_game_data can be used to obtain game data.
    cached_packages_mods_data can be used to contain mods data.

    Game and mods data may contain also internal names.
    If you want to create a ZIP file for an outfit make sure to include only mods data files.
    References to game files should be listed as external requirements.
    """

    WARN_MSG = "WARNING - This file contains private and/or sensitive information (your local username and your installed mods). Do not share it!"

    '''
    {
    	'RGVsdGFcU1AyOVxTaW11bGF0aW9uUHJlbG9hZA==': [123947, '2022-08-08T18:43:56'],  # base64(package-name): [size, time|sha1]
    	...,
    }
    '''
    _mods_packages: Dict[str, List] = dict()
    _game_packages: Dict[str, List] = dict()

    '''
    {
        'RGF0YVxDbGllbnRcQ2xpZW50RnVsbEJ1aWxkMA==': {  # base64(Data\Client\ClientFullBuild0.package)
            3308: {  # GUID of a Cas Part item
                'name': 'ymShoes_AnkleWork_Brown',  # 'name' and value(name)
                'dlc': 'EP01',  # re: "''|[EFGS]P[0-9][0-9]"
                'body_type': 8,  # BodyType.SHOES = 8
                'species': [ ... ],
                'ages': [ ... ],
                'genders': [ ... ],
                'tags': [ ... ],
                'colors': [ ... ],
                },
            3309: { ... },
        '...': { ... },
    }
    '''
    _mods_data: Dict[str, Dict[int, Dict[str, Union[str, List[int]]]]] = dict()  # {'a.package': {1: 'Author_Cas_Part_Name_1234', 2: 'Author...', ...}, 'b.package': {100: ...}, ...}
    _game_data: Dict[str, Dict[int, Dict[str, Union[str, List[int]]]]] = dict()

    '''
    {
        'RGF0YVxDbGllbnRcQ2xpZW50RnVsbEJ1aWxkMA==': {  # base64(Data\Client\ClientFullBuild0.package)
            (3308, 3309, ...),  # All GUIDs within this package
        '...': { ... },
    }
    '''
    _mods_items_mini: Dict[str, Set[int]] = dict()
    _game_items_mini: Dict[str, Set[int]] = dict()

    '''
    (3308, 3309, ...)  # All Cas Part GUIDs
    '''
    _mods_items_part_ids: Set[int] = set()  # (1, 2, 100, ...) - All 'mods' Cas Part GUIDs
    _game_items_part_ids: Set[int] = set()

    _mods_data_defined = False
    _game_data_defined = False
    _is_ready = False

    _t = '\t'
    _o = '{'
    _c = '}'
    _n = '\n'
    _intent = 0

    def __init__(self):
        self.ts4f = TS4Folders(log, ModInfo.get_identity().base_namespace)

    def load(self, t: GUIDStoreType):
        if (t == GUIDStoreType.MODS) or (t == GUIDStoreType.GAME):
            __cached_data_filename = os.path.join(self.ts4f.data_folder, f"cached_{t.value}_data.dict")
            data: Dict[str, Dict] = self._read_cached_data(__cached_data_filename)

            __cached_packages_filename = os.path.join(self.ts4f.data_folder, f"cached_{t.value}_filename_info.dict")
            packages: Dict[str, List] = self._read_cached_filename_info(__cached_packages_filename)  # {'b64(a.package)': [size(a.package), ctime/sha1((a.package)], ...}

            self._load(t, data, packages)

    @staticmethod
    def _load(t, data, packages):
        items_dict: Dict[str, Set[int]] = dict()
        items_set = set()
        if t == GUIDStoreType.MODS:
            GUIDStore._mods_data = data
            GUIDStore._mods_packages = packages

            for b64_filename, _data in GUIDStore._mods_data.items():
                items_dict.update({b64_filename: set(_data.keys())})
                items_set.update(set(_data.keys()))
            GUIDStore._mods_items_mini = items_dict
            GUIDStore._mods_items_part_ids = items_set

            GUIDStore._mods_data_defined = True
            if GUIDStore._game_data_defined:
                GUIDStore._is_ready = True

        elif t == GUIDStoreType.GAME:
            GUIDStore._game_data = data
            GUIDStore._game_packages = packages

            for b64_filename, _data in GUIDStore._game_data.items():
                items_dict.update({b64_filename: set(_data.keys())})
                items_set.update(set(_data.keys()))
            GUIDStore._game_items_mini = items_dict
            GUIDStore._game_items_part_ids = items_set

            GUIDStore._game_data_defined = True
            if GUIDStore._mods_data_defined:
                GUIDStore._is_ready = True


    def save(self, t: GUIDStoreType, pretty: bool = False):
        if t == GUIDStoreType.MODS:
            data = GUIDStore._mods_data
            packages = GUIDStore._mods_packages
        elif t == GUIDStoreType.GAME:
            data = GUIDStore._game_data
            packages = GUIDStore._game_packages
        else:
            return

        cached_data_filename = os.path.join(self.ts4f.data_folder, f"cached_{t.value}_data.dict")
        # TODO split the data f(size)
        self.write_dict(cached_data_filename, data, pretty=pretty)

        cached_packages_filename = os.path.join(self.ts4f.data_folder, f"cached_{t.value}_filename_info.dict")
        self.write_dict(cached_packages_filename, packages, pretty=pretty)

    def packages(self, t: GUIDStoreType) -> Union[None, Dict[str, List]]:
        if t == GUIDStoreType.MODS:
            return GUIDStore._mods_packages
        elif t == GUIDStoreType.GAME:
            return GUIDStore._game_packages
        return None

    def data(self, t: GUIDStoreType) -> Union[None, Dict[str, Dict[int, Dict[str, Union[str, List[int]]]]]]:
        if t == GUIDStoreType.MODS:
            return GUIDStore._mods_data
        elif t == GUIDStoreType.GAME:
            return GUIDStore._game_data
        return None

    def update(self, t: GUIDStoreType, data: Dict[str, Dict[int, Dict[str, Union[str, List[int]]]]], packages: Dict[str, List]):
        self._load(t, data, packages)

    @property
    def mods_data(self) -> Union[None, Dict[str, Dict[int, Dict[str, Union[str, List[int]]]]]]:
        if GUIDStore._is_ready:
            return GUIDStore._mods_data
        return None
    
    @property
    def mods_data_mini(self) -> Union[None, Dict[str, Set[int]]]:
        if GUIDStore._is_ready:
            return GUIDStore._mods_items_mini
        return None
    
    @property
    def mods_data_part_ids(self) -> Union[None, Set[int]]:
        if GUIDStore._is_ready:
            return GUIDStore._mods_items_part_ids
        return None

    @mods_data.setter
    def mods_data(self, data: Dict[str, Dict[int, Dict[str, Union[str, List[int]]]]]):
        GUIDStore._mods_data = data

        items_dict: Dict[str, Set[int]] = dict()
        items_set = set()
        for b64_filename, data in GUIDStore._mods_data.items():
            items_dict.update({b64_filename: set(data.keys())})
            items_set.update(set(data.keys()))
        GUIDStore._mods_items_mini = items_dict
        GUIDStore._mods_items_part_ids = items_set

        GUIDStore._mods_data_defined = True
        if GUIDStore._game_data_defined:
            GUIDStore._is_ready = True

    @property
    def game_data(self) -> Union[None, Dict[str, Dict[int, Dict[str, Union[str, List[int]]]]]]:
        if GUIDStore._is_ready:
            return GUIDStore._game_data
        return None

    @property
    def game_data_mini(self) -> Union[None, Dict[str, Set[int]]]:
        if GUIDStore._is_ready:
            return GUIDStore._game_items_mini
        return None

    @property
    def game_data_part_ids(self) -> Union[None, Set[int]]:
        if GUIDStore._is_ready:
            return GUIDStore._game_items_part_ids
        return None

    @game_data.setter
    def game_data(self, data: Dict[str, Dict[int, Dict[str, Union[str, List[int]]]]]):
        GUIDStore._game_data = data

        items_dict: Dict[str, Set[int]] = dict()
        items_set = set()
        for b64_filename, data in GUIDStore._game_data.items():
            items_dict.update({b64_filename: set(data.keys())})
            items_set.update(set(data.keys()))
        GUIDStore._game_items_mini = items_dict
        GUIDStore._game_items_part_ids = items_set

        GUIDStore._game_data_defined = True
        if GUIDStore._mods_data_defined:
            GUIDStore._is_ready = True

    @property
    def free(self) -> bool:
        """
        Purge the 'data' values from cache. It affects only 'mods_data' and 'game_data' properties which will return 'None' afterwards.
        Calling it may have an impact on other mods relying on the Cas Part Name data.
        Usage pattern: 'game_data(data); free()'
        :return:
        """
        _mods_data: Dict[str, Dict[int, str]] = dict()
        _game_data: Dict[str, Dict[int, str]] = dict()
        return True

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    @is_ready.setter
    def is_ready(self, value: bool):
        if value is None:
            return
        GUIDStore._mods_data_defined = value
        GUIDStore._game_data_defined = value
        GUIDStore._is_ready = value

    def _read_cached_filename_info(self, filename) -> Dict[str, List[int]]:
        """
        Read a file with packages and their date/cname values
        :param filename:
        :return:
        """

        configuration: Dict[str, List] = dict()
        try:
            if os.path.isfile(filename):
                with open(filename, 'rt', encoding='utf-8') as fp:
                    configuration = ast.literal_eval(fp.read())
        except Exception as e:
            log.error(f"Error '{e}' reading '{filename}'.", throw=True, privacy_filter=True)
        return configuration

    def _read_cached_data(self, filename: str) -> dict:
        """
        Read the cached data with the package file names and their packages.
        :param filename:
        :return:
        """
        configuration: Dict[str, Dict[int, str]] = dict()
        try:

            if os.path.isfile(filename):
                with open(filename, 'rt', encoding='utf-8') as fp:
                    configuration = ast.literal_eval(fp.read())
        except Exception as e:
            log.warn(f"Error '{e}' reading '{filename}'.", privacy_filter=True)
        return configuration

    def write_dict(self, filename: str, data: dict, pretty: bool = False, with_filenames: bool = True):
        """
        No check for ' in keys or values. Elements with ' will lead to corrupt files.
        :param filename:
        :param data:
        :param pretty:
        :param with_filenames: If pretty==True the file names will be printed. Set this to False for other dicts.
        :return:
        """
        GUIDStore._intent = 0

        def write(fp, _data: dict):

            def _prepare(parameter: Any) -> Any:
                if isinstance(parameter, str):
                    return f"'{parameter}'"
                else:
                    return parameter

            fp.writelines(f"{GUIDStore._o}{GUIDStore._n}")
            GUIDStore._intent += 1
            for k, v in _data.items():
                if with_filenames and (GUIDStore._intent == 1):
                    try:
                        fp.writelines(f"\t# {self._get_folder_file_name_from_b64_short('', k)}\n")
                    except:
                        pass
                if isinstance(v, dict):
                    fp.writelines(f"{GUIDStore._t * GUIDStore._intent}{_prepare(k)}: ")
                    write(fp, v)
                else:
                    fp.writelines(f"{GUIDStore._t * GUIDStore._intent}{_prepare(k)}: {_prepare(v)},{GUIDStore._n}")
            GUIDStore._intent -= 1
            if GUIDStore._intent > 0:
                fp.writelines(f"{GUIDStore._t * GUIDStore._intent}{GUIDStore._c},{GUIDStore._n}")
            else:
                fp.writelines(f"{GUIDStore._t * GUIDStore._intent}{GUIDStore._c}{GUIDStore._n}")

        try:
            log.debug(f"pretty_write_dict({filename}, data={len(data.keys())}, pretty={pretty})", privacy_filter=True)
            fp = open(filename, 'wt', encoding='utf-8')
            fp.writelines(f"# {GUIDStore.WARN_MSG}{GUIDStore._n * 2}")
            if pretty:
                write(fp, data)
            else:
                fp.write(f"{data}")
            fp.writelines(f"{GUIDStore._n}# {GUIDStore.WARN_MSG}{GUIDStore._n}")
            fp.close()
        except Exception as e:
            log.error(f"Error '{e}' writing '{filename}'.")


    @staticmethod
    def _get_folder_file_name_from_b64_short(base_folder: str, short_folder_file_name_b64: str) -> str:
        """
        Encode the base64 encoded 'short_folder_file_name_b64' string and surround it with 'base_folder' and '.package'.
        It will convert 'TGl0dGxlL0JyaXRhaW4=' to 'Little/Britain.package' and prepend the 'base_folder'.
        Set base_folder to '' to exclude it.
        :param base_folder:
        :param short_folder_file_name_b64:
        :return:
        """
        suffix = '.package'
        short_folder_file_name = base64.b64decode(short_folder_file_name_b64.encode('ascii')).decode('utf-8')
        folder_file_name = os.path.normpath(os.path.join(base_folder, f"{short_folder_file_name}{suffix}"))
        return folder_file_name

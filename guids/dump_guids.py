#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2022 https://github.com/Oops19
#


import ast
import fnmatch
import hashlib
import os
import time
import base64
from typing import Set, List, Dict, Union

from guids.enums.resource_types import ResourceTypes
from guids.guid_store import GUIDStore, GUIDStoreType
from guids.libraries.ts4folders import TS4Folders
from guids.readers.dbpf.dbpf_parser import DBPFParser

from s4cl.utils.uncommon_log import UnCommonLog  # TODO
from guids.modinfo import ModInfo  # TODO
log: UnCommonLog = UnCommonLog(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name)  # TODO


class DumpGUIDs:
    warn_msg = "WARNING - This file contains private and/or sensitive information (your local username and your installed mods). Do not share it!"
    on_zone_loaded_message = ''
    _enabled = False
    """
    The config files will be read and according to the settings GUIDs will be parsed or not.
    Afterwards this value is set to True and the config settings will be ignored.
    """

    @staticmethod
    def get_configuration(ts4f: TS4Folders):
        configuration = {
            'scan_on_startup': True,  # Do the initial state scan
            'process_on_startup': True,  # Process everything on startup
            'process_game_data': True,  # Read game and DLC packages
            'process_mods_data': True,  # Read packages in 'Mods'
            'lookup_names': True,  # Add also the internal 'CAS Part Name'
            'lookup_metadata': False,  # Add the internal 'CAS Part Name' and 'Flags'
            'lookup_lods': False,  # Lookup logs and materials
        }
        configuration_file = None
        try:
            configuration_file = os.path.join(ts4f.data_folder, 'config.dict')
            if os.path.isfile(configuration_file):
                with open(configuration_file, 'rt') as fp:
                    user_configuration: Dict[str, bool] = ast.literal_eval(fp.read())
                    user_configuration.update(user_configuration)
                    log.debug(f"Read configuration file '{user_configuration}'.")
                    for key in configuration.keys():
                        value: Union[bool, None] = user_configuration.get(key, None)
                        if isinstance(value, bool):
                            configuration.update({key: value})
        except Exception as e:
            log.error(f"Error '{e}' while reading configuration file '{configuration_file}'.", throw=True)
        return configuration

    def process_folder(self, ts4f: TS4Folders, t: GUIDStoreType, config: Dict[str, bool]):
        gs = GUIDStore()
        # Read the already read and cached Data and Packages
        log.debug(f"Loading '{t.value}' data.")
        gs.load(t)

        cached_packages = gs.packages(t)
        cached_data = gs.data(t)

        # Gather all readable Package files
        scan_folder = t.value  # 'mods' or 'game'
        if t == GUIDStoreType.MODS:
            base_folder = ts4f.mods_folder
        else:
            base_folder = ts4f.ts4_folder_game
        all_packages_dict = self.find_all_packages(base_folder, scan_folder.capitalize())

        # Figure out the diff between 'all' and 'cached'
        new_packages: Dict[str, List] = dict()
        for file_name, data in all_packages_dict.items():
            cached_package_data = cached_packages.get(file_name, None)
            if cached_package_data == data:
                # package already in cache
                continue
            new_packages.update({file_name: data})

        # Figure out the diff between 'all' and 'cached' to delete removed packages
        # Duplicate GUIDs will return 2-n files and if one has been deleted it may cause issues for other mods trying to read them
        if t == GUIDStoreType.MODS:
            _missing_packages: Set = set()
            for b64_filename in cached_packages.keys():
                filename = self.get_folder_file_name_from_b64_short(base_folder, b64_filename)
                if os.path.exists(filename):
                    continue
                _missing_packages.add(b64_filename)
            if _missing_packages:
                log.debug(f"Removing {len(_missing_packages)} missing '{scan_folder.capitalize()}' packages from cache.")
                for missing_package in _missing_packages:
                    del cached_packages[missing_package]
                    try:
                        del cached_data[missing_package]
                    except:
                        pass
                if new_packages:
                    gs.save(t)  # t = GUIDStoreType.MODS, processing of the new packages will create a pretty file
                else:
                    gs.save(t, pretty=True)

        DumpGUIDs.on_zone_loaded_message += f"Found {len(new_packages)} new/modified '{scan_folder.capitalize()}' files.\n"
        log.debug(f"Found {len(new_packages)} new/modified '{scan_folder.capitalize()}' files.")

        new_packages_filename = os.path.join(ts4f.data_folder, f"new_{scan_folder}_filename_info.dict")
        if new_packages:
            gs.write_dict(new_packages_filename, new_packages, pretty=True)
        else:
            try:
                os.remove(new_packages_filename)
            except:
                pass

        process_on_startup = config.get('process_on_startup', False)
        lookup_names: bool = config.get('lookup_names', False)
        lookup_metadata: bool = config.get('lookup_metadata', False)
        lookup_lods: bool = config.get('lookup_lods', False)

        try:
            # noinspection PyUnresolvedReferences
            from guids.readers.cas_parts.cas_part_stream_reader import SCCASPartStreamReader
        except:
            lookup_metadata = False

        if new_packages and (process_on_startup or DumpGUIDs._enabled):
            log.debug(f"Processing '{scan_folder.capitalize()}' ...")
            self.dump_package_contents(
                t, base_folder, new_packages,
                cached_data, cached_packages,
                lookup_names, lookup_metadata, lookup_lods)

            gs =  GUIDStore()
            gs.load(GUIDStoreType.MODS)
            gs.load(GUIDStoreType.GAME)

    def __init__(self):
        DumpGUIDs.on_zone_loaded_message = ''  # For v2.0
        try:
            log.warn(f"{DumpGUIDs.warn_msg}")
            ts4f = TS4Folders(log, ModInfo.get_identity().base_namespace)
            os.makedirs(ts4f.data_folder, exist_ok=True)

            config = self.get_configuration(ts4f)
            config.update({'lookup_metadata': False})  # TODO Save in chunks with 10000 items to avoid huge dicts which can no longer be parsed
            config.update({'lookup_lods': False})  # TODO FIX 'ByteIndexList' object has no attribute 'parent_tgi_block_list'

            scan_on_startup: bool = config.get('scan_on_startup', False)
            process_on_startup: bool = config.get('process_on_startup', False)
            process_game_data = config.get('process_game_data', False)
            process_mods_data = config.get('process_mods_data', False)
            lookup_names: bool = config.get('lookup_names', False)
            lookup_metadata: bool = config.get('lookup_metadata', False)
            lookup_lods: bool = config.get('lookup_lods', False)

            scan_folders: List[GUIDStoreType] = list()
            if process_mods_data:
                scan_folders.append(GUIDStoreType.MODS)
            if process_game_data:
                scan_folders.append(GUIDStoreType.GAME)
            if not (process_game_data or process_mods_data):
                log.debug(f"Early exiting. (process_game_data: {process_game_data}; process_mods_data: {process_mods_data})")
                return

            if not (scan_on_startup or process_on_startup or DumpGUIDs._enabled):
                DumpGUIDs._enabled = True
                log.debug(f"Early exiting. (scan_on_startup: {scan_on_startup}; process_on_startup: {process_on_startup}; DumpGUIDs._enabled: {DumpGUIDs._enabled})")
                return

            for scan_folder in scan_folders:
                self.process_folder(ts4f, scan_folder, config)

            # After the initial call enable DumpGUIDs.
            DumpGUIDs._enabled = True

        except Exception as e:
            log.error(f"Initialization error '{e}'")

    @staticmethod
    def get_b64_short_folder_file_name(base_folder: str, folder_file_name: str) -> str:
        """
        Convert the folder name (c:/Users/Ting Tong/Documents/Electronic Arts/The Sims 4/Mods/Little/Britain.package) to a base64 encoded sting.
        Saving it to a dict later makes sure that it can be read later without hitting issues with meta characters used to store data.
        Also the 'base_folder' part and '.package' are removed to store only 'Little/Britain' as 'TGl0dGxlL0JyaXRhaW4='.
        Set base_folder to '' to exclude it.
        :param base_folder:
        :param folder_file_name:
        :return:
        """

        if base_folder == '':
            len_prefix = 0
        else:
            _base_folder = os.path.normpath(base_folder)
            len_prefix = len(_base_folder) + len(os.sep)

        suffix = '.package'
        len_suffix = len(suffix)

        _folder_file_name = os.path.normpath(folder_file_name)
        short_folder_file_name = _folder_file_name[len_prefix:-len_suffix]

        short_folder_file_name_b64 = base64.b64encode(short_folder_file_name.encode('utf-8')).decode('ascii')
        return short_folder_file_name_b64

    @staticmethod
    def get_folder_file_name_from_b64_short(base_folder: str, short_folder_file_name_b64: str) -> str:
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

    def find_all_packages(self, base_folder: str, folder_info: str = 'Game') -> Dict[str, List[int]]:
        """
        Scan 'base_folder' and all sub folders for '*.package' files and return them all.
        To identify the files size+ctime are used instead of creating a checksum which would take much longer.
        :param base_folder:
        :param folder_info:
        :return: A dict with '{file_name: [size, ctime], ...}'.
        """
        log.debug(f"find_all_packages('{base_folder}', '{folder_info}')", privacy_filter=True)
        configuration: Dict[str, List[int]] = dict()
        try:
            packages: Set[str] = set()
            if base_folder and os.path.exists(base_folder):
                packages = self.get_packages(base_folder, '*.package')
                log.debug(f"Found {len(packages)} '{folder_info}' packages.")
            else:
                log.warn(f"Can't read '{folder_info}' packages.")

            for file_name in packages:
                try:
                    file_name_b64 = self.get_b64_short_folder_file_name(base_folder, file_name)
                    size = os.path.getsize(file_name)
                    ctime = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(os.path.getctime(file_name)))
                    if folder_info == 'Game':
                        # Don't rely on ctime. It is often the same
                        sha1 = self._get_sha1(file_name, size)
                        if sha1:
                            ctime = sha1
                    configuration.update({file_name_b64: [size, ctime]})
                except:
                    log.warn(f"Error reading package file '{file_name}'.")
        except:
            log.warn(f"Error reading packages.")
        return configuration

    @staticmethod
    def _get_sha1(filename: str, size: int) -> str:
        """
        Return sha1 of the last 100 kB of files > 3 GB
        :param filename:
        :param size:
        :return:
        """
        sha1 = ''
        try:
            if size > 3_000_000:
                with open(filename, "rb") as f:
                    f.seek(size - 100_000)
                    b = f.read()
                    sha1 = hashlib.sha1(b).hexdigest()
        except:
            log.warn(f"Could not get sha1 for '{filename}'")
        return sha1

    def get_packages(self, base_folder: str, pattern: str = '*.package') -> Set[str]:
        """
        Recursively scan the directory for files matching the pattern.
        :param base_folder: The folder to start looking for "pattern" files. All sub folders will be scanned.
        :param pattern: The pattern to look for
        :return: a set with all matching files
        """
        packages: Set[str] = set()
        for root, dirs, files in os.walk(base_folder):
            for filename in fnmatch.filter(files, pattern):
                package_path = str(os.path.join(root, filename))
                packages.add(package_path)
        return packages

    def DELELTE_ME_read_cached_filename_info(self, filename) -> Dict[str, List[int]]:
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
        except:
            log.warn(f"Error reading '{filename}'.")
        return configuration

    def DELELTE_ME_write_cached_filename_info(self, filename: str, data: Union[None, Dict[str, List]] = None, pretty: bool = False):
        """
        Write a file with packages and their date/cname values.
        :param filename:
        :param data:
        :param pretty: Slower, newlines will be added.
        :return:
        """
        try:
            log.debug(f"write_cached_packages({filename}, {len(data.keys())}, {pretty})", privacy_filter=True)
            with open(filename, 'wt', encoding='utf-8') as fp:
                fp.writelines(f"# {DumpGUIDs.warn_msg}\n")
                if not pretty:
                    fp.write(f"{data}")
                else:
                    o = '{'
                    c = '}'
                    fp.writelines(f"{o}\n")
                    for b64_file_name, _data in data.items():
                        fp.writelines(f"\t# {self.get_folder_file_name_from_b64_short('', b64_file_name)}\n")
                        fp.writelines(f"\t'{b64_file_name}': {_data},\n")
                    fp.writelines(f"{c}\n")
                fp.writelines(f"\n# {DumpGUIDs.warn_msg}\n")
        except Exception as e:
            log.error(f"Error '{e}' writing '{filename}'.")

    def DELELTE_ME_read_cached_data(self, filename: str) -> dict:
        """
        Read the cached data with the package file names and their packages.
        :param filename:
        :return:
        """
        configuration: Dict[str, Dict[int, str]] = dict()
        try:

            if os.path.isfile(filename):
                with open(filename, 'rt', encoding='utf-8') as fp:
                    data = fp.read()
                    configuration = ast.literal_eval(data)
        except Exception as e:
            log.warn(f"Error '{e}' reading '{filename}'.")
        return configuration

    def DELELTE_ME_write_cached_data(self, filename: str, data: dict, pretty: bool = False):
        """
        Write the cached data with the package file names and their packages.
        :param filename:
        :param data:
        :param pretty: Slower, newlines will be added.
        :return:
        """
        try:
            log.debug(f"write_cached_data({filename}, {len(data.keys())}, {pretty})")
            with open(filename, 'wt', encoding='utf-8') as fp:
                fp.writelines(f"# {DumpGUIDs.warn_msg}\n")
                if not pretty:
                    fp.write(f"{data}")
                else:
                    o = '{'
                    c = '}'
                    fp.writelines(f"{o}\n")
                    for file_name, _data in data.items():
                        fp.writelines(f"\t# {self.get_folder_file_name_from_b64_short('', file_name)}\n")
                        fp.writelines(f"\t'{file_name}': {o}\n")
                        for guid, __data in _data.items():
                            fp.writelines(f"\t\t{guid}: {__data},\n")
                        fp.writelines(f"\t{c},\n")
                    fp.writelines(f"{c}\n")
                fp.writelines(f"\n# {DumpGUIDs.warn_msg}\n")
        except Exception as e:
            log.error(f"Error '{e}' writing '{filename}'.")

    def dump_package_contents(
            self, t: GUIDStoreType, base_folder: str, new_packages: Dict[str, List[int]],
            cached_data, cached_packages,
            lookup_names: bool = False, lookup_metadata: bool = False, lookup_lods: bool = False):

        """
        :param t:
        :param base_folder: The folder to look for the files in 'new_packages'
        :param new_packages: List with filenames to be read. The data is used for cached_packages_filename/cached_packages.
        :param cached_data: Currently existing GUID values.
        :param cached_packages: Currently existing cached files values.
        :param lookup_names: Set to True to enable name extraction of .package files. This takes a little longer as the package content is read.
        :param lookup_metadata: Set to True to enable name and metadata extraction of .package files. This takes longer as the package content is read and processed.
        :param lookup_lods: Read the LOD metadata, this will take even longer.
        :return:
        """
        log.debug(f"cached_data: {len(cached_data)}")
        log.debug(f"cached_packages: {len(cached_packages)}")
        total_files = len(new_packages)

        '''
        REMOVE big_cached_data
        big_cached_data = {}
        if lookup_metadata or lookup_lods:
            pass
            # TODO load data into 'big_cached_data'
        '''
        read_files = 0
        dbpf_parser = DBPFParser()
        _time = time.time()
        try:
            for b64_file_name, data in new_packages.items():
                try:
                    file_name = self.get_folder_file_name_from_b64_short(base_folder, b64_file_name)
                    file_mbs = os.path.getsize(file_name) / 1_000_000
                    log.debug(f"Processing file '{read_files}/{total_files}' '{file_name}' ({file_mbs:.1f} MB)...", privacy_filter=True)
                    read_files += 1

                    with open(file_name, "rb") as f:
                        # Reading the whole (up to 2 GB) file into the IO cache.
                        # This will avoid reading chunks from disk later and hopefully file lock issues.
                        f.read()

                    id_name_dict, failures = dbpf_parser.read_package_items(file_name, ResourceTypes.CAS_PART, lookup_names=lookup_names, lookup_metadata=lookup_metadata, lookup_lods=lookup_lods)
                    if id_name_dict:
                        cached_data.update({b64_file_name: id_name_dict})
                        '''
                        REMOVE big_cached_data
                        if lookup_metadata or lookup_lods:
                            for part_id, data in id_name_dict.items():   # Dict[part_id, Dict[str, Any]
                                dlc_name = data.get('dlc')
                                dlc_data = big_cached_data.get(dlc_name, {})
                                if (part_id not in dlc_data.keys()) or ('Delta' in file_name) or ('delta' in file_name):
                                    # This is either a new key or a 'Delta' package.
                                    dlc_data.update(id_name_dict)  # Add / Replace the key
                                    big_cached_data.update({dlc_name: dlc_data})  # Dict[DLC, Dict[part_id, Dict[str, Any]]]
                        else:
                            cached_data.update({b64_file_name: id_name_dict})
                        '''

                    # Add entry to the cached files
                    cached_packages.update({b64_file_name: data})
                    _dt = time.time() - _time
                    if _dt > 60:
                        log.debug("Writing to cache (fast)")
                        GUIDStore().update(t, cached_data, cached_packages)
                        GUIDStore().save(t)
                        _time = time.time()
                except Exception as e:
                    log.warn(f"Oops: {e}")

        except Exception as ex:
            log.warn(f"Oops: {ex}")

        log.debug("Writing to cache ...")
        log.debug(f"cached_data: {len(cached_data)}")
        log.debug(f"cached_packages: {len(cached_packages)}")
        # Write to disk
        GUIDStore().update(t, cached_data, cached_packages)
        GUIDStore().save(t, pretty=True)

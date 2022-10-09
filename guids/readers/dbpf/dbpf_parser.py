#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2022 https://github.com/Oops19
#
# Includes code from andrew https://sims4studio.com/thread/15145/started-python-scripting?page=4 and https://github.com/andrew-tavera/dbpf-reader-py
# License: Creative Commons Zero v1.0 Universal
# © andrew-tavera


import io
import os
import struct
import time
from typing import Tuple, Dict, Union


from guids.enums.resource_types import ResourceTypes
from guids.modinfo import ModInfo

from guids.readers.dbpf.dbpf_reader import DBPFReader
from s4cl.utils.uncommon_log import UnCommonLog  # TODO
log: Union[None, UnCommonLog] = UnCommonLog(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name)


class DBPFParser:
    def __init__(self):
        pass

    def read_package_items(self, filename_dbpf: str, resource_type: ResourceTypes, lookup_names: bool = False, lookup_metadata: bool = False, lookup_lods: bool = False) -> Tuple[Dict[int, Dict], int]:
        """

        :param lookup_lods:
        :param lookup_metadata:
        :param filename_dbpf: The Package file to read
        :param resource_type: The Resource Type to filter (eg CAS_PART or CLIP_HEADER)
        :param lookup_names: Set to False to disable reading of the .package to query the name. Then only the package dictionary will be read.
        :return: Tuple with 'Dict with GUIDs: Names,' and 'error-counter'
        """
        id_name_dict: Dict[int, Dict] = dict()
        failures: int = 0
        _time = time.time()
        for t, g, i, load_func in DBPFReader.read_package(filename_dbpf, type_filter={resource_type, ResourceTypes.S4S_MPM}):
            try:
                _dt = time.time() - _time
                if _dt > 10:
                    _time = time.time()
                    log.debug(f"\t\titem '{DBPFReader.index_entry}/{DBPFReader.index_entry_count}'")

                if lookup_metadata or lookup_lods:
                    if t == ResourceTypes.CAS_PART:
                        try:
                            # noinspection PyUnresolvedReferences
                            from guids.readers.cas_parts.cas_part_stream_reader import SCCASPartStreamReader
                            # noinspection PyUnresolvedReferences
                            from guids.dtos.cas_parts.cas_part_data import SCCASPartData
                            # noinspection PyUnresolvedReferences
                            from guids.dtos.resource_key import ResourceKey
                            with io.BytesIO(load_func()) as resource:
                                d: SCCASPartData = SCCASPartStreamReader.read_cas_part_from_stream(resource, filename_dbpf, ResourceKey(t, g, i), lookup_lods=lookup_lods)
                                dlc = self.get_dlc_requirement(filename_dbpf, d.cas_part_raw_display_name)
                                name = d.cas_part_raw_display_name.replace("'", "´")
                                id_name_dict.update({
                                    i: {
                                        # 'file': d.file_name,
                                        # 'tgi': d.tgi,
                                        'name': name,
                                        'dlc': dlc,
                                        'body_type': d.body_type,
                                        'species': d.species,
                                        'ages': d.available_for_ages,
                                        'genders': d.available_for_genders,
                                        'tags': d.part_tags,
                                        'colors': d.swatch_colors
                                    }
                                })
                        except Exception as e:
                            log.error(f"Error '{e}'")
                    elif t == ResourceTypes.S4S_MPM:
                        name = 'S4S Merged Package Manifest'
                        id_name_dict.update({i: {'name': name}})

                elif lookup_names:
                    if t == ResourceTypes.S4S_MPM:
                        name = 'S4S Merged Package Manifest'
                        id_name_dict.update({i: {'name': name}})
                    elif t == ResourceTypes.CAS_PART:
                        with io.BytesIO(load_func()) as resource:
                            res_name = DBPFParser.get_name_CAS_PART(resource)
                            name = res_name.replace("'", "´")
                            id_name_dict.update({i: {'name': name}})
                    elif t == ResourceTypes.CLIP_HEADER:
                        with io.BytesIO(load_func()) as resource:
                            res_name = DBPFParser.get_name_CAS_PART(resource)
                            name = res_name.replace("'", "´")
                            id_name_dict.update({i: {'name': name}})
                    else:
                        pass
                else:
                    id_name_dict.update({i: {}})
            except Exception as ex:
                log.error(f"get_package_items() Bad key: {g:x} {i:x} {t:x} in {filename_dbpf} ({ex}", throw=True)
                failures += 1
        return id_name_dict, failures

    @staticmethod
    def get_dlc_requirement(file_name: str, name: str):
        try:
            dlc = file_name.rsplit(os.sep, 2)[1]  # '.../Origin/The Sims 4/Delta/GP02/ClipHeader.package'
            if len(dlc) == 4:
                if dlc[:2] in ['EP', 'GP', 'SP', 'FP'] and dlc[2:].isdecimal():
                    return dlc
        except:
            pass
        try:
            dlc = name.split('_', 1)[1][:4]  # 'nn..._EP01...'
            if dlc[:2] in ['EP', 'GP', 'SP', 'FP'] and dlc[2:].isdecimal():
                return dlc
        except:
            pass
        try:
            dlc = name.split('_', 2)[2][:4]  # '[Author]_nn..._EP01...'
            if dlc[:2] in ['EP', 'GP', 'SP', 'FP'] and dlc[2:].isdecimal():
                return dlc
        except:
            pass
        return 'BASE'

    # noinspection PyPep8Naming
    @staticmethod
    def get_name_CAS_PART(resource):
        # https://github.com/s4ptacle/Sims4Tools/blob/fff19365a12711879bad26481a393a6fbc62c465/s4pi%20Wrappers/CASPartResource/CASPartResource.cs
        # https://github-wiki-see.page/m/Kuree/Sims4Tools/wiki/0x034AEECB
        # SKIP 0x04 Version  # this.version = r.ReadUInt32();
        # SKIP 0x04  TGI list (Type Group Index)  # this.TGIoffset = r.ReadUInt32() + 8;
        # SKIP 0x04 presets  # this.presetCount = r.ReadUInt32();
        # BYTE[] count of string
        b_text = b''
        text_length = 0
        try:

            resource.seek(0x0c, io.SEEK_SET)
            b = resource.read(1)  # 1 byte according to doc
            text_length: int = int.from_bytes(b, byteorder='big')
            if text_length > 127:
                b = resource.read(1)
                text_length2: int = int.from_bytes(b, byteorder='big')
                text_length = (text_length2 << 7) | (text_length & 127)

            b_text = resource.read(text_length)
            text = b_text.decode(encoding='utf-16be')
            return text
        except Exception as e:
            text = f"Error({e} for {b_text} with len {text_length})"
        return text

    # noinspection PyPep8Naming
    @staticmethod
    def get_name_CLIP_HEADER(resource):
        # SKIP a lot of unknown things
        resource.seek(0x38, io.SEEK_SET)
        text_length: int = struct.unpack('i', resource.read(4))[0]
        text: str = resource.read(text_length).decode('ascii')
        return text

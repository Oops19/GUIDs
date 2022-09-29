#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2022 https://github.com/Oops19
#
# Includes code from andrew https://sims4studio.com/thread/15145/started-python-scripting?page=4 and https://github.com/andrew-tavera/dbpf-reader-py
# License: Creative Commons Zero v1.0 Universal
# © andrew-tavera


import io
import struct
import zlib
from typing import Iterator, Tuple, Callable, Set
from s4cl.utils.uncommon_log import UnCommonLog  # TODO
from guids.modinfo import ModInfo  # TODO
log: UnCommonLog = UnCommonLog(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name)  # TODO


class DBPFReader:
    """
    This class reads dbpf (.package) files and returns tgi and a function to read data for each item in the index.
    The items can be limited to specific types like GuidTypes.CLIP_HEADER and/or GuidTypes.CAS_PART
    Usage:
    resource_types = {GuidTypes.CAS_PART, }
    for t, g, i, load_func in DBPFReader.read_package(filename_dbpf, type_filter=resource_types):
        with io.BytesIO(load_func()) as resource:
            .. = resource.read(..)
    """
    index_entry_count = 0
    index_entry = 0

    @staticmethod
    def read_package(filename_dbpf: str, type_filter: Set, ) -> Iterator[Tuple[int, int, int, Callable[[], bytes]]]:
        """
        Read a DBPF filename_dbpf file.
        :param filename_dbpf: The file name
        :param type_filter: A set of types to pre-filter the results
        :return:
        """
        type_filter = set() if not type_filter else type_filter
        with open(filename_dbpf, 'rb') as stream:
            def u32() -> int:
                return struct.unpack('I', stream.read(4))[0]

            # 1st bytes === 'DBPF' - .filename_dbpf file format
            # https://wiki.sc4devotion.com/index.php?title=DBPF
            # stream.seek(0, io.SEEK_SET) - not needed
            tag = stream.read(4).decode('ascii')
            assert tag == 'DBPF'

            stream.seek(32, io.SEEK_CUR)  # relative read to 36
            # stream.seek(36, io.SEEK_SET)  # 36 == pos of Index entry count
            index_entry_count = u32()
            DBPFReader.index_entry_count = index_entry_count
            stream.seek(24, io.SEEK_CUR)  # relative read to 64
            # stream.seek(64, io.SEEK_SET)  # 64 == pos of Index offset
            index_offset = u32()
            stream.seek(index_offset, io.SEEK_SET)  # Read the index
            index_flags: int = u32()
            # https://wiki.sc4devotion.com/index.php?title=DBPF_Source_Code
            # https://wiki.sc4devotion.com/images/9/94/DBPF_File_Format_v2.0.png
            # https://modthesims.info/archive/index.php?t-618074.html - {0x0000: "Uncompressed", 0xfffe: "Streamable compression", 0xffff: "Internal compression", 0xffe0: "Deleted record", 0x5a42: "ZLIB"}

            # 100% andrew, code is hard to understand but it works. Comments added by Oops19.
            # Read 'Entry Type' of TGI Block (Type Group Index)
            static_t: int = u32() if index_flags & 0x1 else 0
            static_g: int = u32() if index_flags & 0x2 else 0
            static_i: int = u32() << 32 if index_flags & 0x4 else 0
            static_i |= u32() if index_flags & 0x8 else 0

            for index_entry in range(index_entry_count):
                DBPFReader.index_entry = index_entry
                t = static_t if index_flags & 0x1 else u32()
                g = static_g if index_flags & 0x2 else u32()
                instance_hi = static_i >> 32 if index_flags & 0x4 else u32()
                instance_lo = static_i & 0xFFFFFFFF if index_flags & 0x8 else u32()
                i = (instance_hi << 32) + instance_lo                                   # Instance ID (?)
                offset: int = u32()                                                     # File location
                sz: int = u32()                                                         # File size (raw)
                file_size: int = sz & 0x7FFFFFFF                                        # strip high-bit(file size) ==> file size
                stream.seek(4, io.SEEK_CUR)                                             # File size (Decompressed) - do not read
                compressed: bool = sz & 0x80000000 > 0                                  # if high-bit(file size) ==> compressed
                compression_type: int = 0
                if compressed:
                    compression_type = struct.unpack('H', stream.read(2))[0]            # Compression flag (0x0000==No, >0==Yes)
                    stream.seek(2, io.SEEK_CUR)                                         # Unknown (0x0001)

                if compression_type not in (0x0000, 0x5A42):                            # Uncompressed, ZLIB
                    continue

                def load_func() -> bytes:
                    pos = stream.tell()                                                 # get current fp position
                    stream.seek(offset, io.SEEK_SET)                                    # set to 'offset'
                    data = stream.read(file_size)                                       # read the file
                    stream.seek(pos, io.SEEK_SET)                                       # restore fp position
                    return zlib.decompress(data) if compression_type == 0x5A42 else data

                if len(type_filter) == 0 or t in type_filter:
                    yield t, g, i, load_func

from sims4communitylib.mod_support.common_mod_info import CommonModInfo


class ModInfo(CommonModInfo):
    _FILE_PATH: str = str(__file__)

    @property
    def _name(self) -> str:
        return 'GUIDs'

    @property
    def _author(self) -> str:
        return 'o19'

    @property
    def _base_namespace(self) -> str:
        return 'guids'

    @property
    def _file_path(self) -> str:
        return ModInfo._FILE_PATH

    @property
    def _version(self) -> str:
        return '0.1.16'


'''
v0.1.16
    Fixed a few glitches
v0.1.15
    Added config.dict
v0.1.14
    Moved README into 'guids/'
v0.1.13
    Initial public release
v0.1.12
    More cleanup
    Fixed swapped replacement of '{' and '|' to Fullwidth Unicode from sim name to filename
v0.1.11
    Fixed another bug with the pretty printed files.
    Change the max. package file size to include with 'o19.guids.max', default is now 100 MB (was 50 MB).
    Change the dump command to 'o19.guids.zip_outfit'
v0.1.10
    Add outfit exists check to code unless S4CL 2.3 is GA
    Add info.txt to ZIP
v0.1.10
    More cleanup
v0.1.9
    Cleanup
v0.1.8
    Refactor GUIDStore
v0.1.7
    Refactor GUIDStore (in progress, stable)
v0.1.6
    Add a log file to the ZIP.
v0.1.5
    Proper unicode support for the ZIP file.
    Fixed the name of the ZIP file.
v0.1.4
    Start GUIDs only one time
v0.1.3
    Remove deleted files from cache
v0.1.2
    Added mod_data/guids/cached_game_*.dict for a faster startup  
v0.1.0
    Added GUIDStore properties
    Removed all more advanced code
v0.0.7
    Cleanup
v0.0.6
    Fix cache on update. Old values should not be deleted except if the file is to big for 'ast'.
v0.0.5
    Added code (c) ColonolNutty to extract CAS_PART data
v0.0.4
    Added some docstrings.
v0.0.3
    Fixed a bug with TS4_GAME_FOLDER not set.
v0.0.2
    Removed threading support.
    Start delay (first run only) about 10-120 seconds depending on the number of installed DLCs and Mods.
    Start delay after adding Mods about 1-15 seconds.
    Start delay after a game update about 10-30 sesonds
v0.0.1
    Initial version
'''

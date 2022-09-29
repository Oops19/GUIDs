#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2022 https://github.com/Oops19
#


from __future__ import unicode_literals

import os
import re
import time
from typing import List, Dict
from zipfile import ZipFile, ZIP_DEFLATED
from os.path import basename

from guids.dump_guids import DumpGUIDs
from guids.guid_store import GUIDStore
from guids.libraries.ts4folders import TS4Folders
from s4cl.utils.common_outfit_category import OutfitCategory, OutfitIndex
from sims.occult.occult_enums import OccultType
from sims.sim_info import SimInfo
from sims4communitylib.services.commands.common_console_command import CommonConsoleCommand, CommonConsoleCommandArgument
from sims4communitylib.services.commands.common_console_command_output import CommonConsoleCommandOutput

from sims4communitylib.utils.cas.common_outfit_utils import CommonOutfitUtils
from sims4communitylib.utils.sims.common_occult_utils import CommonOccultUtils
from sims4communitylib.utils.sims.common_sim_name_utils import CommonSimNameUtils
from sims4communitylib.utils.sims.common_sim_utils import CommonSimUtils

from s4cl.utils.uncommon_log import UnCommonLog  # TODO
from guids.modinfo import ModInfo  # TODO
log: UnCommonLog = UnCommonLog(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name)  # TODO


class ZipOutfit:
    max_include_file_size = 100  # MB

    def __init__(self):
        self.sim_definition = dict()
        self.part_ids = set()
        self.ts4f = TS4Folders(log, ModInfo.get_identity().base_namespace)
        self.info_filename = os.path.join(self.ts4f.data_folder, 'info.txt')

    @staticmethod
    def get_sim_name(sim_info: SimInfo) -> str:
        return f"{CommonSimNameUtils.get_first_name(sim_info)}#{CommonSimNameUtils.get_last_name(sim_info)}"

    def process_occults(self, sim_info: SimInfo, category: int = -2, index: int = -2):
        log.debug(f"process_occults({sim_info}, {category}, {index})")
        self.sim_definition.update({'sim_name': self.get_sim_name(sim_info)})
        occult_types: List[OccultType] = list()
        for occult_type in CommonOccultUtils.get_all_occult_types_for_sim_gen(sim_info):
            occult_types.append(occult_type.value)
            occult_sim_info = CommonOccultUtils.get_occult_sim_info(sim_info, occult_type)
            if occult_type == OccultType.HUMAN:  # TODO fix after S4CL fix
                occult_sim_info = sim_info
            if occult_sim_info:
                # OccultType.WITCH has no occult outfit, occult_sim_info == None
                self.process_outfit_category(occult_sim_info, occult_type, category, index)
        self.sim_definition.update({'occult_types': occult_types})

    def process_outfit_category(self, sim_info: SimInfo, occult_type: OccultType, category: int = -2, index: int = -2):
        log.debug(f"process_outfit_category({sim_info}, {occult_type}, {category}, {index})")
        try:
            OutfitCategory(category)
            self.process_outfit_index(sim_info, occult_type, category, index)
        except:
            for _category in OutfitCategory.__members__.values():
                if _category == OutfitCategory.CURRENT_OUTFIT:
                    continue
                self.process_outfit_index(sim_info, occult_type, _category.value, index)

    def process_outfit_index(self, sim_info: SimInfo, occult_type: OccultType, category: int = -2, index: int = -2):
        log.debug(f"process_outfit_index({sim_info}, {occult_type}, {category}, {index})")
        try:
            OutfitIndex(index)
            self.process_sim(sim_info, occult_type, category, index)
        except:
            for _index in OutfitIndex.__members__.values():
                self.process_sim(sim_info, occult_type, category, _index.value)

    def process_sim(self, sim_info: SimInfo, occult_type: OccultType, category: int = -2, index: int = -2):
        log.debug(f"process_sim({sim_info}, {occult_type}, {category}, {index})")
        if category == -1:
            category = CommonOutfitUtils.get_current_outfit_category(sim_info)
        if index == -1:
            index = CommonOutfitUtils.get_current_outfit_index(sim_info)
        category_and_index = (category, index)
        if not CommonOutfitUtils.has_outfit(sim_info, category_and_index):  # TODO remove for S4CL 2.3+
            log.debug(f"Sim has no outfit {category_and_index}")
            return
        body_type_and_part_ids: dict = CommonOutfitUtils.get_outfit_parts(sim_info, category_and_index)
        part_ids = set(body_type_and_part_ids.values())
        log.debug(f"part_ids = {part_ids}")
        if part_ids:
            self.part_ids.update(part_ids)
            outfits = self.sim_definition.get('outfits', dict())
            outfits.update({f"{occult_type.value}.{category}.{index}": body_type_and_part_ids})
            self.sim_definition.update({'outfits': outfits})

    def create_zip(self, sim_name: str):
        if not self.part_ids:
            return

        ts4f = TS4Folders(log, ModInfo.get_identity().base_namespace)
        gs = GUIDStore()

        game_data_mini = gs.game_data_mini
        #log.debug(f"game_data_mini {len(game_data_mini)}")
        #log.debug(f"game_data {len(GUIDStore().game_data)}")
        dlcs = set()
        dlc_items: Dict[int, str] = {}
        for part_id in self.part_ids:
            if part_id in gs.game_data_part_ids:
                for b64_filename, data in gs.game_data_mini.items():
                    if part_id in data:
                        filename = DumpGUIDs.get_folder_file_name_from_b64_short('', b64_filename)  # not yet ts4f.ts4_folder_game
                        if filename[:5] == 'Delta':
                            f = filename[6:].split(f'{os.sep}', 1)[0]  # remove '^Delta/'
                        else:
                            f = filename.split(f'{os.sep}', 1)[0]
                        if f == 'Data':
                            continue
                        dlcs.add(f)
                        try:
                            part_name = gs.game_data.get(b64_filename).get(part_id).get('name')
                        except Exception as e:
                            part_name = f"Error({e})"
                        dlc_items.update({part_id: part_name})
                        break
        if dlc_items:
            log.warn(f"Found '{dlc_items}' items from these DLCs: {dlcs}")
            self.sim_definition.update({'dlcs': dlcs})
            self.sim_definition.update({'skipped_dlc_items': dlc_items})

        items = {}
        overrides = set()
        for part_id in self.part_ids:
            if part_id in gs.mods_data_part_ids:
                if part_id in gs.game_data_part_ids:
                    overrides.add(part_id)
                for b64_filename, data in gs.mods_data_mini.items():
                    if part_id in data:
                        filename = DumpGUIDs.get_folder_file_name_from_b64_short('', b64_filename)  # not yet ts4f.ts4_folder_mods
                        current_files = items.get(part_id, [])
                        current_files.append(filename)
                        items.update({part_id: current_files})
                    # don't break, there may be duplicates / unmerged packages
        # log.debug(f"part_ids in these files: {items}")
        self.sim_definition.update({'override_part_ids': overrides})

        new_items = {}
        max_file_size_mb = ZipOutfit.max_include_file_size * 1_000_000
        for part_id, filenames in items.items():
            file_size = 2 ** 40  # 1000 MB - Files should be < 2 GB
            filename = ''
            smallest_file = ''
            for filename in filenames:
                try:
                    _filename = os.path.join(ts4f.mods_folder, filename)  # absolute path to read the file
                    _file_size = os.path.getsize(_filename)
                    if _file_size < file_size:
                        file_size = _file_size
                        smallest_file = filename
                except:
                    _filename = os.path.join('', filename)
                    log.error(f"Could not read '{_filename}'", None, throw=False)
            if file_size > max_file_size_mb:
                in_merged_package = False
                try:
                    b64_filename = DumpGUIDs.get_b64_short_folder_file_name('', filename )
                    part_name = gs.mods_data.get(b64_filename).get(part_id).get('name')
                    if gs.mods_data.get(b64_filename).get(0):
                        in_merged_package = True
                except Exception as e:
                    part_name = f"Error({e})"
                log.warn(f"Skipping '{filename}' with {file_size} bytes. Part '{part_id}' ({part_name}) will be missing.")
                skipped = self.sim_definition.get('skipped', dict())
                skipped.update({
                    filename: {
                        'file_size': file_size,
                        'part_id': part_id,
                        'part_name': part_name,
                        'in_merged_package': in_merged_package
                    }
                })
                self.sim_definition.update({'skipped': skipped})
                continue
            new_items.update({part_id: smallest_file})
        log.debug(f"part_ids in these small files: {new_items}")

        gs.write_dict(self.info_filename, self.sim_definition, pretty=True, with_filenames=False)

        new_items.update({-3: self.info_filename})  # Add it to new_items so it will be zipped.
        try:
            # Python needs unicode_literals to write the file name.
            # from __future__ import unicode_literals
            # Linux supports: '~"#%&:{}\' and '\*', '\<', '\>', '\?', '\|' while '/' is not supported
            _sim_name = sim_name \
                .replace('~', '～') \
                .replace('"', '＂') \
                .replace('#', '＃') \
                .replace('%', '％') \
                .replace('&', '＆') \
                .replace(':', '：') \
                .replace('{', '｛') \
                .replace('}', '｝') \
                .replace('*', '＊') \
                .replace('<', '＜') \
                .replace('>', '＞') \
                .replace('?', '？') \
                .replace('/', '／') \
                .replace('\\', '＼') \
                .replace('|', '｜')
            _sim_name = os.path.join(ts4f.data_folder, f"Outfits_for_{_sim_name}_{time.strftime('%Y.%m.%dT%H.%M.%S', time.localtime(time.time()))}.zip")
            with ZipFile(os.path.join(ts4f.data_folder, _sim_name), 'w', compression=ZIP_DEFLATED) as zipObj:
                for filename in set(new_items.values()):
                    f = os.path.join(ts4f.mods_folder, filename)  # absolute path to read the file
                    zipObj.write(f, basename(f))    
        except:
            # This should never happen.
            # Make sure that the sim name uses valid ASCII characters
            _sim_name = re.sub(r'[^a-zA-Z0-9 ]+', '_', sim_name)
            _sim_name = os.path.join(ts4f.data_folder, f"Outfits_for_{_sim_name}_{time.strftime('%Y.%m.%dT%H.%M.%S', time.localtime(time.time()))}.zip")
            with ZipFile(os.path.join(ts4f.data_folder, _sim_name), 'w', compression=ZIP_DEFLATED) as zipObj:
                for filename in set(new_items.values()):
                    f = os.path.join(ts4f.mods_folder, filename)  # absolute path to read the file
                    zipObj.write(f, basename(f))


@CommonConsoleCommand(
    ModInfo.get_identity(), 'o19.guids.max', 'Set the maximum package file to include in ZIP.',  # 'guids.help' will print out this
    command_arguments=(
            CommonConsoleCommandArgument('size', 'number', 'The file size in MB (default: 100).', is_optional=True, default_value='-2'),
    )
)
def o19_cmd_guids_max_pacakge_size(output: CommonConsoleCommandOutput, size: int = 100):
    output(f"Changing max. package file size to be included from {ZipOutfit.max_include_file_size} MB to {size} MB.")
    ZipOutfit.max_include_file_size = size


@CommonConsoleCommand(
    ModInfo.get_identity(), 'o19.guids.zip_outfit', 'The elite zip file creator for outfits.',   # 'guids.help' will print out this
    command_arguments=(
            CommonConsoleCommandArgument('sim_info', 'Sim Id or Name', 'The Sim to check.', is_optional=True, default_value='Active Sim'),
            CommonConsoleCommandArgument('category', 'number', 'The outfit category [-2..12] (-2=all, -1=current, [0..12]=specific).', is_optional=True, default_value='-2'),
            CommonConsoleCommandArgument('index', 'number', 'The outfit index [-2..4] (-2=all, -1=current, [0..4]=specific).', is_optional=True, default_value='-2'),
    )
)
def o19_cmd_guids_zip_outfit(output: CommonConsoleCommandOutput, sim_info: SimInfo = None, category: int = -2, index: int = -2):
    try:
        output(f"o19_cmd_zip_outfit({sim_info}, {category}, {index})")
        log.debug(f"o19_cmd_zip_outfit({sim_info}, {category}, {index})")

        if sim_info is None:
            sim_info = CommonSimUtils.get_active_sim_info()

        zo = ZipOutfit()
        zo.process_occults(sim_info, category, index)
        log.debug(f"Parts: {zo.part_ids}")

        gs = GUIDStore()
        if gs.is_ready is False:
            log.debug(f"GUIDStore is not ready!")
            DumpGUIDs()
            log.debug(f"GUIDStore should now be ready!")
            log.debug(f"Mode/Game items: {len(GUIDStore._mods_data)} {len(GUIDStore._game_data)}")  # fixme gs.
            return

        sim_name = zo.get_sim_name(sim_info)
        zo.create_zip(sim_name)
        output(f"Done")

    except Exception as e:
        log.error(f"Oops: {e}", None, throw=True)


DumpGUIDs()

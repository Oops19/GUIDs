#  Game Unique IDs

This mod extracts file name information of CAS Parts from Package files.
It scans both the 'Game' and the 'Mods' folder. 

There are quite a few tools available to access these values of TS4 items. 
This mod does the same except that it runs in-game and provides a script API for other mods to query these items.

EA adds useful names, a lot of UGC contains bad names.
We might blame the creators of S4S and similar tools without proper support to choose a good name for the CAS Part. Anyhow a mod creator could still choose a good name and set the flags propery.


### Download
On GitHub there is only the small build available.
The 2 MB build with the version number of the game (eg 1.91.205) contains exactly the same code as the small build.
It contains most CAS Part names used by the 'Game' and DLCs. Using this version will speed up the startup process (about 2.5 minutes or much longer, depending on the used computer)

## Installation
The ZIP file should be extracted into the `The Sims 4` folder to make sure that the folder structure is set up correctly.
* All settings are read from `The Sims 4/mod_data/guids/`.
* The mod documentation (everything in `mod_documentation`) should also not be stores in `Mods`.
* The mod `guids.ts4cript` itself should be stored in `Mods` or in a sub folder. I highly recommend to store it in `_o19_` so you know who created it.

Unless not yet installed: Install [S4CL](https://github.com/ColonolNutty/Sims4CommunityLibrary/releases/latest) as this mod is required.
* I highly recommend to install the S4CL files into `_cn_` so you know who contributed this mod.

This mod has been tested with 1.91.205 (2022-09-13) and S4CL v2.3 (2022-09-xx).
It is expected to work with many older and upcoming releases of TS4 and S4CL.

### Configuration
The mod detects the location of the 'Mods' and 'Game' folder.
It reads the environment variables 'TS4_MODS_FOLDER' and 'TS4_GAME_FOLDER' which may be set to detect it.

The configuration file 'mod_data/guids/config.dict' allows to configure the data to be extracted.

The 'mod_data/guids' folder also stores the cached configuration. The mod includes 'cached_game*.dict' for game version 1.91.205.
This will speed up the start process by 2-10 minutes. 

### Starting TS4
The mod will read all packages in 'The Sims 4/Mods' and 'The Sims 4/Game/..'. This will take a few minutes, please be patient.
Especially after a game update the time may be high as indexing the data takes time.
Adding some CC will delay the start time for a few seconds.
If loading takes long locate your 'The Sims 4/mod_logs' folder and open 'GUIDs_Messages.txt' to check the progress.

### Security
* The mod logs folder names which may contain your local username. 
* It logs all mods (.package) files you have installed.
* All data is kept on your computer.
Please review log files before sharing them. Most log statements should replace the private data with '%USERPROFILE%', '%ProgramFiles%', '$HOME' already.

### Usage
As an API it does not provide any user interaction. There are currently no mods which require it.

## Cheat commands
The single available command is 'o19.guids.zip_outfit'.

It creates a ZIP file with all used outfits (similar to the 'Sims 4 Tray Importer').
It does not include files for buffs or traits. It skips files > 100 MB. These are usually merged files.

If no outfit-category is specified all outfits will be processed. (-1 = current, 0=Everyday, ..., 12)

If no outfit-index is specified all outfits of the category will be processed. (values: 0-4)

General usage:
* `'o19.guids.zip_outfit ["sim name" [outfit-category [outfit-index]]]'`
* `'o19.guids.zip_outfit'`: Get all outfits of the active sim
* `'o19.guids.zip_outfit "Ting Tong"'`: Get all outfits of Ting Tong.
* `'o19.guids.zip_outfit "Ting Tong" 0'`: Get all 'Everday' outfits of Ting Tong.
* `'o19.guids.zip_outfit "Ting Tong" 0 0'`: Get the 'Everday[0]' outfit of Ting Tong.
* `'o19.guids.zip_outfit "Ting Tong" -2 0'`: Get all [0] outfits of Ting Tong.

* `'o19.guids.max [size]'`: New max size in MB of packages to include. Default: 100
* `'o19.guids.max 15'`: Se the size to 15 MB, .package files bigger 15 MB will not be included in the ZIP.

Together with the ZIP file an 'info.txt' file is created and added to it. It contains a lot of useful information:
* `'sim_name': 'Ting#Tong',`: The sim name, first and last name are separated with '#' which is not a valid character within sim names.
* `'occult_types': [1]`: The occult types of the sim.
* `'dlcs': {'EP01', 'EP02', ...},`: The DLCs used for the outfit (not included in ZIP).
* `'skipped_dlc_items': {81835: 'yuHat_EP01BeanieSlouchy_Beige',}`: The DLC items with their name (not included in ZIP).
* `'override_part_ids': {148023, ...},`: Overrides of TS4 CAS Parts (eg better Teeth).
* `	'skipped': {...}`: Skipped items due to the file size, their file name, the name of the CAS Part item and whether it is located in a merged Package file which S4S should be able to unmerge.
* Outfits as '{occult}.{category}.{index}' with the CAS Part IDs.

This file can't be used to restore an outfit automatically while one may apply the CAS Parts manually.
It does not contain sim sliders, traits or buffs and can't be used to restore a sim.

#### Outfit Categories
* CURRENT_OUTFIT = -1
* EVERYDAY = 0
* FORMAL = 1
* ATHLETIC = 2
* SLEEP = 3
* PARTY = 4
* BATHING = 5
* CAREER = 6
* SITUATION = 7
* SPECIAL = 8
* SWIMWEAR = 9
* HOTWEATHER = 10
* COLDWEATHER = 11
* BATUU = 12


### Future / Private version
The private version of this mod is not behind a paywall, it is private and not available as UGC.

It supports extraction of flags like species, genders, occults, body type (top, bottom, ...), sub type (pants, skirt, shorts, ...), colors, ...

The amount of extracted data from the game and all mods is huge and will allow mods to select 'red pants (for) male aliens' and things like this.

Crunching down the amount of used data is still on the todo list and also the public implementation might still contain bugs which should be fixed first.

The storage format will very likely change.
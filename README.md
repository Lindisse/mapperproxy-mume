# mapperproxy mume
A mapper proxy for playing [MUME](http://mume.org "MUME Official Site") targeted towards the needs of blind players. It is entirely controlled by plain text commands, and offers some facilities such as pathfinding and room finding. It also comes with a high contrast GUI for visually impaired players, and a tiled one for sighted players.

![screenshot of the sighted GUI](tiles/screenshot.png?raw=true "screenshot of the sighted GUI")

## License And Credits
Mapper Proxy is licensed under the terms of the [Mozilla Public License, version 2.0.](https://www.mozilla.org/en-US/MPL/2.0/ "MPL2 official Site")
Mapper Proxy was originally created and is actively maintained by Nick Stockton.
Visually Impaired GUI contributed by Katalina Durden.
Sighted GUI and various additions contributed by Lindisse.

The tiles of the GUI for sighted players are distributed under the [CC-BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/legalcode "CC-BY-SA 3.0 official site") license. They are a modified version of [fantasy-tileset.png](https://opengameart.org/content/32x32-fantasy-tileset "fantasy-tileset page on OpenGameArt") originally created by [Jerome.](http://jerom-bd.blogspot.fr/ "Jerome old site")


## Installation
### As part of mud clients
Mume-mapperproxy is distributed as part of
[MUSHclient-MUME](https://github.com/nstockton/mushclient-mume/blob/master/README.md), and [tintin-MUME](https://github.com/nstockton/tintin-mume), which also provide scripts to play Mume more easily. Refer to these projects for an installation guide.

### Standalone installation
If you only need the mapperproxy, install the [Python interpreter,](https://python.org "Python Home Page") and make sure it's in your path before running this package.

## Mapper Proxy usage
### Manual start up
To start the mapper, run `python start.py` from the _mume-mapperproxy/_ directory. It accepts the following arguments:

- `-e` Start in emulation mode. The mapper does not connect to MUME.
- `-g [default|sighted]` Use a GUI. The default GUI is a high contrast one for visually impaired players. The sighted GUI uses png tiles.
- `-t` Text only mode (no GUI).
- `-f [normal|tintin|raw]` Select how the data from the server is transformed before being sent to the client. Default is "_normal_".

Once done, connect your client to `127.0.0.1`, port `4000`.

### Starting up from a client
It is possible to start the mapper directly from the client. Here is, for example, how to start it from a tintin+++ script, from the _mume-mapperproxy/_ directory:

```
#run {mapper} {python -B}
from mapper.main import main
#action {^MPICOMMAND:%1:MPICOMMAND$} {#mume {#system %1;#mapper continue}}
#gts
#mapper main(outputFormat="tintin", use_gui="sighted")
```

## Mapper Proxy commands
### Auto Mapping Commands
Auto mapping mode must be on for these commands to have any effect.

* autolink  --  Toggle Auto linking on or off. If on, the mapper will attempt to link undefined exits in newly added rooms.
* automap  --  Toggle automatic mapping mode on.
* automerge  --  Toggle automatic merging of duplicate rooms on or off.
* autoupdate  --  Toggle Automatic updating of room name/descriptions/dynamic descriptions on or off.

### Map Editing Commands
* doorflags [add|remove] [hidden|needkey|noblock|nobreak|nopick|delayed|reserved1|reserved2] [north|east|south|west|up|down]  --  Modify door flags for a given direction.
* exitflags [add|remove] [exit|door|road|climb|random|special|avoid|no_match] [north|east|south|west|up|down]  --  Modify exit flags for a given direction.
* ralign [good|neutral|evil|undefined]  --  Modify the alignment flag of the current room.
* ravoid [+|-]  --  Set or clear the avoid flag for the current room. If the avoid flag is set, the mapper will try to avoid the room when path finding.
* rdelete [vnum]  --  Delete the room with vnum. If the mapper is synced and no vnum is given, delete the current room.
* rlabel [add|delete|info|search] [label] [vnum]  --  Manage room labels. Vnum is only used when adding a room. Leave it blank to use the current room's vnum. Use rlabel info all to get a list of all labels.
* rlight [lit|dark|undefined]  --  Modify the light flag of the current room.
* rlink [add|remove] [oneway] [vnum] [north|east|south|west|up|down]  --  Manually manage links from the current room to room with vnum. If oneway is given, treat the link as unidirectional.
* rloadflags [add|remove] [treasure|armour|weapon|water|food|herb|key|mule|horse|packhorse|trainedhorse|rohirrim|warg|boat|attention|tower]  --  Modify the load flags of the current room.
* rmobflags [add|remove] [rent|shop|weaponshop|armourshop|foodshop|petshop|guild|scoutguild|mageguild|clericguild|warriorguild|rangerguild|smob|quest|any|reserved2]  --  Modify the mob flags of the current room.
* rnote [text]  --  Modify the note for the current room.
* rportable [portable|notportable|undefined]  --  Modify the portable flag of the current room.
* rridable [ridable|notridable|undefined]  --  Modify the ridable flag of the current room.
* rterrain [death|city|shallowwater|forest|hills|road|cavern|field|water|underwater|rapids|indoors|brush|tunnel|mountains|random|undefined]  --  Modify the terrain of the current room.
* rx [number]  --  Modify the X coordinate of the current room.
* ry [number]  --  Modify the Y coordinate of the current room.
* rz [number]  --  Modify the Z coordinate of the current room.
* savemap  --  Save modifications to the map to disk.
* secret [add|remove] [name] [north|east|south|west|up|down]  --  Add or remove a secret door in the current room.

### Searching Commands
* fdoor [text]  --  Search the map for rooms with doors matching text. Returns the closest 20 rooms to you based on the [Manhattan Distance.](https://en.wikipedia.org/wiki/Taxicab_geometry "Wikipedia Page On Taxicab Geometry")
* fname [text]  --  Search the map for rooms with names matching text. Returns the closest 20 rooms to you based on the [Manhattan Distance.](https://en.wikipedia.org/wiki/Taxicab_geometry "Wikipedia Page On Taxicab Geometry")
* fnote [text]  --  Search the map for rooms with notes matching text. Returns the closest 20 rooms to you based on the [Manhattan Distance.](https://en.wikipedia.org/wiki/Taxicab_geometry "Wikipedia Page On Taxicab Geometry")

### Path commands
* path [vnum|label] [nodeath|nocity|noshallowwater|noforest|nohills|noroad|nocavern|nofield|nowater|nounderwater|norapids|noindoors|nobrush|notunnel|nomountains|norandom|noundefined]  --  Print speed walk directions from the current room to the room with vnum or label. If one or more avoid terrain flags are given after the destination, the mapper will try to avoid all rooms with that terrain type. Multiple avoid terrains can be ringed together with the '|' character, for example, path ingrove noroad|nobrush.
* run [c|t] [vnum|label] [nodeath|nocity|noshallowwater|noforest|nohills|noroad|nocavern|nofield|nowater|nounderwater|norapids|noindoors|nobrush|notunnel|nomountains|norandom|noundefined]  --  Automatically walk from the current room to the room with vnum or label. If 'c' is provided instead of a vnum or label, the mapper will recalculate the path from the current room to the previously provided destination. If t (short for target) is given before the vnum or label, the mapper will store the destination, but won't start auto walking until the user enters 'run c'. If one or more avoid terrain flags are given after the destination, the mapper will try to avoid all rooms with that terrain type. Multiple avoid terrains can be ringed together with the '|' character, for example, run ingrove noroad|nobrush.
* step [label|vnum]  --  Move 1 room towards the destination room matching label or vnum.
* stop  --  Stop auto walking.

### Doors commands
* secretaction [action] [north|east|south|west|up|down]  --  Perform an action on a secret door in a given direction. This command is meant to be called from an alias. For example, secretaction open east.

### Miscellaneous Mapper Commands
* getlabel [vnum]  --  Returns the label or labels defined for the room with vnum. If no vnum is supplied, the current room's vnum is used.
* gettimer  --  Returns the amount of seconds since the mapper was started in an optimal format for triggering. This is to assist scripters who use clients with no time stamp support such as VIP Mud.
* gettimerms  --  Returns the amount of milliseconds since the mapper was started in an optimal format for triggering. This is to assist scripters who use clients with no time stamp support such as VIP Mud.
* rinfo [vnum|label]  --  Print info about the room with vnum or label. If no vnum or label is given, use current room.
* sync [vnum|label]  --  Manually sync the map to the room with vnum or label. If no vnum or label is given, mapper will be placed in an unsynced state, and will try to automatically sync to the current room.
* tvnum  --  Tell the vnum of the current room to another player.
* vnum  --  Print the vnum of the current room.

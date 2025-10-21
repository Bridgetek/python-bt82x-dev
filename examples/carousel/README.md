# Python BT82x Development Simple Rotating Menu Wheel Example

[Back](../README.md)

## Simple Rotating Menu Example

The `rotateselect.py` example demonstrates drawing a rotating selection wheel using a custom font, rotating graphics, and accessing the raw touch X,Y register. 

A "wheel" selection is drawn that shows multiple options at equidistant points on the circumferance of the circle. These options are represented by graphics symbols taken from the "MaterialSymbolsSharp-Regular_26_L4" font. This font contains Basic Latin, Latin-1 Supplemental (0x0020 to 0x00FF) and Private Use Area (0xE000 to 0xE8FF) glyphs.

The font is stored as a relocatable asset `.reloc` file and is loaded as an asset with the `CMD_LOADASSET` command.

Each character of the custom font can be rotated 

<!-- ![Segment Example](docs/rotateselect.png) -->

### Running the Example

The format of the command call to run `rotateselect` is as follows:

_MPSSE example:_
```
python rotateselect.py --connector ft232h 
```

_FT4222 example in single mode (--mode 0):_

```
python rotateselect.py --connector ft4222module 

```

_FT4222 example in dual mode (--mode 1) or quad mode (--mode 2):_

```
python rotateselect.py --connector ft4222module --mode 2

```

The number in the command line is used as a decimal number to display in the widgets.

## Files and Folders

The example contains a single file which comprises all the demo functionality.

| File/Folder | Description |
| --- | --- |
| [rotateselect.py](rotateselect.py) | Example source code file |
| [patch_rotate.py](patch_rotate.py) | Patch extension for memory allocation |
| assets/MaterialSymbolsSharp-Regular_26_L4.reloc | Font including graphics symbols (binary file) |
| [docs](docs) | Documentation support files |

# Python BT82x Development Simple Example

[Back](../README.md)

## Simple Example

The `simple.py` example demonstrates writing text on the screen. It parses arguments and uses them to determine the display list for the BT82x.

The demo will only write a string of text on the BT82x screen using an optionally specified font.

### Running the Example

The format of the command call is as follows:

_MPSSE example:_
```
python simple.py --connector ft232h "simple program to write to the screen" --font 25
```

_FT4222 example in single mode (--mode 0):_

```
python simple.py --connector ft4222module "simple program to write to the screen" --font 25

```

_FT4222 example in dual mode (--mode 1) or quad mode (--mode 2):_

```
python simple.py --connector ft4222module "simple program to write to the screen" --font 25 --mode 2

```

The string in quotes is used in a `CMD_TEXT` call with the font number set in the `--font` parameter. Make sure that the font number is a valid ROM FONT.

## Files and Folders

The example contains a single file which comprises all the demo functionality.

| File/Folder | Description |
| --- | --- |
| [simple.py](simple.py) | Example source code file |

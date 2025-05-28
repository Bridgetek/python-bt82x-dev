# Python BT82x Development Simple Example

The `simple.py` example demonstrates writing text on the screen. It parses arguments and uses them to determine the display list for the BT82x.

The format of the command call is as follows:

MPSSE example
```
python simple.py --connector ft232h "simple program to write to the screen" --font 25
```
FT4222 example in single mode (--mode 0)
```
python simple.py --connector ft4222module "simple program to write to the screen" --font 25

```
FT4222 example in dual mode (--mode 1) or quad mode (--mode 2)
```
python simple.py --connector ft4222module "simple program to write to the screen" --font 25 --mode 2

```

The string in quotes is used in a `CMD_TEXT` call with the font number set in the `--font` parameter. Make sure that the font number is a valid ROM FONT.


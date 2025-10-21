# Python BT82x Development Picture Carousel Example

[Back](../README.md)

## Simple Picture Carousel Example

The `carousel.py` example demonstrates drawing a selection of pictures from SD card. Each time the picture is touched it will move to the next picture in the root of the SD card directory. Only bitmap (`.bmp`) and PNG (`.png`) files are displayed.

RAM_G memory is used to expand the pictures from the SD card before they are displayed. There must not be so many pictures stored on the SD card that the RAM_G is filled with images. Pictures are stored in RAM_G as RGB565 format - that is 2 bytes per pixel. Therefore, on a 1 Gb BT82x board there will be (1 * 1024 * 1024 * 1024 / 8 bytes = 128 MB available, with the top 1.5 MB reserved for use by the co-processor).

This project is suitable for running on CircuitPython.

<!-- ![Segment Example](docs/carousel.png) -->

### Running the Example

The format of the command call to run `carousel` is as follows:

_MPSSE example:_
```
python carousel.py --connector ft232h 
```

_FT4222 example in single mode (--mode 0):_

```
python carousel.py --connector ft4222module 

```

_FT4222 example in dual mode (--mode 1) or quad mode (--mode 2):_

```
python carousel.py --connector ft4222module --mode 2

```

## Files and Folders

The example contains a single file which comprises all the demo functionality.

| File/Folder | Description |
| --- | --- |
| [carousel.py](carousel.py) | Example source code file |
| [docs](docs) | Documentation support files |

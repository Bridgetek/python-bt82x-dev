# Python BT82x Development Example Code

[Back](../README.md)

The `common` directory contains code that is used in the examples for the Python BT82x Development module. The following common code is available:

## Contents

- [Widgets](#widgets)
  - [Seven Segment LED Widget](#Seven-Segment-LED-Widget)
  - [VU Meter Widget](#vu-meter-widget)
- [Utilities](#utilities)
  - [Screenshot Utility](#python-screenshot-utility)
  - [Image Size Utility](#python-image-size-utility)
- [Extensions](#extensions)
  - [Screenshot Utility](#extension-screenshot-utility)
  - [Extension Graph Drawing](#extension-graph-drawing)
  - [Extension Graph and Seven Segment Drawing](#extension-graph-and-seven-segment-drawing)

## Widgets

There are several widgets in the directory:

| File/Folder | Description |
| --- | --- |
| [sevensegment.py](#Seven-Segment-LED-Widget) | Seven segement LED code |
| [vumeter.py](#vu-meter-widget) | VU meter code |

### Seven Segment LED Widget

This widget will simulate a 7 segment LED display. Active LEDs will be drawn in the foreground colour and inactive ones as the background. The digit to be displayed is sent in the range 0-16. For values 0 to 9 the decimal number is shown, for 10 to 15 the letters 'a' to 'f' are shown for hexadecimale displays, and for 16 a dash '-' is displayed.

![Seven Segment LEDs](docs/segment123.png)

_Calling format:_

   `sevenseg.cmd_sevenseg(eve, x, y, size, digit, fgcolour, bgcolour)`

_Parameters:_

-   **x,y**: Location of top left of the seven segment LED widget (in pixels).
-   **size**: Size of a segment of the seven segment LED widget (in pixels).
-   **digit**: Number to display on seven segment LED. 
-   **fgcolour**: Tuple with (R,G,B) colour for active segment.
-   **bgcolour**: Tuple with (R,G,B) colour for inactive segment.

_Example:_

```
sevensegment.cmd_sevenseg(eve, 200, 100, 90, int(number%10), (255, 0, 0), (32, 0, 0))
```

### VU Meter Widget

The VU Meter widget shows a simulation of an analogue level meter commonly found in Hi-Fi audio systems. It will have a FSD (Full Scale Deflection) of 255. It must be provided with the previous value that was returned from the widget to provide proper animation. 

![VU Meter](docs/vumeter.png)

_Calling format:_
   `vumeter.cmd_vumeter(eve, x, y, w, h, vu_level, vu_prev, border)`

_Parameters:_
-   **eve**: Handle to class of bteve2.
-   **x,y**: Location of top left of the VU Meter widget (in pixels).
-   **w,h**: Size of the VU Meter widget (in pixels).
-   **vu_level**: position of VU Meter dial. 0 to 255 (Full Scale Deflection)
-   **vu_prev**: previous position of VU Meter dial.
-   **border**: thickness of grey border around the VU Meter.

_Returns:_
   This returns the **vu_prev** value that must be passed the next time it is 
   called to ensure proper animated action.

_Example:_
```
vu_prev = None
while True:
    vu_level = getvu()
    vu_prev1 = vumeter.cmd_vumeter(eve, 100, 100, 300, 200, vu_level, vu_prev1, 5)
```

## Python Utilities

| File/Folder | Description |
| --- | --- |
| [evescreenshot.py](#python-screenshot-utility) | Utility to generate a screenshot as a BMP file which can be written to a file on the host PC |
| [eveimagesize.py](#python-image-size-utility) | Utility to determine the properties of a file before loading to EVE |

### Python Screenshot Utility

A python screenshot utility `evescreenshot.py` can write a screenshot to a file on the host PC as a BMP file. It comprises a single function `cmd_screenshot`.

Once the display to be captured is drawn into a display list then the cmd_screenshot function is called. This **MUST** be called after a `DISPLAY` command and before a `CMD_SWAP` command.

#### Screenshot Command

_Calling format:_
   `evescreenshot.cmd_screenshot(eve, filename)`

_Parameters:_
-   **eve**: Handle to class of bteve2.
-   **filename**: Filename to write BMP file to on host PC.

_Returns:_
   There is no return value. An exception will be raised if the file cannot be opened.

_Example:_
```
import evescreenshot

eve.LIB_BeginCoProList()
eve.CMD_DLSTART()
eve.CLEAR_COLOR_RGB(64,72,64)
eve.CLEAR(1,1,1)
drawscreen(eve)
eve.DISPLAY()
screenshot.cmd_screenshot(eve, "segments.bmp")
eve.CMD_SWAP()
eve.LIB_EndCoProList()
eve.LIB_AwaitCoProEmpty()
```

### Python Image Size Utility

The eveimagesize utility will obtain the width, height and EVE image format of a PNG or JPG file before it is loaded into the device using `CMD_LOADIMAGE`. It can be used for sizing buffers to receive the image in RAM_G. 

_Calling format:_
   `eveimageproperties.get(eve, img_data)`

_Parameters:_
-   **eve**: Handle to class of bteve2.
-   **img_data**: array containing binary data from image file.

_Returns:_
   This returns a tuple with the width, height and imagetype. If the format is not supported then it will raise an exception.

_Example:_
```
import eveimageproperties

with open("image.jpg", "rb") as file:
    img_data = file.read()
width,height,imagetype = eveimageproperties.get(eve, img_data)
```

## Extensions

| File/Folder | Description |
| --- | --- |
| [extscreenshot.py](#extension-screenshot-utility) | Utility to write a screenshot to an SD Card on a BT82x as a BMP file |
| screenshot.patch | Binary extension file to support the `extscreenshot.py` utility |
| [extplotmem.py](#extension-graph-drawing) | Utility to provide additional graph drawing functionality as an extension |
| [extplotmemsevenseg.py](#extension-graph-and-seven-segment-drawing) | Utility to provide additional graph drawing functionality and seven segment LEDs as an extension |

Documentation 

### Extension Screenshot Utility

The screenshot utility `extscreenshot.py` can write a screenshot to an SD Card on the BT82x as a BMP file. It comprises two parts `setup` and `cmd_screenshot`. The file `screenshot.patch` is loaded as an extension to the BT82x.

Once the display to be captured is drawn into a display list then the cmd_screenshot function is called. This **MUST** be called after a `DISPLAY` command and before a `CMD_SWAP` command.

#### Extension Components

This extension comprises of only the `fssnapshot` extension. The following coprocessor commands are added:
-   CMD_SDBLOCKWRITE
-   CMD_FSWRITE
-   CMD_FSFILE
-   CMD_FSSNAPSHOT
-   CMD_FSCROPSHOT

#### Screenshot Setup

The setup code must be called at some point before the display list to screenshot is drawn, it will load extension code to allow writing to the SD card. This will interfere with other patches that are loaded in the EVE device. The `ext-fssnapshot` extension can be added to a another patch that is loaded in the device.

_Calling format:_
   `extscreenshot.setup(eve)` 

_Parameters:_
-   **eve**: Handle to class of bteve2.

_Returns:_
   This returns the status from an SD card operation. A value of zero is success, any other value is a failure. SD card return values are decoded into strings in the `LIB_SDCardError` function in the EVE module.

#### Screenshot Command

_Calling format:_
   `extscreenshot.cmd_screenshot(eve, filename)`

_Parameters:_
-   **eve**: Handle to class of bteve2.
-   **filename**: Filename to write BMP file to on SD card.

_Returns:_
   This returns the status from an SD card operation. A value of zero is success, any other value is a failure. SD card return values are decoded into strings in the `LIB_SDCardError` function in the EVE module.

_Example:_
```
import extscreenshot

extscreenshot.setup(eve)
eve.LIB_BeginCoProList()
eve.CMD_DLSTART()
eve.CLEAR_COLOR_RGB(64,72,64)
eve.CLEAR(1,1,1)
drawscreen(eve)
eve.DISPLAY()
extscreenshot.cmd_screenshot(eve, "segments.bmp")
eve.CMD_SWAP()
eve.LIB_EndCoProList()
eve.LIB_AwaitCoProEmpty()
```

### Extension Graph Drawing

The `extplotmem.py` script will load an extension to add additional graph drawing functionality to the BT82x.  

#### Extension Components

This extension comprises the `plot` and `mem` extensions. The following coprocessor commands are added:
-   CMD_MEMORYINIT
-   CMD_MEMORYMALLOC
-   CMD_MEMORYFREE
-   CMD_MEMORYBITMAP
-   CMD_PLOTDRAW
-   CMD_PLOTSTREAM
-   CMD_PLOTBITMAP

#### Extension Graph Loading Command

_Calling format:_
   `extplotmem.loadpatch(eve)`

_Parameters:_
-   **eve**: Handle to class of bteve2.

_Returns:_
   This returns the version strings for the extension and the components of the extension.

_Example:_
```
print(extplotmem.loadpatch(eve))

arr1 = bytearray(b'')
for i in range(90):
   arr1.append(128 + int(math.sin((i * 4 / 180) * math.pi) * 120))
eve.LIB_BeginCoProList()
eve.CMD_DLSTART()
eve.CLEAR_COLOR_RGB(30, 30, 90)
eve.CLEAR(1,1,1)
eve.COLOR_RGB(255, 255, 255)
eve.VERTEX_FORMAT(0)
eve.LINE_WIDTH(16)
eve.CMD_PLOTDRAW(0, len(arr), eve.OPT_PLOTHORIZONTAL, 10, 10, 0x14000, 0x18000, 1)
eve.DISPLAY()
eve.CMD_SWAP()
eve.LIB_EndCoProList()
eve.LIB_AwaitCoProEmpty()
```
For example, the following may be returned by `extplotmem.loadpatch()` and printed on the console:
```
plot6;plot-0.3;mem-0.1;
```
This is extension ID/version string of `plot6` and components `plot` version 0.3 and `mem` version 0.1.

### Extension Graph and Seven Segment Drawing

This extension script `extplotmemsevenseg.py` adds an extension to draw seven segment LEDs to the [Extension Graph Drawing](#extension-graph-drawing) extension.

#### Extension Components

This extension comprises the `plot` and `mem` extensions. The following coprocessor commands are added:
-   CMD_MEMORYINIT
-   CMD_MEMORYMALLOC
-   CMD_MEMORYFREE
-   CMD_MEMORYBITMAP
-   CMD_PLOTDRAW
-   CMD_PLOTSTREAM
-   CMD_PLOTBITMAP
-   CMD_SEVENSEG

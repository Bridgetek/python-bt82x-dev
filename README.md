# Python BT82x Development

This python module and connector allow python to be used to communicate with a BT82x device using [pyftdi](https://github.com/eblot/pyftdi) and an FTDI MPSSE device using the [libMPSSE-SPI](https://ftdichip.com/software-examples/mpsse-projects/libmpsse-spi-examples/) library.

The connector code supports the [UMFTPD2A](https://brtchip.com/product/umftpd2a/)_(see note 1)_ module from Bridgetek, USB to MPSSE cables such as the [C232HM](https://ftdichip.com/products/c232hm-edhsl-0/).

Support for FT4222H devices from FTDI may be added in future.

On Windows systems the software connection from pyftdi to the FTDI MPSSE device requires [libusb](https://sourceforge.net/projects/libusb-win32/) drivers which can be easily installed by the [Zadig](https://zadig.akeo.ie/) utility.

This module may also be used with [circuitpython](https://circuitpython.org/), however __this is not yet supported__.

_Note 1_: _A pin header and jumper cables are required to interface the CN2 connector to the BT82x development board._

## Software Setup

All platforms will require a working up-to-date installation of __python 3.13.x__ or later. These instructions assume the use of __pip__ to install required packages.

```
pip install pyftdi

```

### Windows Setup

To connunicate with the MPSSE interface on Windows the standard FTDI drivers cannot be used. These must be replaced with a libusb driver in order for pyftdi to access the device directly. It is not necessary to replace the drivers for all the interfaces on the FTDI devices, just the one used for MPSSE.

The Zadig utility is a handy utility that will replace a driver with libusb. Click on the menu item "Options", then "List all Devices". For a UMFTPD2A board,from the drop-down box select __UMFTPD2A (Interface 1)__ and for the driver choose __libusb-win32__, then click "Replace Driver".

![Zadig screenshot](docs/zadig.png)

### Linux Setup

*These instructions are incomplete!* The built-in Linux drivers for FTDI devices need to be disabled for the libusb driver to be invoked.

## Hardware Setup

_MPSSE Bus numbers refer to the MPSSE interface signals._

The header on the BT82x board has the following connections:

| Pin | Name | Description |
| --- | ----- | ---- |
| 1 | SCK  | SPI SCK - Clock |
| 2 | MOSI  | SPI MOSI - Master Out Slave In |
| 3 | MISO  | SPI MISO - Master In Slave Out |
| 4 | CS#  | SPI CS# Serial Chip Select signal, active LOW |
| 5 | INT#  | Interrupt signal from BT82x, active LOW |
| 6 | RESET#  | Powerdown signal from SPI host, active LOW |
| 7 | NC  | no connection |
| 8 | NC  | no connection |
| 9 | GND  | Signal GND for SPI |
| 10 | GND  | Signal GND for SPI |

### MPSSE Cables

For an MPSSE cable use the MPSSE SPI connections as per [Application Note AN_188](https://ftdichip.com/wp-content/uploads/2020/07/AN_188_C232HM_MPSSE_Cable_in_USB_to_SPI-Interface.pdf).

The following cable coloured wires are connected to the BT82x development board:

| Bus | Cable | Name |
| --- | ----- | ---- |
| MPSSE0 | SK (Orange)    | SPI SCK - Clock|
| MPSSE1 | DO (Yellow)    | SPI MOSI - Master Out Slave In |
| MPSSE2 | DI (Green)     | SPI MISO - Master In Slave Out |
| MPSSE3 | CS (Brown)     | SPI CS# - Serial Chip Select signal |
| MPSSE7 | GPIO L3 (Blue) | PD# - Powerdown signal |
| N/A    | GND (Black)    | Signal GND for SPI |

### UMFTPD2A Programming Boards

On UMFTPD2A the CN2 connector is a 12-pin 2.54 mm pitch through hole connector. It is recommended that a through hole pin header is soldered into the connector and short male-to-male jumper cables used to connect to the BT82x board. The CN2 pins are connected as follows:

| Bus | Pin | Name |
| --- | ----- | ---- |
| MPSSE0 | CN2-1 | SCLK - Clock |
| MPSSE1 | CN2-3 | MOSI - Master Out Slave In |
| MPSSE2 | CN2-4 | MISO - Master In Slave Out |
| MPSSE3 | CN2-2 | CS - Serial Chip Select signal |
| MPSSE7 | CN2-10 | PD# - Powerdown signal |
| N/A    | CN2-7  | Signal GND for SPI |

## Files

| File/Folder | Description |
| --- | --- |
| bteve2 | Module and library code for BT82x |
| connectors | Code to interface between library code and hardware |
| docs | Documentation and images for documentation |
| apprunner.py | Wrapper code to setup library, connector and application |
| simple.py | Simple example code |

### apprunner

This is a wrapper program the selects the command line parameters and chooses a connector. It establishes a module for the BT82x API library and then calls the example program with the graphics descriptor (`gd`) and EVE definitions (`eve`) setup.

### bteve2

This makes a module for the BT82x interface allowing calls from python to be encoded as binary commands for the BT82x. 

### connectors

To run the python code and connect to a BT82x a connector is required. The connector is selected in the parameters to the example programs. It opens a port to the device that makes the SPI signals and sets-up the target device. API interfaces for `reset`, `wr`, `rd`, `cs` functions are required. 

There are supported connectors for [FT4232H (`ft4232h.py`)](connectors/ft4232h.py), [FT232H (`ft232h.py`)](connectors/ft232h.py). The FT4232H connector uses the second MPSSE interface (USB Interface 1) in line with the CN2 connector on the UMFTPD2A board.

Connectors to other transports are simple to make. The `reset` function must be able to setup the BT82x in line with the provided code in supported connectors. The use of Chip Select in the `cs` function is required rather than automatic action of chip select on some devices.

## Running Examples

The apprunner wrapper looks for the `--connector` parameter and attempts to find a connector python file in the connectors directory with a matching name. All other parameters are passed to the example code.

In the example code the `apprunner` and `bteve2` libraries are imported. A function is made which takes a parameter called `gd` (graphics descriptor) which is used to access the BT82x. At the top level of python script a call is made to `apprunner` with the name of the function. This sets up the environment for drawing on the BT82x.

The simplest example code will therefore be:

```
import apprunner
import bteve2 as eve

def simple(gd):
    # Start drawing test screen.
    gd.begin()
    gd.ClearColorRGB(64,72,64)
    gd.Clear(1,1,1)

    gd.Display()
    gd.swap()
    
apprunner.run(simple)
```

### simple.py

This simple program demonstrates writing text on the screen, it parses arguments and uses them to determine the display list for the BT82x.

The format of the command is as follows:

```
python simple.py --connector ft4232h "simple program to write to the screen" --font 25
```

The string in quotes is used in a CMD_TEXT call with the font number set in the `--font` parameter. Make sure that the font number is a valid ROM FONT.

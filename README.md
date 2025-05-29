# Python BT82x Development

This python module and interface connectors allow python to be used to communicate with a BT82x device using D2XX, FT4232H, FT232H or FT4222H devices. 

## Contents

- [Setup](#Setup)
  - [MPSSE Interface](#mpsse-interface)
  - [FT4222H Interface](#ft4222h-interface)
  - [D2XX Interface](#d2xx-interface)
  - [CircuitPython Interface](#circuitpython-interface)
- [Files and Folder Structure](#files-and-folder-structure)
- [BT82x python API](#api)
  - [Display List Commands](#display-list-commands)
  - [Coprocessor Commands](#coprocessor-commands)
  - [Library Functions](#library-functions)
  - [Options and Constants](#options-and-constants)

Additional Documentation:

- [Examples](examples/README.md)

## Setup

The FT4232H and FT232H methods use the **[MPSSE Interface](#mpsse-interface)** of the devices to communicate over SPI to the BT82x. The **[FT4222H Interface](#ft4222h-interface)** has built-in SPI hardware and controller. The D2XX method sends commands to an FT232H, FT4232H or FT232R device directly to drive the SPI interface.

The BT82X based module [VM820C](https://brtchip.com/product/vm820c/) is the main targeted hardware of this repo. 
It is equipped with [FT4222H Interface](#ft4222h-interface) on board for SPI connection with PC through USB.  
To work with MPSSE interface,  please refer to the [VM820C datasheet](https://brtchip.com/wp-content/uploads/2025/01/DS_VM820C-1.pdf)

### MPSSE Interface

For MPSSE devices the [pyftdi](https://github.com/eblot/pyftdi) module for python and the [libMPSSE-SPI](https://ftdichip.com/software-examples/mpsse-projects/libmpsse-spi-examples/) library are required. 

The **connector code** `"connectors/ft4232h.py"` is compatible with the [UMFTPD2A](https://brtchip.com/product/umftpd2a/) _(see note 1)_ module from Bridgetek,  whereas `"connectors/ft232h.py"` supports **USB-to-MPSSE** cables like the [VA800-SPI](https://www.digikey.com/en/htmldatasheets/production/1371434/0/0/1/va800a-spi) and [C232HM](https://ftdichip.com/products/c232hm-edhsl-0/).

The connector `ft4232h` supports the quad-channel FT4232H devices and the connector `ft232h` supports the single-channel FT232H devices.

_Note 1_: _A pin header and jumper cables are required to interface the CN2 connector to the BT82x development board._

#### Software Setup

All platforms will require a working up-to-date installation of __python 3.13.x__ or later. These instructions assume the use of __pip__ to install required pyftdi package.

```
pip install pyftdi
```

This code may also be used with [circuitpython](https://circuitpython.org/), however __this is not yet supported__.

#### Windows Setup

To connunicate with the MPSSE interface on Windows the standard FTDI drivers cannot be used. These must be replaced with a libusb driver in order for pyftdi to access the device directly. It is not necessary to replace the drivers for all the interfaces on the FTDI devices, just the one used for MPSSE.

The [Zadig](https://zadig.akeo.ie/) utility is a handy utility that will replace a driver with libusb. Click on the menu item "Options", then "List all Devices". For a UMFTPD2A board,from the drop-down box select __UMFTPD2A (Interface 1)__ and for the driver choose __libusb-win32__, then click "Replace Driver".

![Zadig screenshot](docs/zadig.png)

It may be neccessary to reboot the PC or remove and replug the MPSSE device. Once this is done the interface for the device will show in Windows Device Manager. Note that there is a missing USB Serial Port (COM4) now.

![Device Manager screenshot](docs/devman.png)

#### Linux Setup

*These instructions are incomplete!* The built-in Linux drivers for FTDI devices need to be disabled for the libusb driver to be invoked.

#### Hardware Setup

_MPSSE Bus numbers refer to the MPSSE interface signals._

The header on the BT82x board has the following connections:

| Pin | Name | Description |
| --- | ----- | ---- |
| 1 | SCK  | SPI SCK - Clock |
| 2 | CS#  | SPI CS# Serial Chip Select signal, active LOW |
| 3 | MOSI  | SPI MOSI - Master Out Slave In |
| 4 | MISO  | SPI MISO - Master In Slave Out |
| 5 | INT#  | Interrupt signal from BT82x, active LOW |
| 6 | RESET#  | Powerdown signal from SPI host, active LOW |
| 7 | NC  | no connection |
| 8 | NC  | no connection |
| 9 | GND  | Signal GND for SPI |
| 10 | GND  | Signal GND for SPI |

Additional methods for connecting an SPI bus can reference this table to connect to BT82x boards.

#### MPSSE Cables

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

The MPSSE cable setup is used with the `ft4232h`, `ft232h`, and `d2xx` connector method.

#### UMFTPD2A Programming Boards

On UMFTPD2A the CN2 connector is a 12-pin 2.54 mm pitch through hole connector. It is recommended that a through hole pin header is soldered into the connector and short male-to-male jumper cables used to connect to the BT82x board. The CN2 pins are connected as follows:

| Bus | Pin | Name |
| --- | ----- | ---- |
| MPSSE0 | CN2-1 | SCLK - Clock |
| MPSSE3 | CN2-2 | CS - Serial Chip Select signal |
| MPSSE1 | CN2-3 | MOSI - Master Out Slave In |
| MPSSE2 | CN2-4 | MISO - Master In Slave Out |
| MPSSE7 | CN2-10 | PD# - Powerdown signal |
| N/A    | CN2-7  | Signal GND for SPI |

The UMFTPD2A programming board can be used with the `ft4232h` and `d2xx` connector method.

### FT4222H Interface

The FT4222 device is supported using the [python-ft4222](https://msrelectronics.gitlab.io/python-ft4222/index.html) module for python and the [libFT4222](https://ftdichip.com/software-examples/ft4222h-software-examples/) library from FTDI.

The connector `ft4222module` supports for FT4222H devices from FTDI.

#### Software Setup

All platforms will require a working up-to-date installation of __python 3.13.x__ or later. These instructions assume the use of __pip__ to install required python-ft4222 package.

```
pip install ft4222
```

This code may also be used with [circuitpython](https://circuitpython.org/), however __this is not yet supported__.

### D2XX Interface

The D2XX interface needs no external libraries as it communicates directly with the MPSSE hardware on an FT4232H, FT232H or FT232R device.

The cable or board connections are identical to the (#MPSSE Cables) section.

### CircuitPython Interface

Embedded MCUs which support the `busio` and `digitalio` modules can be interfaced to the BT82x using the `circuitpython` connector. 

#### Software Setup

The SPI and GPIO pins used for communication are defined in the `__init__` function of the [bteve2/circuitpython.py](bteve2/circuitpython.py) file.

The directory structure on circuitpython is different to this repository. The files in `bteve2` must be copied to the `lib` directory on the circuitpython `CIRCUITPY` drive. Since there is usually less space on a circuitpython device than a PC the library file in `bteve2` may need to be 

See the page [Creating and sharing a CircuitPython library](https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library) for creating a circuitpython module for distribution. This method uses `cookiecutter` to make a distributable library.

For development, individual files can be converted to `.mpy` format using the `mpy-cross` utility. These can be copied into the `lib` directory in a subdirectory called `bteve2` to replicate the functionality on a PC.

```
pip install mpy-cross
```

In future the code here may be distributed as an installable module for circuitpython.

## Files and Folder Structure

The source code in this repository is structured as follows:

| File/Folder | Description |
| --- | --- |
| [bteve2](bteve2) | Module and library code for BT82x |
| [docs](docs) | Documentation and images for documentation |
| [examples](examples) | Example code which use this module |
| [apprunner.py](apprunner.py) | Wrapper code to setup library, connector and application |

The following sections explain the files in the top directory of this repository.

### bteve2

This is a python module for the BT82x interface allowing calls from python to be encoded as binary commands for the BT82x. Files for the connectors are within the module.

#### bteve2 Connectors

To run the python code and connect to a BT82x a connector is required. The connector is selected in the parameters to the example programs. It opens a port to the device that makes the SPI signals and sets-up the target device. API interfaces for `reset`, `wr`, `rd`, `cs` functions are required. 

There are supported connectors for [FT4232H (`ft4232h.py`)](bteve2/ft4232h.py), [FT232H (`ft232h.py`)](bteve2/ft232h.py), [FT4222H (`ft4222module.py`)](bteve2/ft4222module.py), [D2XX (`d2xx.py`)](bteve2/d2xx.py). 

The FT4232H connector uses the first MPSSE interface, if it fails to open that then the second MPSSE interface (USB Interface 1) is used. The the CN2 connector on the UMFTPD2A board is connected to the second MPSSE interface.

Connectors to other transports are simple to make. The `reset` function must be able to setup the BT82x in line with the provided code in supported connectors. The use of Chip Select in the `cs` function is required rather than automatic action of chip select on some devices.

### apprunner

This is a wrapper program that selects the command line parameters, sets up the required display "panel" and chooses a connector. It establishes a module for the BT82x API library and then calls the example program with the EVE handle (`eve`). There is no need to load the `bteve2` module directly.

The apprunner wrapper looks for the `--connector` parameter and attempts to find a connector python file in the connectors directory with a matching name. The next parameter it looks for is `--panel` which it will attempt to match with a panel type name in the program that will be used to setup the display panel. All other parameters are passed unchanged to the called code.

The simplest example code (in the top level directory of the repo) will therefore be:

```
import apprunner

def simplest(eve):
    # Start drawing test screen.
    eve.CMD_DLSTART()
    eve.CLEAR_COLOR_RGB(64,72,64)
    eve.CLEAR(1,1,1)

    eve.DISPLAY()
    eve.CMD_SWAP()
    eve.LIB_AWAITCOPROEMPTY()
    
apprunner.run(simplest)
```

## BT82x python API

The API for using the python interface is simple. All keywords, commands, options, and registers are in capital letters.
* Display List commands have no decoration.
* Coprocessor commands are in prefixed with "CMD_".
* Library functions that automate a coprocessor command are prefixed with "LIB_".
* Registers are prefixed with "REG_".
* Special memory addresses are prefixed with "RAM_".
* Options are prefixed with "OPT_".
* Other constants are prefixed with the function they are related to.

All parameters must be an "int" type and are converted to int by the python `int()` function. Parameters such as 16.16 fixed point and angles must be converted to the binary representation used by the BT82x.

### Display List Commands

These are as described in Chapter 4 of the "BT82X Series Programming Guide". The function for display list commands will add that command to the display list. 

Non-reserved bitfields in the commands are passed as parameters in the call to the function. The parameters are used to set the bits in the 32-bit display list command without modification.

### Coprocessor Commands

These are as described in Chapter 5 of the "BT82X Series Programming Guide". The function for coprocessor commands will add that command to the display list, they will not retrieve any result fields from the coprocessor FIFO.

All results fields for commands will need to be passed as a parameter, even though the result will overwrite this value in the coprocessor FIFO.

### Library Functions

These are provided to generate a coprocessor command and return a result from commands which update the coprocessor FIFO with a result value. 

The reason that the coprocessor commands and the library functions both exist is so that the user has the option of ignoring the result of a coprocessor command without reading the result. This can result in a significant performance improvement.

It is also possible to use coprocessor commands such as CMD_RESULT to copy result values to memory to be checked after a block of coprocessor activity.

### Registers

These are as described in Chapter 3 of the "BT82X Series Programming Guide".

### Options and Constants

Options for display list and coprocessor commands are described in the Chapter 4 and 5 of the "BT82X Series Programming Guide". The naming of the options and constants is made to clarify the function(s) that they are associated with.  e.g. "BEGIN_LINE_STRIP" for use with the display list BEGIN command.

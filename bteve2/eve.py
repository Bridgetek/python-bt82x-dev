# For Bridgetek Pte. Ltd. license see `LICENSE.txt`

import struct
import array
from collections import namedtuple

class CoprocessorException(Exception):
    pass

_B0 = b'\x00'

def align4(s):
    """
    :param bytes s: input bytes object
    :return: the bytes object extended so that its length is a multiple of 4
    """
    return s + _B0 * (-len(s) & 3)

def f16(v):
    return int(round(65536 * v))

def furmans(deg):
    """ Given an angle in degrees, return it in Furmans """
    return 0xffff & f16(deg / 360.0)

# Order matches the register layout, so can fill with a single block read
# REG_TOUCH_SCREEN_XY            = 0x7f006160   #   Touchscreen screen $(x,y)$ (16, 16)
# REG_TOUCH_RAW_XY               = 0x7f006164   #   Touchscreen raw $(x,y)$ (16, 16)
# REG_CTOUCH_TOUCHB_XY           = 0x7f006168   #   Touchscreen touch 2
# REG_CTOUCH_TOUCHC_XY           = 0x7f00616c   #   Touchscreen touch 3
# REG_CTOUCH_TOUCH4_XY           = 0x7f006170   #   Touchscreen touch 4
# REG_TOUCH_TAG_XY               = 0x7f006174   #   Touchscreen screen $(x,y)$ used for tag lookup
# REG_TOUCH_TAG                  = 0x7f006178   #   Touchscreen tag result 0
_Touch = namedtuple(
    "TouchInputs",
    (
    "y", "x",
    "rawy", "rawx",
    "y1", "x1",
    "y2", "x2",
    "y3", "x3",
    "tag_y", "tag_x",
    "tag",
    ))
_State = namedtuple(
    "State",
    (
    "touching",
    "press",
    "release"
    ))
_Tracker = namedtuple(
    "Tracker",
    (
    "tag",
    "val"
    ))
_Inputs = namedtuple(
    "Inputs",
    (
    "touch",
    "tracker",
    "state",
    ))

class EVE2:

    # EVE Registers

    REG_TRACKER                    = 0x7f004000   #   Tracker register 0
    REG_TRACKER_1                  = 0x7f004004   #   Tracker register 1
    REG_TRACKER_2                  = 0x7f004008   #   Tracker register 2
    REG_TRACKER_3                  = 0x7f00400c   #   Tracker register 3
    REG_TRACKER_4                  = 0x7f004010   #   Tracker register 4
    REG_MEDIAFIFO_READ             = 0x7f004014   #   media FIFO read offset
    REG_MEDIAFIFO_WRITE            = 0x7f004018   #   media FIFO write offset
    REG_FLASH_SIZE                 = 0x7f004024   #   Detected flash capacity, in Mbytes
    REG_ANIM_ACTIVE                = 0x7f00402c   #   32-bit mask of currently playing animations
    REG_OBJECT_COMPLETE            = 0x7f004038   #   Used with OPT_COMPLETEREG
    REG_EXTENT_X0                  = 0x7f00403c   #   Previous widget pixel extents
    REG_EXTENT_Y0                  = 0x7f004040   #   Previous widget pixel extents
    REG_EXTENT_X1                  = 0x7f004044   #   Previous widget pixel extents
    REG_EXTENT_Y1                  = 0x7f004048   #   Previous widget pixel extents
    REG_PLAY_CONTROL               = 0x7f004050   #   Video playback control
    REG_ID                         = 0x7f006000   #   Identification register, always reads as 0x7c
    REG_FRAMES                     = 0x7f006004   #   Frame counter, since reset
    REG_CLOCK                      = 0x7f006008   #   Clock cycles, since reset
    REG_FREQUENCY                  = 0x7f00600c   #   Main clock frequency
    REG_RE_DEST                    = 0x7f006010   #   RE destination address
    REG_RE_FORMAT                  = 0x7f006014   #   RE format, as bitmap format
    REG_RE_ROTATE                  = 0x7f006018   #   RE rotate control
    REG_RE_W                       = 0x7f00601c   #   RE target width, in pixels
    REG_RE_H                       = 0x7f006020   #   RE target height, in pixels
    REG_RE_DITHER                  = 0x7f006024   #   RE target dither enable
    REG_RE_ACTIVE                  = 0x7f006028   #   RE write path active
    REG_RE_RENDERS                 = 0x7f00602c   #   RE render counter
    REG_SC0_RESET                  = 0x7f006034   #   Swapchain 0, write to reset
    REG_SC0_SIZE                   = 0x7f006038   #   Swapchain 0, ring size 1-4
    REG_SC0_PTR0                   = 0x7f00603c   #   Swapchain 0, pointer 0
    REG_SC0_PTR1                   = 0x7f006040   #   Swapchain 0, pointer 1
    REG_SC0_PTR2                   = 0x7f006044   #   Swapchain 0, pointer 2
    REG_SC0_PTR3                   = 0x7f006048   #   Swapchain 0, pointer 3
    REG_SC1_RESET                  = 0x7f00604c   #   Swapchain 0, write to reset
    REG_SC1_SIZE                   = 0x7f006050   #   Swapchain 0, ring size 1-4
    REG_SC1_PTR0                   = 0x7f006054   #   Swapchain 0, pointer 0
    REG_SC1_PTR1                   = 0x7f006058   #   Swapchain 0, pointer 1
    REG_SC1_PTR2                   = 0x7f00605c   #   Swapchain 0, pointer 2
    REG_SC1_PTR3                   = 0x7f006060   #   Swapchain 0, pointer 3
    REG_SC2_RESET                  = 0x7f006064   #   Swapchain 0, write to reset
    REG_SC2_SIZE                   = 0x7f006068   #   Swapchain 0, ring size 1-4
    REG_SC2_PTR0                   = 0x7f00606c   #   Swapchain 0, pointer 0
    REG_SC2_PTR1                   = 0x7f006070   #   Swapchain 0, pointer 1
    REG_SC2_PTR2                   = 0x7f006074   #   Swapchain 0, pointer 2
    REG_SC2_PTR3                   = 0x7f006078   #   Swapchain 0, pointer 3
    REG_CPURESET                   = 0x7f006088   #   Coprocessor reset bits 2:JA 1:JT 0:J1
    REG_HCYCLE                     = 0x7f00608c   #   Horizontal total cycle count
    REG_HOFFSET                    = 0x7f006090   #   Horizontal display start offset
    REG_HSIZE                      = 0x7f006094   #   Horizontal display pixel count
    REG_HSYNC0                     = 0x7f006098   #   Horizontal sync fall offset
    REG_HSYNC1                     = 0x7f00609c   #   Horizontal sync rise offset
    REG_VCYCLE                     = 0x7f0060a0   #   Vertical total cycle count
    REG_VOFFSET                    = 0x7f0060a4   #   Vertical display start offset
    REG_VSIZE                      = 0x7f0060a8   #   Vertical display line count
    REG_VSYNC0                     = 0x7f0060ac   #   Vertical sync fall offset
    REG_VSYNC1                     = 0x7f0060b0   #   Vertical sync rise offset
    REG_DLSWAP                     = 0x7f0060b4   #   DISPLAY list swap control
    REG_PCLK_POL                   = 0x7f0060b8   #   PCLK polarity, 0 = clock on rising, 1 = falling
    REG_TAG_X                      = 0x7f0060bc   #   Tag query X coordinate
    REG_TAG_Y                      = 0x7f0060c0   #   Tag query Y coordinate
    REG_TAG                        = 0x7f0060c4   #   Tag query result
    REG_VOL_L_PB                   = 0x7f0060c8   #   Volume for playback left
    REG_VOL_R_PB                   = 0x7f0060cc   #   Volume for playback right
    REG_VOL_SOUND                  = 0x7f0060d0   #   Volume for synth sound
    REG_SOUND                      = 0x7f0060d4   #   Sound effect select
    REG_PLAY                       = 0x7f0060d8   #   Start effect playback
    REG_GPIO_DIR                   = 0x7f0060dc   #   GPIO pin direction, 1 = output
    REG_GPIO                       = 0x7f0060e0   #   GPIO read/write
    REG_DISP                       = 0x7f0060e4   #   DISP output
    REG_INT_FLAGS                  = 0x7f006100   #   Interrupt flags
    REG_INT_EN                     = 0x7f006104   #   Global interrupt enable
    REG_INT_MASK                   = 0x7f006108   #   Interrupt enable mask
    REG_PLAYBACK_START             = 0x7f00610c   #   Audio playback RAM start address
    REG_PLAYBACK_LENGTH            = 0x7f006110   #   Audio playback sample length (bytes)
    REG_PLAYBACK_READPTR           = 0x7f006114   #   Audio playback current read pointer
    REG_PLAYBACK_FREQ              = 0x7f006118   #   Audio playback frequency (Hz)
    REG_PLAYBACK_FORMAT            = 0x7f00611c   #   Audio playback format
    REG_PLAYBACK_LOOP              = 0x7f006120   #   Audio playback loop enable
    REG_PLAYBACK_PLAY              = 0x7f006124   #   Start audio playback
    REG_PWM_HZ                     = 0x7f006128   #   PWM output frequency (Hz)
    REG_PWM_DUTY                   = 0x7f00612c   #   PWM output duty cycle 0=0\%, 128=100\%
    REG_MACRO_0                    = 0x7f006130   #   DISPLAY list macro command 0
    REG_MACRO_1                    = 0x7f006134   #   DISPLAY list macro command 1
    REG_CMD_READ                   = 0x7f00614c   #   Command buffer read pointer
    REG_CMD_WRITE                  = 0x7f006150   #   Command buffer write pointer
    REG_CMD_DL                     = 0x7f006154   #   Command DL offset
    REG_CTOUCH_EXTENDED            = 0x7f00615c   #   0: single-touch, 1: multi-touch
    REG_CTOUCH_TOUCH0_XY           = 0x7f006160   #   Touchscreen screen $(x,y)$ (16, 16) Extended Mode
    REG_TOUCH_SCREEN_XY            = 0x7f006160   #   Touchscreen screen $(x,y)$ (16, 16)
    REG_CTOUCH_TOUCHA_XY           = 0x7f006164   #   Touchscreen raw $(x,y)$ (16, 16) Extended Mode
    REG_TOUCH_RAW_XY               = 0x7f006164   #   Touchscreen raw $(x,y)$ (16, 16)
    REG_CTOUCH_TOUCHB_XY           = 0x7f006168   #   Touchscreen touch 2 Extended Mode
    REG_CTOUCH_TOUCHC_XY           = 0x7f00616c   #   Touchscreen touch 3 Extended Mode
    REG_CTOUCH_TOUCH4_XY           = 0x7f006170   #   Touchscreen touch 4 Extended Mode
    REG_TOUCH_TAG_XY               = 0x7f006174   #   Touchscreen screen $(x,y)$ used for tag lookup
    REG_TOUCH_TAG                  = 0x7f006178   #   Touchscreen tag result 0
    REG_TOUCH_TAG1_XY              = 0x7f00617c   #   Touchscreen screen $(x,y)$ used for tag lookup
    REG_TOUCH_TAG1                 = 0x7f006180   #   Touchscreen tag result 1
    REG_TOUCH_TAG2_XY              = 0x7f006184   #   Touchscreen screen $(x,y)$ used for tag lookup
    REG_TOUCH_TAG2                 = 0x7f006188   #   Touchscreen tag result 2
    REG_TOUCH_TAG3_XY              = 0x7f00618c   #   Touchscreen screen $(x,y)$ used for tag lookup
    REG_TOUCH_TAG3                 = 0x7f006190   #   Touchscreen tag result 3
    REG_TOUCH_TAG4_XY              = 0x7f006194   #   Touchscreen screen $(x,y)$ used for tag lookup
    REG_TOUCH_TAG4                 = 0x7f006198   #   Touchscreen tag result 4
    REG_TOUCH_TRANSFORM_A          = 0x7f00619c   #   Touchscreen transform coefficient (s15.16)
    REG_TOUCH_TRANSFORM_B          = 0x7f0061a0   #   Touchscreen transform coefficient (s15.16)
    REG_TOUCH_TRANSFORM_C          = 0x7f0061a4   #   Touchscreen transform coefficient (s15.16)
    REG_TOUCH_TRANSFORM_D          = 0x7f0061a8   #   Touchscreen transform coefficient (s15.16)
    REG_TOUCH_TRANSFORM_E          = 0x7f0061ac   #   Touchscreen transform coefficient (s15.16)
    REG_TOUCH_TRANSFORM_F          = 0x7f0061b0   #   Touchscreen transform coefficient (s15.16)
    REG_TOUCH_CONFIG               = 0x7f0061b4   #   Touchscreen configuration
    REG_CMDB_SPACE                 = 0x7f006594   #   Command DL (bulk) space available
    REG_PLAYBACK_PAUSE             = 0x7f0065d0   #   audio playback pause, 0=play 1=pause
    REG_FLASH_STATUS               = 0x7f0065d4   #   Flash status 0=INIT 1=DETACHED 2=BASIC 3=FULL
    REG_SO_MODE                    = 0x7f0065f4   #   Scanout pixel mode
    REG_SO_SOURCE                  = 0x7f0065f8   #   Scanout 0 source
    REG_SO_FORMAT                  = 0x7f0065fc   #   Scanout 0 format
    REG_SO_EN                      = 0x7f006600   #   Scanout 0 enable
    REG_I2S_EN                     = 0x7f006714   #   I2S interface enable
    REG_I2S_FREQ                   = 0x7f006718   #   I2S sample frequency
    REG_SC2_STATUS                 = 0x7f006780   #   Swapchain 2 status, write to reset
    REG_SC2_ADDR                   = 0x7f006784   #   Swapchain 2 status, write to reset

    # System Registers

    REG_LVDSRX_CORE_ENABLE         = 0x7f006670   #   LVDSRX enable register
    REG_LVDSRX_CORE_CAPTURE        = 0x7f006674   #   LVDSRX enable capture register
    REG_LVDSRX_CORE_SETUP          = 0x7f006678   #   LVDSRX pixel setup control register
    REG_LVDSRX_CORE_DEST           = 0x7f00667c   #   LVDSRX destination frame address register
    REG_LVDSRX_CORE_FORMAT         = 0x7f006680   #   LVDSRX output pixel format register
    REG_LVDSRX_CORE_DITHER         = 0x7f006684   #   LVDSRX enable dither register
    REG_LVDSRX_CORE_FRAMES         = 0x7f006698   #   LVDSRX frame counter
    REG_LVDSRX_SETUP               = 0x7F800500   #   LVDSRX system set-up
    REG_LVDSRX_CTRL                = 0x7F800504   #   LVDSRX analog block configuration
    REG_LVDSRX_STAT                = 0x7F800508   #   LVDSRX status register
    REG_LVDSTX_EN                  = 0x7f800300   #   LVDS enables
    REG_LVDSTX_PLLCFG              = 0x7f800304   #   LVDS PLL and Clock configuration
    REG_LVDSTX_CTRL_CH0            = 0x7f800314   #   LVDS channel 0 control
    REG_LVDSTX_CTRL_CH1            = 0x7f800318   #   LVDS channel 1 control
    REG_LVDSTX_STAT                = 0x7f80031c   #   LVDS status
    REG_LVDSTX_ERR_STAT            = 0x7f800320   #   LVDS error status

    REG_PIN_DRV_0                  = 0x7f800408   #   Pin drive strength setting
    REG_PIN_DRV_1                  = 0x7f80040C   #   Pin drive strength setting
    REG_PIN_SLEW_0                 = 0x7f800410   #   Pin output slew rate setting
    REG_PIN_TYPE_0                 = 0x7f800414   #   Pin type setting
    REG_PIN_TYPE_1                 = 0x7f800418   #   Pin type setting
    REG_SYS_CFG                    = 0x7f800420   #   Miscellaneous system configuration
    REG_SYS_STAT                   = 0x7f800424   #   System status
    REG_CHIP_ID                    = 0x7f800448   #   CHIP_ID info
    REG_BOOT_STATUS                = 0x7f80044C   #   EVE boot status
    REG_DDR_TYPE                   = 0x7f800454   #   DDR DRAM type setting
    REG_PIN_DRV_2                  = 0x7f800464   #   Pin drive strength setting
    REG_PIN_SLEW_1                 = 0x7f800468   #   Pin output slew rate setting
    REG_PIN_TYPE_2                 = 0x7f80046C   #   Pin type setting
    REG_I2S_CFG                    = 0x7f800800   #   I2S configuration registers
    REG_I2S_CTL                    = 0x7f800804   #   I2S control registers
    REG_I2S_STAT                   = 0x7f800810   #   I2S status
    REG_I2S_PAD_CFG                = 0x7f800814   #   I2S padding configuration

    # Enums

    CMDBUF_SIZE                    = 0x4000
    RAM_CMD                        = 0x7f000000
    RAM_DL                         = 0x7f008000
    RAM_G                          = 0
    RAM_REPORT                     = 0x7f004800
    REG_CMDB_WRITE                 = 0x7f010000
    SWAPCHAIN_0                    = 0xffff00ff
    SWAPCHAIN_1                    = 0xffff01ff
    SWAPCHAIN_2                    = 0xffff02ff

    FIFO_MAX = (CMDBUF_SIZE - 4) # Maximum reported free space in the EVE command FIFO

    # EVE options

    KEY_RETURN                     = 13     # Definition of value of return key.
    KEY_DEL                        = 8      # Definition of value of backspace\delete key.
    KEY_TAB                        = 9      # Definition of value of tab key.
    KEY_ESC                        = 27     # Definition of value of escape key.
    KEY_SHIFT                      = 1      # Definition of value of shift key.
    KEY_ALPHA                      = 2      # Definition of value of alpha key.
    KEY_NUMBER                     = 3      # Definition of value of number key.
    KEY_SYMBOLNUM                  = 4      # Definition of value of symbol key.
    KEY_SYMBOLS                    = 5      # Definition of value of symbol key.
    KEY_CAPS                       = 6      # Definition of value of caps lock key.
    KEY_ALT                        = 11     # Definition of value of alt key.
    KEY_CTRL                       = 12     # Definition of value of ctrl key.

    OPT_3D                         = 0
    OPT_1BIT                       = 0
    OPT_4BIT                       = 2
    OPT_BASELINE                   = 0x8000
    OPT_CASESENSITIVE              = 2
    OPT_CENTER                     = 0x600
    OPT_CENTERX                    = 0x200
    OPT_CENTERY                    = 0x400
    OPT_COMPLETEREG                = 0x1000
    OPT_DIRECT                     = 0x800
    OPT_DIRSEP_UNIX                = 8
    OPT_DIRSEP_WIN                 = 4
    OPT_DITHER                     = 0x100
    OPT_FILL                       = 0x2000
    OPT_FLASH                      = 0x40
    OPT_FLAT                       = 0x100
    OPT_FORMAT                     = 0x1000
    OPT_FS                         = 0x2000
    OPT_FULLSCREEN                 = 8
    OPT_FULLSPEED                  = 0
    OPT_HALFSPEED                  = 4
    OPT_IS_MMC                     = 16
    OPT_IS_SD                      = 32
    OPT_MEDIAFIFO                  = 16
    OPT_MONO                       = 1
    OPT_NOBACK                     = 0x1000
    OPT_NODL                       = 2
    OPT_NOHANDS                    = 0xc000
    OPT_NOHM                       = 0x4000
    OPT_NOKERN                     = 0x4000
    OPT_NOPOINTER                  = 0x4000
    OPT_NOSECS                     = 0x8000
    OPT_NOTICKS                    = 0x2000
    OPT_OVERLAY                    = 0x80
    OPT_QUARTERSPEED               = 8
    OPT_RGB565                     = 0
    OPT_RIGHTX                     = 0x800
    OPT_SFNLOWER                   = 1
    OPT_SIGNED                     = 0x100
    OPT_SIMULATION                 = 1
    OPT_SOUND                      = 32
    OPT_TRUECOLOR                  = 0x200
    OPT_YCBCR                      = 0x400

    # patch-sevenseg
    OPT_DECIMAL                    = 0x10   #   Option to draw a decimal point to the immediate right of the 7 segment.
    OPT_TIMECOLON                  = 0x20   # Option to draw a time colon to the immediate right of the 7 segment.
    OPT_NUMBER                     = 0x0f   # Option of BCD number to show in segments.
    OPT_SEGMENTMASK                = 0x2030 # Mask for above options and vc.OPT_FILL

    # patch-dialogs
    # The amount of alpha to apply to the background box rectangle 
    # behind the text of the message. Set to zero to not apply
    # any alpha.
    OPT_MSGBGALPHA                 = 0x00ff   
    # Option to place the message box in the top third of the screen.
    # This is useful to allow space to draw feedback buttons below.
    OPT_MSGTOP                     = 0x0200   
    # Option to place the message box in the bottom third of the screen.
    # This is useful to allow space to draw feedback buttons above.
    OPT_MSGBOTTOM                  = 0x0400   
    # Option to place the message box aligned to the top or bottom edge of the screen.
    # This gives maximum space below or above the message.
    OPT_MSGEDGE                    = 0x0800   

    # patch-keyboard
    OPT_EXTEND_EDGE                = 0x1000 # Option to extend edge keys to fill spaces.
    OPT_NO_EXTEND_SPACE            = 0x2000 # Option to not expand space character to maximum extent.
    OPT_MAP_SPECIAL_KEYS           = 0x4000 # Options to map special key tags and use premade text instead of mapped font character (Ret, Del, Esc, Aa, ?123, Abc)
    OPT_INVERT_SPECIAL             = 0x8000 # Option to invert colours of special keys.
    OPT_PRESSED                    = 0x00ff # Option to show key with matching tag code in this byte as pressed.

    # patch-plotgraph
    OPT_PLOTHORIZONTAL             = 0x0000      # Option to plot graph horizontally, data on Y-axis
    OPT_PLOTVERTICAL               = 0x1000      # Option to plot graph vertically, data on X-axis
    OPT_PLOTFILTER                 = 0x2000      # Option to remove duplicate points
    OPT_PLOTINVERT                 = 0x4000      # Option to invert data
    OPT_PLOTOVERLAY                = 0x8000

    FORMAT_ARGB1555                       = 0
    FORMAT_L1                             = 1
    FORMAT_L4                             = 2
    FORMAT_L8                             = 3
    FORMAT_RGB332                         = 4
    FORMAT_ARGB2                          = 5
    FORMAT_ARGB4                          = 6
    FORMAT_RGB565                         = 7
    FORMAT_PALETTED                       = 8
    FORMAT_TEXT8X8                        = 9
    FORMAT_TEXTVGA                        = 10
    FORMAT_BARGRAPH                       = 11
    FORMAT_PALETTED565                    = 14
    FORMAT_PALETTED4444                   = 15
    FORMAT_PALETTED8                      = 16
    FORMAT_L2                             = 17
    FORMAT_RGB8                           = 19
    FORMAT_ARGB8                          = 20
    FORMAT_PALETTEDARGB8                  = 21
    FORMAT_RGB6                           = 22
    FORMAT_ARGB6                          = 23
    FORMAT_LA1                            = 24
    FORMAT_LA2                            = 25
    FORMAT_LA4                            = 26
    FORMAT_LA8                            = 27
    FORMAT_YCBCR                          = 28
    FORMAT_GLFORMAT                       = 31
    FORMAT_COMPRESSED_RGBA_ASTC_10x10_KHR = 0x93bb
    FORMAT_COMPRESSED_RGBA_ASTC_10x5_KHR  = 0x93b8
    FORMAT_COMPRESSED_RGBA_ASTC_10x6_KHR  = 0x93b9
    FORMAT_COMPRESSED_RGBA_ASTC_10x8_KHR  = 0x93ba
    FORMAT_COMPRESSED_RGBA_ASTC_12x10_KHR = 0x93bc
    FORMAT_COMPRESSED_RGBA_ASTC_12x12_KHR = 0x93bd
    FORMAT_COMPRESSED_RGBA_ASTC_4x4_KHR   = 0x93b0
    FORMAT_COMPRESSED_RGBA_ASTC_5x4_KHR   = 0x93b1
    FORMAT_COMPRESSED_RGBA_ASTC_5x5_KHR   = 0x93b2
    FORMAT_COMPRESSED_RGBA_ASTC_6x5_KHR   = 0x93b3
    FORMAT_COMPRESSED_RGBA_ASTC_6x6_KHR   = 0x93b4
    FORMAT_COMPRESSED_RGBA_ASTC_8x5_KHR   = 0x93b5
    FORMAT_COMPRESSED_RGBA_ASTC_8x6_KHR   = 0x93b6
    FORMAT_COMPRESSED_RGBA_ASTC_8x8_KHR   = 0x93b7

    BEGIN_BITMAPS                        = 1
    BEGIN_POINTS                         = 2
    BEGIN_LINES                          = 3
    BEGIN_LINE_STRIP                     = 4
    BEGIN_EDGE_STRIP_R                   = 5
    BEGIN_EDGE_STRIP_L                   = 6
    BEGIN_EDGE_STRIP_A                   = 7
    BEGIN_EDGE_STRIP_B                   = 8
    BEGIN_RECTS                          = 9

    TEST_NEVER                          = 0
    TEST_LESS                           = 1
    TEST_LEQUAL                         = 2
    TEST_GREATER                        = 3
    TEST_GEQUAL                         = 4
    TEST_EQUAL                          = 5
    TEST_NOTEQUAL                       = 6
    TEST_ALWAYS                         = 7

    FILTER_NEAREST                        = 0
    FILTER_BILINEAR                       = 1

    WRAP_BORDER                         = 0
    WRAP_REPEAT                         = 1

    BLEND_ZERO                           = 0
    BLEND_ONE                            = 1
    BLEND_SRC_ALPHA                      = 2
    BLEND_DST_ALPHA                      = 3
    BLEND_ONE_MINUS_SRC_ALPHA            = 4
    BLEND_ONE_MINUS_DST_ALPHA            = 5

    STENCIL_ZERO                           = 0
    STENCIL_KEEP                           = 1
    STENCIL_REPLACE                        = 2
    STENCIL_INCR                           = 3
    STENCIL_DECR                           = 4
    STENCIL_INVERT                         = 5

    TOUCHMODE_OFF                  = 0
    TOUCHMODE_ONESHOT              = 1
    TOUCHMODE_FRAME                = 2
    TOUCHMODE_CONTINUOUS           = 3

    TOUCH_100KHZ                   = 0x800
    TOUCH_400KHZ                   = 0x000
    TOUCH_FOCALTECH                = 1
    TOUCH_GOODIX                   = 2
    TOUCH_AR1021                   = 3
    TOUCH_ILI2511                  = 4
    TOUCH_TSC2007                  = 5
    TOUCH_QUICKSIM                 = 0x8000

    DLSWAP_DONE                    = 0
    DLSWAP_FRAME                   = 2

    INT_SWAP                       = 0x01
    INT_TOUCH                      = 0x02
    INT_TAG                        = 0x04
    INT_SOUND                      = 0x08
    INT_PLAYBACK                   = 0x10
    INT_CMDEMPTY                   = 0x20
    INT_CMDFLAG                    = 0x40
    INT_CONVCOMPLETE               = 0x80

    SAMPLES_LINEAR                 = 0
    SAMPLES_ULAW                   = 1
    SAMPLES_ADPCM                  = 2
    SAMPLES_S16                    = 3
    SAMPLES_S16S                   = 4

    RED                            = 2
    GREEN                          = 3
    BLUE                           = 4
    ALPHA                          = 5

    ADC_SINGLE_ENDED           = 0
    ADC_DIFFERENTIAL           = 1

    ANIM_ONCE                      = 0
    ANIM_LOOP                      = 1
    ANIM_HOLD                      = 2

    CGRADIENT_CORNER_ZERO                    = 0
    CGRADIENT_EDGE_ZERO                      = 1

    CTOUCHMODE_EXTENDED           = 0
    CTOUCHMODE_COMPATIBILITY      = 1

    FLASH_STATUS_INIT              = 0
    FLASH_STATUS_DETACHED          = 1
    FLASH_STATUS_BASIC             = 2
    FLASH_STATUS_FULL              = 3

    ROMFONT_WIDTHS = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 
        8,8,8,8,10,13,14,17,24,30, 
        14,15,18,22,28,38,48,62,83]
    ROMFONT_HEIGHTS = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 
        8,8,16,16,13,17,20,22,29,38, 
        16,18,22,27,33,46,58,74,98]
    ROMFONT_FORMATS = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 
        FORMAT_L1,FORMAT_L1,FORMAT_L1,FORMAT_L1,FORMAT_L1, 
        FORMAT_L1,FORMAT_L1,FORMAT_L1,FORMAT_L1,FORMAT_L1, 
        FORMAT_L4,FORMAT_L4,FORMAT_L4,FORMAT_L4,FORMAT_L4, 
        FORMAT_L4,FORMAT_L4,FORMAT_L4,FORMAT_L4 ]
    
    # Definitions used for target display resolution selection
    WQVGA   = 480     # e.g. VM800B with 5" or 4.3" display
    WVGA    = 800     # e.g. ME813A-WH50C or VM816
    WSVGA   = 1024    # e.g. ME817EV with 7" display
    WXGA    = 1280    # e.g. ME817EV with 10.1" display
    HD      = 1920    # e.g. 10" high definition display

    # Select the resolution
    DISPLAY_RES = HD

    # Explicitly disable QuadSPI
    QUADSPI_ENABLE = 0

    # Setup default parameters for various displays.
    # These must be overridden for different display modules.
    SET_PCLK_FREQ       = 0
    EVE_DISP_WIDTH      = 0 #   Active width of LCD display
    EVE_DISP_HEIGHT     = 0 #  Active height of LCD display
    EVE_DISP_HCYCLE     = 0 #  Total number of clocks per line
    EVE_DISP_HOFFSET    = 0 #  Start of active line
    EVE_DISP_HSYNC0     = 0 #  Start of horizontal sync pulse
    EVE_DISP_HSYNC1     = 0 # End of horizontal sync pulse
    EVE_DISP_VCYCLE     = 0 #  Total number of lines per screen
    EVE_DISP_VOFFSET    = 0 #  Start of active screen
    EVE_DISP_VSYNC0     = 0 #  Start of vertical sync pulse
    EVE_DISP_VSYNC1     = 0 #  End of vertical sync pulse
    EVE_DISP_PCLK       = 0 #  Pixel Clock
    EVE_DISP_SWIZZLE    = 0 #  Define RGB output pins
    EVE_DISP_PCLKPOL    = 0 #  Define active edge of PCLK
    EVE_DISP_CSPREAD    = 0
    EVE_DISP_DITHER     = 0
    EVE_TOUCH_CONFIG    = 0 # Touch panel settings

    """
    Co-processor commands are defined in this file and begin with "cmd_".

    Typically the library will be called like this:
        gd.LIB_BeginCoProList()
        gd.CMD_DLSTART()
        gd.CLEAR_COLOR_RGB(64,72,64)
        gd.CLEAR(1,1,1)
        gd.CMD_TEXT(10, 10, 25, 0, "Hello, World!")
        # Send CMD_SWAP then wait for the co-processor to finish.
        gd.CMD_SWAP()
        gd.LIB_EndCoProList()
        gd.LIB_AwaitCoProEmpty() 

    However, if required the display list can be ended with finish
        gd.LIB_BeginCoProList()
        gd.CMD_DLSTART()
        gd.CLEAR_COLOR_RGB(64,72,64)
        gd.CLEAR(1,1,1)
        gd.CMD_TEXT(10, 10, 25, 0, "Hello, World!")
        # Send CMD_SWAP to the display list.
        gd.CMD_SWAP()
        # Wait for the co-processor to finish.
        gd.LIB_EndCoProList()
        gd.LIB_AwaitCoProEmpty()
    
    More advanced usage can have multiple display lists sent to the 
    co-processor.
        gd.LIB_BeginCoProList()
        gd.CMD_DLSTART()
        gd.CLEAR_COLOR_RGB(64,72,64)
        gd.CLEAR(1,1,1)
        gd.CMD_TEXT(10, 10, 25, 0, "Hello, World!")
        # Send CMD_SWAP to the display list.
        gd.CMD_SWAP()
        # Start the co-processor, but do not wait to finish.
        gd.LIB_EndCoProList()
        gd.LIB_AwaitCoProEmpty()
        # Perform some processing for a long time in parallel to the
        # co-processor working.
        long_time_routine()
        # Wait for co-processor.
        while not gd.is_finished(): pass

    """

    # Reset and wait until the co-processor is ready.
    def boot(self):
        print("Booting")
        self.reset()
        self.getspace()

    # Read a 32 bit word from an address on the EVE.
    def rd32(self, a):
        self.cs(True)
        r = struct.unpack("I", self.rd(a, 4))[0]
        self.cs(False)
        return r

    # Write 32 bit word to an address on the EVE.
    def wr32(self, a, v):
        self.cs(True)
        self.wr(a, struct.pack("I", v))
        self.cs(False)

    # Query the co-processor RAM_CMD space.
    # When the co-processor is idle this will be FIFO_MAX.
    # Note: when bit 0 is set then the co-processor has encountered an error.
    def getspace(self):
        self.space = self.rd32(self.REG_CMDB_SPACE)
        if self.space & 1:
            self.cs(True)
            message = self.rd(self.RAM_REPORT, 256).strip(b'\x00').decode('ascii')
            self.cs(False)
            raise CoprocessorException(message)

    # Return True if the co-processor RAM_CMD space is empty (FIFO_MAX 
    # remaining).
    def is_finished(self):
        self.getspace()
        return self.space == self.FIFO_MAX

    # Write data to the co-processor RAM_CMD space. First checks to see if
    # there is sufficient space.
    # Buffer here and write in batches in the connector.
    def write(self, ss):
        i = 0
        while i < len(ss):
            avail = max(0, self.space - 16)
            if (avail > 0): 
                send = ss[i:i + avail]
                i += avail
                self.cs(True)
                self.wr(self.REG_CMDB_WRITE, send, False)
                self.cs(False)
                self.space -= avail
            else:
                self.getspace()

    # Write data to the RAM_G.
    def write_ramg(self, ss, a):
        self.wr(a, ss, True)

    # @brief EVE API: Begin coprocessor list
    # @details Starts a coprocessor list. Waits for the coprocessor to be idle
    #  before asserting chip select.
    def LIB_BeginCoProList(self):
        #self.finish(True)
        pass

    # @brief EVE API: End coprocessor list
    # @details Ends a coprocessor list. Deasserts chip select.
    def LIB_EndCoProList(self):
        pass

    # @brief EVE API: Waits for coprocessor list to end
    # @details Will poll the coprocessor command list until it has been completed.
    #  Will report a coprocessor exception.
    def LIB_AwaitCoProEmpty(self):
        self.finish(True)

    # @brief EVE API: Returns a result from the coprocessor command buffer
    # @details Will return a result value from "offset" words back in the command buffer.
    #  If the value of offset is 1 then the previous value from the coprocessor
    #  command buffer is returned.
    # @returns result of a previous coprocessor command.
    def LIB_GetResult(self, offset = 1):
        return self.previous(offset)
    
    # @brief EVE API: Get coprocessor exception description
    # @details Will query the coprocessor exception description to a string.
    # @returns Coprocessor exception description. This is a pointer to a string
    #   and must be sufficient to hold 256 characters.
    def LIB_GetCoProException(self):
        self.cs(True)
        r = self.rd(self.RAM_REPORT, 256).strip(b'\x00').decode('ascii')
        self.cs(False)
        return r

    # @brief EVE API: Write a buffer to memory mapped RAM
    # @details Writes a block of data via SPI to the EVE.
    # @param s - data buffer.
    # @param a - Memory mapped address on EVE.
    def LIB_WriteDataToRAMG(self, s, a):
        self.cs(True)
        self.write_ramg(s, a)
        self.cs(False)

    # @brief EVE API: Read a buffer from memory mapped RAM
    # @details Reads a block of data via SPI from the EVE.
    # @param s - Pointer to start of receive data buffer.
    # @param len - Number of bytes to read (rounded up to be 32-bit aligned).
    # @param a - 24 bit memory mapped address on EVE.
    def LIB_ReadDataFromRAMG(self, n, a):
        s = b''
        assert (n & 3) == 0, "Data must be a multiple of 4 bytes"
        while n > 0:
            chunk = min((1024 * 32), n)
            self.cs(True)
            s = s + self.rd(a, chunk)
            self.cs(False)
            n -= chunk
            a += chunk
        return s

    # @brief EVE API: Write a buffer to the coprocessor command memory
    # @details Writes a block of data via SPI to the EVE coprocessor.
    #  This must be part of a coprocessor list. It will typically be called
    #  after a coprocessor command to provide data for the operation.
    #  The data will be added to the coprocessor command list therefore the
    #  write will block on available space in this list.
    # @param s - Pointer to start of data buffer.
    # @param DataSize - Number of bytes in buffer.
    def LIB_WriteDataToCMD(self, s):
        self.ram_cmd(s)

    # Perform a swap command in the co-processor. 
    # This will optionally call the finish function to send the data to
    # the co-processor then wait for it to complete.
    def swap(self, finish = True):
        self.DISPLAY()
        self.CMD_SWAP()
        if finish:
            self.finish()

    # Finish a display list in the co-processor.
    # The command buffer is sent to the co-processor then it will optionally
    # wait for the co-processor to complete.
    # Note that this will be synchronised with the frame rate.
    def finish(self, wait = True):
        self.flush()
        if wait:
            while not self.is_finished():
                pass

    # Recover from a coprocessor exception.
    def recover(self):
        self.wr32(self.REG_CMD_READ, 0)
        # Instructions are write REG_CMD_READ as zero then
        # wait for REG_CMD_WRITE to become zero.
        while True:
            writeptr = self.rd32(self.REG_CMD_WRITE)
            if (writeptr == 0): break;

    # Return the result field of the preceding command
    def previous(self, offset = 1, fmt = "I"):
        assert offset > 0, "Offset to result must be greater than zero"
        offset -= 1
        # Change the offset to 32-bit word offset
        offset *= 4
        self.finish(wait=True)
        size = struct.calcsize(fmt)
        assert (size % 4) == 0, "Result format must be a mulitple of 4 bytes"
        cmdoffset = (self.rd32(self.REG_CMD_READ) - offset - size) & self.FIFO_MAX
        self.cs(True)
        r = struct.unpack(fmt, self.rd(self.RAM_CMD + cmdoffset, size))
        self.cs(False)
        if len(r) == 1:
            return r[0]
        else:
            return r

    # For operations that return a result code in the last argument
    def result(self):
        self.cc(b'\00\00\00\00')
        return self.previous()

    # Send a 'C' string to the command buffer.
    def cstring(self, s):
        if type(s) == str:
            s = bytes(s, "utf-8")
        self.cc(align4(s + _B0))

    # Send a string to the command buffer in MicroPython.
    def fstring(self, aa):
        self.cstring(aa[0])
        # XXX MicroPython is currently lacking array.array.tobytes()
        self.cc(bytes(array.array("i", aa[1:])))

    # Read the touch inputs.
    def get_inputs(self):
        self.finish()
        t = _Touch(*struct.unpack("hhHHhhhhhhhhI", self.rd(self.REG_TOUCH_RAW_XY, 28)))

        r = _Tracker(*struct.unpack("HH", self.rd(self.REG_TRACKER, 4)))

        if not hasattr(self, "prev_touching"):
            self.prev_touching = False
        touching = (t.x != -32768)
        press = touching and not self.prev_touching
        release = (not touching) and self.prev_touching
        s = _State(touching, press, release)
        self.prev_touching = touching

        self.inputs = _Inputs(t, r, s)
        return self.inputs

    # Calibrate the touch screen.
    # If there is no saved calibration then a new calibrate operation
    # is performed and the results of the calibration are stored in the 
    # file system.
    def LIB_AutoCalibrate(self):
        fn = "calibrate.bin"

        try:
            with open(fn, "rb") as f:
                self.cs(True)
                self.wr(self.REG_TOUCH_TRANSFORM_A, f.read())
                self.cs(False)
        except FileNotFoundError:
            self.LIB_BeginCoProList()
            self.CMD_DLSTART()
            self.CLEAR()
            self.CMD_TEXT(self.w // 2, self.h // 2, 34, self.OPT_CENTER, "Tap the dot")
            self.CMD_CALIBRATE(0)
            self.LIB_EndCoProList()
            self.LIB_AwaitCoProEmpty()
            self.CMD_DLSTART()
            self.cs(True)
            with open(fn, "wb") as f:
                f.write(self.rd(self.REG_TOUCH_TRANSFORM_A, 24))
            self.cs(False)

    # Load from a file-like into the command buffer.
    def load(self, f):
        while True:
            s = f.read(512)
            if not s:
                return
            while len(s) % 4:
                s += b'\x00'
            self.ram_cmd(s)

    # Command that returns a value as a result from the CMDB.
    def cmdr(self, code, fmt, args):
        self.cmd(code, fmt, args)
        return self.result()

    # Get the touch panel X,Y coordinates
    def LIB_GetTouch(self):
        self.cs(True)
        (ty, tx) = struct.unpack("hh", self.rd(self.REG_TOUCH_SCREEN_XY, 4))
        self.cs(False)
        return (tx, ty)

    # Resolve an SD card error to a description
    def LIB_SDCardError(self, r):
        message = {
                0: "No error.",
                0xd000: "SD card is not detected.",
                0xd001: "No response from card.",
                0xd002: "Card timeout during initialization.",
                0xd003: "Sector 0 (MBR) not found on card.",
                0xd004: "FAT filesystem not found.",
                0xd005: "Card failed to enter high-speed mode",
        }.get(r, "Unknown code")
        return message

    # Setup the EVE registers to match the surface created.
    def panel(self, surface, panelset=None, touch=None):
        self.LIB_BeginCoProList()
        self.CMD_RENDERTARGET(*surface)
        self.CLEAR()
        self.CMD_SWAP()
        self.CMD_GRAPHICSFINISH()
        self.LIB_EndCoProList()
        self.LIB_AwaitCoProEmpty()

        (self.w, self.h) = (surface.w, surface.h)
        self.LIB_BeginCoProList()
        self.CMD_REGWRITE(self.REG_GPIO, 0x80)
        self.CMD_REGWRITE(self.REG_DISP, 1)

        self.EVE_DISP_WIDTH = self.w
        self.EVE_DISP_HEIGHT = self.h

        if panelset == None:
            horcy = self.w + 180
            vercy = self.h + 45 # 1210-1280

            self.EVE_DISP_HCYCLE = horcy
            self.EVE_DISP_HOFFSET = 50
            self.EVE_DISP_HSYNC0 = 0
            self.EVE_DISP_HSYNC1 = 30
            self.EVE_DISP_VCYCLE = vercy
            self.EVE_DISP_VOFFSET = 10
            self.EVE_DISP_VSYNC0 = 0
            self.EVE_DISP_VSYNC1 = 3
            self.EVE_DISP_PCLKPOL = 0

            self.EVE_DISP_PCLK = 2 # Pixel Clock
            self.EVE_DISP_SWIZZLE = 0 # Define RGB output pins
            self.EVE_DISP_CSPREAD = 0
            self.EVE_DISP_DITHER = 1
        
        else:
        
            self.EVE_DISP_HCYCLE = panelset.hcycle
            self.EVE_DISP_HOFFSET = panelset.hoffset
            self.EVE_DISP_HSYNC0 = panelset.hsync0
            self.EVE_DISP_HSYNC1 = panelset.hsync1
            self.EVE_DISP_VCYCLE = panelset.vcycle
            self.EVE_DISP_VOFFSET = panelset.voffset
            self.EVE_DISP_VSYNC0 = panelset.vsync0
            self.EVE_DISP_VSYNC1 = panelset.vsync1
            self.EVE_DISP_PCLKPOL = panelset.pclk_pol

            self.EVE_DISP_PCLK = panelset.pclk_freq
            self.EVE_DISP_SWIZZLE = panelset.swizzle
            self.EVE_DISP_CSPREAD = panelset.cspread
            self.EVE_DISP_DITHER = panelset.dither

        if touch == None:
            self.EVE_TOUCH_CONFIG = ((0x5d << 4) | (2) | (1 << 11)) # Goodix GT911
        else:
            self.EVE_TOUCH_CONFIG = ((touch.address << 4) | (touch.type) | (1 << 11)) 

        self.CMD_REGWRITE(self.REG_HSIZE, self.EVE_DISP_WIDTH)
        self.CMD_REGWRITE(self.REG_VSIZE, self.EVE_DISP_HEIGHT)
        self.CMD_REGWRITE(self.REG_HCYCLE, self.EVE_DISP_HCYCLE)
        self.CMD_REGWRITE(self.REG_HOFFSET, self.EVE_DISP_HOFFSET)
        self.CMD_REGWRITE(self.REG_HSYNC0, self.EVE_DISP_HSYNC0)
        self.CMD_REGWRITE(self.REG_HSYNC1, self.EVE_DISP_HSYNC1)
        self.CMD_REGWRITE(self.REG_VCYCLE, self.EVE_DISP_VCYCLE)
        self.CMD_REGWRITE(self.REG_VOFFSET, self.EVE_DISP_VOFFSET)
        self.CMD_REGWRITE(self.REG_VSYNC0, self.EVE_DISP_VSYNC0)
        self.CMD_REGWRITE(self.REG_VSYNC1, self.EVE_DISP_VSYNC1)
        self.CMD_REGWRITE(self.REG_PCLK_POL, self.EVE_DISP_PCLKPOL)
        self.CMD_REGWRITE(self.REG_RE_DITHER, self.EVE_DISP_DITHER)
        self.LIB_EndCoProList()
        self.LIB_AwaitCoProEmpty()

        # 0: 1 pixel single // 1: 2 pixel single // 2: 2 pixel dual // 3: 4 pixel dual
        extsyncmode = 3
        TXPLLDiv = 0x03
        self.wr32(self.REG_LVDSTX_PLLCFG, 0x00300870 + TXPLLDiv if TXPLLDiv > 4 else 0x00301070 + TXPLLDiv)
        self.wr32(self.REG_LVDSTX_EN, 7) # Enable PLL

        self.LIB_BeginCoProList()
        self.CMD_REGWRITE(self.REG_SO_MODE, extsyncmode)
        self.CMD_REGWRITE(self.REG_SO_SOURCE, surface.addr)
        self.CMD_REGWRITE(self.REG_SO_FORMAT, surface.fmt)
        self.CMD_REGWRITE(self.REG_SO_EN, 1)
        self.LIB_EndCoProList()
        self.LIB_AwaitCoProEmpty()

    # Add commands to the co-processor buffer.
    # It is only sent when flush is called or the buffer exceeds
    # the size of the FIFO.
    def cc(self, s):
        assert (len(s) % 4) == 0, "Coprocessor commands must be a multiple of 4 bytes"
        self.buf += s
        assert (len(self.buf) % 4) == 0, "Coprocessor command buffer must be a multiple of 4 bytes"
        # Flush the co-processor buffer to the EVE device.
        n = len(self.buf)
        if n >= self.FIFO_MAX - 16:
            chunk = min(self.FIFO_MAX - 16, n)
            self.write(self.buf[:chunk])
            self.buf = self.buf[chunk:]

    def register(self, sub):
        self.buf = b''
        getattr(sub, 'write') # Confirm that there is a write method

    # Send the co-processor buffer to the EVE device.
    def flush(self):
        if (len(self.buf)):
            self.write(self.buf)
            self.buf = b''

    # Send a 32-bit value to the EVE.
    def c4(self, i):
        self.cc(struct.pack("I", i))

    # Send a 32-bit basic graphic command to the EVE.
    def cmd0(self, num):
        self.c4(0xffffff00 | num)

    # Send a 32-bit basic graphic command and parameters to the EVE.
    def cmd(self, num, fmt, args):
        self.c4(0xffffff00 | num)
        self.cc(struct.pack(fmt, *args))

    # Send an arbirtary block of data to the co-processor buffer.
    # This can cope with data sizes larger than the buffer.
    def ram_cmd(self, s):
        # CLEAR currently stored buffer.
        n = len(self.buf)
        if n >= self.FIFO_MAX:        
            self.flush()
        assert (len(s) & 3) == 0, "Data must be a multiple of 4 bytes"
        p = len(s)
        while p > 0:
            chunk = min((1024 * 15), self.FIFO_MAX - n)
            self.buf += s[:chunk]
            self.flush()
            s = s[chunk:]
            p -= chunk

    # The basic graphics instructions for DISPLAY Lists.
    def ALPHA_FUNC(self, func,ref):
        self.c4((9 << 24) | ((int(func) & 7) << 8) | ((int(ref) & 255)))
    def BEGIN(self, prim):
        self.c4((31 << 24) | ((int(prim) & 15)))
    def BITMAP_EXT_FORMAT(self, fmt):
        self.c4((46 << 24) | (int(fmt) & 65535))
    def BITMAP_HANDLE(self, handle):
        self.c4((5 << 24) | ((int(handle) & 63)))
    def BITMAP_LAYOUT(self, format,linestride,height):
        self.c4((7 << 24) | ((int(format) & 31) << 19) | ((int(linestride) & 1023) << 9) | ((int(height) & 511)))
    def BITMAP_LAYOUT_H(self, linestride,height):
        self.c4((40 << 24) | (((linestride) & 3) << 2) | (((height) & 3)))
    def BITMAP_SIZE(self, filter,wrapx,wrapy,width,height):
        self.c4((8 << 24) | ((int(filter) & 1) << 20) | ((int(wrapx) & 1) << 19) | ((int(wrapy) & 1) << 18) | ((int(width) & 511) << 9) | ((int(height) & 511)))
    def BITMAP_SIZE_H(self, width,height):
        self.c4((41 << 24) | (((width) & 3) << 2) | (((height) & 3)))
    def BITMAP_SOURCE(self, addr):
        self.c4((1 << 24) | ((int(addr) & 0xffffff)))
    def BITMAP_SOURCE_H(self, addr):
        self.c4((49 << 24) | ((int(addr) & 0xff)))
    def BITMAP_SWIZZLE(self, r, g, b, a):
        self.c4((47 << 24) | ((int(r) & 7) << 9) | ((int(g) & 7) << 6) | ((int(b) & 7) << 3) | ((int(a) & 7)))
    def BITMAP_TRANSFORM_A(self, p, a):
        self.c4((21 << 24) | ((int(p) & 1) << 17) | ((int(a) & 131071)))
    def BITMAP_TRANSFORM_B(self, p, b):
        self.c4((22 << 24) | ((int(p) & 1) << 17) | ((int(b) & 131071)))
    def BITMAP_TRANSFORM_C(self, c):
        self.c4((23 << 24) | ((int(c) & 16777215)))
    def BITMAP_TRANSFORM_D(self, p, d):
        self.c4((24 << 24) | ((int(p) & 1) << 17) | ((int(d) & 131071)))
    def BITMAP_TRANSFORM_E(self, p, e):
        self.c4((25 << 24) | ((int(p) & 1) << 17) | ((int(e) & 131071)))
    def BITMAP_TRANSFORM_F(self, f):
        self.c4((26 << 24) | ((int(f) & 16777215)))
    def BITMAP_ZORDER(self,o):
        self.c4((51 << 24) | (int(o) & 255))
    def BLEND_FUNC(self, src,dst):
        self.c4((11 << 24) | ((int(src) & 7) << 3) | ((int(dst) & 7)))
    def CALL(self, dest):
        self.c4((29 << 24) | ((int(dest) & 65535)))
    def CELL(self, cell):
        self.c4((6 << 24) | ((int(cell) & 127)))
    def CLEAR_COLOR_A(self, alpha):
        self.c4((15 << 24) | ((int(alpha) & 255)))
    def CLEAR_COLOR_RGB(self, red,green,blue):
        self.c4((2 << 24) | ((int(red) & 255) << 16) | ((int(green) & 255) << 8) | ((int(blue) & 255)))
    def CLEAR_COLOR(self, c):
        self.c4((2 << 24) | (c&0xffffff))
    def CLEAR(self, c = 1,s = 1,t = 1):
        self.c4((38 << 24) | ((int(c) & 1) << 2) | ((int(s) & 1) << 1) | ((int(t) & 1)))
    def CLEAR_STENCIL(self, s):
        self.c4((17 << 24) | ((int(s) & 255)))
    def CLEAR_TAG(self, s):
        self.c4((18 << 24) | ((int(s) & 0xffffff)))
    def COLOR_A(self, alpha):
        self.c4((16 << 24) | ((int(alpha) & 255)))
    def COLOR_MASK(self, r,g,b,a):
        self.c4((32 << 24) | ((int(r) & 1) << 3) | ((int(g) & 1) << 2) | ((int(b) & 1) << 1) | ((int(a) & 1)))
    def COLOR_RGB(self, red,green,blue):
        self.c4((4 << 24) | ((int(red) & 255) << 16) | ((int(green) & 255) << 8) | ((int(blue) & 255)))
    def COLOR(self, c):
        self.c4((4 << 24) | (c&0xffffff))
    def DISPLAY(self):
        self.c4((0 << 24))
    def END(self):
        self.c4((33 << 24))
    def JUMP(self, dest):
        self.c4((30 << 24) | ((int(dest) & 65535)))
    def LINE_WIDTH(self, width):
        self.c4((14 << 24) | ((int(width) & 4095)))
    def MACRO(self, m):
        self.c4((37 << 24) | ((int(m) & 1)))
    def NOP(self):
        self.c4((45 << 24))
    def PALETTE_SOURCE(self, addr):
        self.c4((42 << 24) | (((addr) & 4194303)))
    def PALETTE_SOURCE_H(self, addr):
        self.c4((50 << 24) | (((addr >> 24) & 255)))
    def POINT_SIZE(self, size):
        self.c4((13 << 24) | ((int(size) & 8191)))
    def REGION(self,y,h,dest):
        self.c4((52 << 24) | ((int(y) & 63) << 18) | ((int(h) & 63 ) << 12) | (int(dest) & 4095))
    def RESTORE_CONTEXT(self):
        self.c4((35 << 24))
    def RETURN(self):
        self.c4((36 << 24))
    def SAVE_CONTEXT(self):
        self.c4((34 << 24))
    def SCISSOR_SIZE(self, width,height):
        self.c4((28 << 24) | ((int(width) & 4095) << 12) | ((int(height) & 4095)))
    def SCISSOR_XY(self, x,y):
        self.c4((27 << 24) | ((int(x) & 2047) << 11) | ((int(y) & 2047)))
    def STENCIL_FUNC(self, func,ref,mask):
        self.c4((10 << 24) | ((int(func) & 7) << 16) | ((int(ref) & 255) << 8) | ((int(mask) & 255)))
    def STENCIL_MASK(self, mask):
        self.c4((19 << 24) | ((int(mask) & 255)))
    def STENCIL_OP(self, sfail,spass):
        self.c4((12 << 24) | ((int(sfail) & 7) << 3) | ((int(spass) & 7)))
    def TAG_MASK(self, mask):
        self.c4((20 << 24) | ((int(mask) & 1)))
    def TAG(self, s):
        self.c4((3 << 24) | ((int(s) & 0xffffff)))
    def VERTEX_FORMAT(self, frac):
        self.c4((39 << 24) | (int(frac) & 7))
    def VERTEX2F(self, x, y):
        self.c4(0x40000000 | ((int(x) & 32767) << 15) | (int(y) & 32767))
    def VERTEX2II(self, x, y, handle = 0, cell = 0):
        self.c4((2 << 30) | ((int(x) & 511) << 21) | ((int(y) & 511) << 12) | ((int(handle) & 31) << 7) | ((int(cell) & 127)))
    def VERTEX_TRANSLATE_X(self, x):
        self.c4((43 << 24) | (((int(x)) & 131071)))
    def VERTEX_TRANSLATE_Y(self, y):
        self.c4((44 << 24) | (((int(y)) & 131071)))

    # CMD_ANIMDRAW(int32_t ch)
    def CMD_ANIMDRAW(self, *args):
        self.cmd(0x4f, 'i', [ int(arg) for arg in args ])

    # CMD_ANIMFRAME(int16_t x, int16_t y, uint32_t aoptr, uint32_t frame)
    def CMD_ANIMFRAME(self, *args):
        self.cmd(0x5e, 'hhII', [ int(arg) for arg in args ])

    # CMD_ANIMSTART(int32_t ch, uint32_t aoptr, uint32_t loop)
    def CMD_ANIMSTART(self, *args):
        self.cmd(0x5f, 'iII', [ int(arg) for arg in args ])

    # CMD_ANIMSTOP(int32_t ch)
    def CMD_ANIMSTOP(self, *args):
        self.cmd(0x4d, 'i', [ int(arg) for arg in args ])

    # CMD_ANIMXY(int32_t ch, int16_t x, int16_t y)
    def CMD_ANIMXY(self, *args):
        self.cmd(0x4e, 'ihh', [ int(arg) for arg in args ])

    # CMD_APPEND(uint32_t ptr, uint32_t num)
    def CMD_APPEND(self, *args):
        self.cmd(0x1c, 'II', [ int(arg) for arg in args ])

    # CMD_APPENDF(uint32_t ptr, uint32_t num)
    def CMD_APPENDF(self, *args):
        self.cmd(0x52, 'II', [ int(arg) for arg in args ])

    # CMD_ARC(int16_t x, int16_t y, uint16_t r0, uint16_t r1, uint16_t a0, uint16_t a1)
    def CMD_ARC(self, *args):
        self.cmd(0x87, 'hhHHHH', [ int(arg) for arg in args ])

    # CMD_BGCOLOR(uint32_t c)
    def CMD_BGCOLOR(self, *args):
        self.cmd(0x07, 'I', [ int(arg) for arg in args ])

    def CMD_BGCOLOR_RGB(self, red,green,blue):
        self.CMD_BGCOLOR((int(red) & 255) << 16) | ((int(green) & 255) << 8) | ((int(blue) & 255))

    # CMD_BITMAP_TRANSFORM(int32_t x0, int32_t y0, int32_t x1, int32_t y1, int32_t x2, int32_t y2, int32_t tx0, int32_t ty0, int32_t tx1, int32_t ty1, int32_t tx2, int32_t ty2, uint16_t result)
    def CMD_BITMAP_TRANSFORM(self, *args):
        self.cmd(0x1f, 'iiiiiiiiiiiiHH', [ int(arg) for arg in args ] + [0])

    # CMD_BUTTON(int16_t x, int16_t y, int16_t w, int16_t h, int16_t font, uint16_t options, const char* s)
    def CMD_BUTTON(self, *args):
        self.cmd(0x0b, 'hhhhhH', [ int(arg) for arg in args[:6] ])
        self.fstring(args[6:])

    # CMD_CALIBRATE(uint32_t result)
    def CMD_CALIBRATE(self, *args):
        self.cmd(0x13, 'I', [ int(arg) for arg in args ])

    def LIB_Calibrate(self, size):
        self.CMD_CALIBRATE(0)
        return self.previous()

    # CMD_CALIBRATESUB(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint32_t result)
    def CMD_CALIBRATESUB(self, *args):
        self.cmd(0x56, 'HHHHI', [ int(arg) for arg in args ])

    # CMD_CALLLIST(uint32_t a)
    def CMD_CALLLIST(self, *args):
        self.cmd(0x5b, 'I', [ int(arg) for arg in args ])

    # CMD_CGRADIENT(uint32_t shape, int16_t x, int16_t y, int16_t w, int16_t h, uint32_t rgb0, uint32_t rgb1)
    def CMD_CGRADIENT(self, *args):
        self.cmd(0x8a, 'IhhhhII', [ int(arg) for arg in args ])

    # CMD_CLOCK(int16_t x, int16_t y, int16_t r, uint16_t options, uint16_t h, uint16_t m, uint16_t s, uint16_t ms)
    def CMD_CLOCK(self, *args):
        self.cmd(0x12, 'hhhHHHHH', [ int(arg) for arg in args ])

    # CMD_COLDSTART()
    def CMD_COLDSTART(self, *args):
        self.cmd0(0x2e)

    # CMD_COPYLIST(uint32_t dst)
    def CMD_COPYLIST(self, *args):
        self.cmd(0x88, 'I', [ int(arg) for arg in args ])

    # CMD_DDRSHUTDOWN()
    def CMD_DDRSHUTDOWN(self, *args):
        self.cmd0(0x65)

    # CMD_DDRSTARTUP()
    def CMD_DDRSTARTUP(self, *args):
        self.cmd0(0x66)

    # CMD_DIAL(int16_t x, int16_t y, int16_t r, uint16_t options, uint16_t val)
    def CMD_DIAL(self, *args):
        self.cmd(0x29, "hhhHI", [ int(arg) for arg in args ])

    # CMD_DLSTART()
    def CMD_DLSTART(self, *args):
        self.cmd0(0x00)

    # CMD_ENABLEREGION(uint32_t en)
    def CMD_ENABLEREGION(self, *args):
        self.cmd(0x7e, 'I', [ int(arg) for arg in args ])

    # CMD_ENDLIST()
    def CMD_ENDLIST(self, *args):
        self.cmd0(0x5d)

    # CMD_FENCE()
    def CMD_FENCE(self, *args):
        self.cmd0(0x68)

    # CMD_FGCOLOR(uint32_t c)
    def CMD_FGCOLOR(self, *args):
        self.cmd(0x08, 'I', [ int(arg) for arg in args ])

    def CMD_FGCOLOR_RGB(self, red,green,blue):
        self.CMD_FGCOLOR(((int(red) & 255) << 16) | ((int(green) & 255) << 8) | ((int(blue) & 255)))

    # CMD_FILLWIDTH(uint32_t s)
    def CMD_FILLWIDTH(self, *args):
        self.cmd(0x51, 'I', [ int(arg) for arg in args ])

    # CMD_FLASHATTACH()
    def CMD_FLASHATTACH(self, *args):
        self.cmd0(0x43)

    # CMD_FLASHDETACH()
    def CMD_FLASHDETACH(self, *args):
        self.cmd0(0x42)

    # CMD_FLASHERASE()
    def CMD_FLASHERASE(self, *args):
        self.cmd0(0x3e)

    # CMD_FLASHFAST(uint32_t result)
    def CMD_FLASHFAST(self, *args):
        self.cmd(0x44, "I", [ int(arg) for arg in args ])

    def LIB_FlashFast(self):
        self.CMD_FLASHFAST(0)
        return self.previous()

    # CMD_FLASHPROGRAM(uint32_t dest, uint32_t src, uint32_t num)
    def CMD_FLASHPROGRAM(self, *args):
        self.cmd(0x64, 'III', [ int(arg) for arg in args ])

    # CMD_FLASHREAD(uint32_t dest, uint32_t src, uint32_t num)
    def CMD_FLASHREAD(self, *args):
        self.cmd(0x40, 'III', [ int(arg) for arg in args ])

    # CMD_FLASHSOURCE(uint32_t ptr)
    def CMD_FLASHSOURCE(self, *args):
        self.cmd(0x48, 'I', [ int(arg) for arg in args ])

    # CMD_FLASHSPIDESEL()
    def CMD_FLASHSPIDESEL(self, *args):
        self.cmd0(0x45)

    # CMD_FLASHSPIRX(uint32_t ptr, uint32_t num)
    def CMD_FLASHSPIRX(self, *args):
        self.cmd(0x47, 'II', [ int(arg) for arg in args ])

    # CMD_FLASHSPITX(uint32_t num!)
    def CMD_FLASHSPITX(self, *args):
        self.cmd(0x46, 'I', [ int(arg) for arg in args ])

    # CMD_FLASHUPDATE(uint32_t dest, uint32_t src, uint32_t num)
    def CMD_FLASHUPDATE(self, *args):
        self.cmd(0x41, 'III', [ int(arg) for arg in args ])

    # CMD_FLASHWRITE(uint32_t ptr, uint32_t num!)
    def CMD_FLASHWRITE(self, *args):
        self.cmd(0x3f, 'II', [ int(arg) for arg in args ])

    # CMD_FSDIR(uint32_t dst, uint32_t num, const char* path, uint32_t result)
    def CMD_FSDIR(self, *args):
        self.cmd(0x8e, 'II', [ int(arg) for arg in args[:2] ])
        self.cstring(args[2])
        self.c4(int(args[3]))

    def LIB_FSDir(self, dst, num, path):
        self.CMD_FSDIR(dst, num, path, 0)
        return self.previous()

    # CMD_FSOPTIONS(uint32_t options)
    def CMD_FSOPTIONS(self, *args):
        self.cmd(0x6d, 'I', [ int(arg) for arg in args ])

    # CMD_FSREAD(uint32_t dst, const char* filename, uint32_t result)
    def CMD_FSREAD(self, *args):
        self.cmd(0x71, 'I', [int(args[0])])
        self.cstring(args[1])
        self.c4(args[2])

    def LIB_FSRead(self, dst, filename):
        self.CMD_FSREAD(dst, filename, 0)
        return self.previous()

    # CMD_FSSIZE(const char* filename, uint32_t size)
    def CMD_FSSIZE(self, *args):
        self.cmd0(0x80)
        self.cstring(args[0])
        self.c4(int(args[1]))

    def LIB_FSSize(self, filename):
        self.CMD_FSSIZE(filename, 0)
        return self.previous()

    # CMD_FSSOURCE(const char* filename, uint32_t result)
    def CMD_FSSOURCE(self, *args):
        self.cmd0(0x7f)
        self.cstring(args[0])
        self.c4(int(args[1]))

    def LIB_FSSource(self, filename):
        self.CMD_FSSOURCE(filename, 0)
        return self.previous()

    # CMD_GAUGE(int16_t x, int16_t y, int16_t r, uint16_t options, uint16_t major, uint16_t minor, uint16_t val, uint16_t range)
    def CMD_GAUGE(self, *args):
        self.cmd(0x11, 'hhhHHHHH', [ int(arg) for arg in args ])

    # CMD_GETIMAGE(uint32_t source, uint32_t fmt, uint32_t w, uint32_t h, uint32_t palette)
    def CMD_GETIMAGE(self, *args):
        self.cmd(0x58, 'IIIII', [ int(arg) for arg in args ])

    # @brief EVE API: Get image properties.
    # @details From the last CMD_LOADIMAGE get the address, size, format and 
    #   palette of the loaded image.
    # @retuns tuple containting the address the image was loaded to, the format, 
    #   width, height, and palette of the loaded image.
    def LIB_GetImage(self):
        self.CMD_GETIMAGE(0,0,0,0,0)
        return self.previous(1, "IIiiI")

    # CMD_GETMATRIX(int32_t a, int32_t b, int32_t c, int32_t d, int32_t e, int32_t f)
    def CMD_GETMATRIX(self, *args):
        self.cmd(0x2f, 'iiiiii', [ int(arg) for arg in args ])

    # @brief EVE API: Get the touchscreen transformation matrix.
    # @details Obtains the transformation matric from a CMD_CALIBRATE operation.
    # @returns tuple with a, b, c, d, e, f components of the matrix.
    def LIB_GetMatrix(self):
        self.CMD_GETMATRIX(0,0,0,0,0,0)
        return tuple([x/0x10000 for x in self.previous(1, "6i")])

    # CMD_GETPROPS(uint32_t ptr, uint32_t w, uint32_t h)
    def CMD_GETPROPS(self, *args):
        self.cmd(0x22, 'III', [ int(arg) for arg in args ])

    # @brief EVE API: Get properties of an CMD_LOADIMAGE operation
    # @details Obtains the details of an image decoded by the CMD_LOADIMAGE
    #    coprocessor command. The properties of the image are taken from
    #    the coprocessor command list.
    # @returns - tuple with image start address, image width, image height.
    def LIB_GetProps(self):
        self.CMD_GETPROPS(0,0,0)
        return self.previous(1, "Iii")

    # CMD_GETPTR(uint32_t result)
    def CMD_GETPTR(self, *args):
        self.cmd(0x20, 'I', [ int(arg) for arg in args ])

    # @brief EVE API: Get current allocation pointer
    # @details Obtains the automatic allocation pointer of the last address
    #    used for certain coprocessor operations.
    # @returns addr - Last allocation address rounded up to the next 32-bit 
    #    boundary.
    def LIB_GetPtr(self):
        self.CMD_GETPTR(0)
        return self.previous()

    # CMD_GLOW(int16_t x, int16_t y, int16_t w, int16_t h)
    def CMD_GLOW(self, *args):
        self.cmd(0x8b, 'hhhh', [ int(arg) for arg in args ])

    # CMD_GRADCOLOR(uint32_t c)
    def CMD_GRADCOLOR(self, *args):
        self.cmd(0x30, 'I', [ int(arg) for arg in args ])

    # CMD_GRADIENT(int16_t x0, int16_t y0, uint32_t rgb0, int16_t x1, int16_t y1, uint32_t rgb1)
    def CMD_GRADIENT(self, *args):
        self.cmd(0x09, 'hhIhhI', [ int(arg) for arg in args ])

    # CMD_GRADIENTA(int16_t x0, int16_t y0, uint32_t argb0, int16_t x1, int16_t y1, uint32_t argb1)
    def CMD_GRADIENTA(self, *args):
        self.cmd(0x50, 'hhIhhI', [ int(arg) for arg in args ])

    # CMD_GRAPHICSFINISH()
    def CMD_GRAPHICSFINISH(self, *args):
        self.cmd0(0x6b)

    # CMD_I2SSTARTUP(uint32_t freq)
    def CMD_I2SSTARTUP(self, *args):
        self.cmd(0x69, 'I', [ int(arg) for arg in args ])

    # CMD_INFLATE(uint32_t ptr, uint32_t options!)
    def CMD_INFLATE(self, *args):
        self.cmd(0x4a, 'II', [ int(arg) for arg in args ])

    # CMD_INTERRUPT(uint32_t ms)
    def CMD_INTERRUPT(self, *args):
        self.cmd(0x02, 'I', [ int(arg) for arg in args ])

    # CMD_KEYS(int16_t x, int16_t y, int16_t w, int16_t h, int16_t font, uint16_t options, const char* s)
    def CMD_KEYS(self, *args):
        self.cmd(0x0c, 'hhhhhH', [ int(arg) for arg in args[:6] ])
        self.fstring(args[6:])

    # CMD_LOADASSET(uint32_t ptr, uint32_t options!)
    def CMD_LOADASSET(self, *args):
        self.cmd(0x81, 'II', [ int(arg) for arg in args ])

    # CMD_LOADIDENTITY()
    def CMD_LOADIDENTITY(self, *args):
        self.cmd0(0x23)

    # CMD_LOADIMAGE(uint32_t ptr, uint32_t options!)
    def CMD_LOADIMAGE(self, *args):
        self.cmd(0x21, 'II', [ int(arg) for arg in args ])

    # CMD_LOADWAV(uint32_t dst, uint32_t options!)
    def CMD_LOADWAV(self, *args):
        self.cmd(0x85, 'II', [ int(arg) for arg in args ])

    # CMD_LOGO()
    def CMD_LOGO(self, *args):
        self.cmd0(0x2d)

    # CMD_MEDIAFIFO(uint32_t ptr, uint32_t size)
    def CMD_MEDIAFIFO(self, *args):
        self.cmd(0x34, 'II', [ int(arg) for arg in args ])

    # CMD_MEMCPY(uint32_t dest, uint32_t src, uint32_t num)
    def CMD_MEMCPY(self, *args):
        self.cmd(0x1b, 'III', [ int(arg) for arg in args ])

    # CMD_MEMCRC(uint32_t ptr, uint32_t num, uint32_t result)
    def CMD_MEMCRC(self, *args):
        self.cmd(0x16, 'III', [ int(arg) for arg in args ])

    # @brief EVE API: Calculate the CRC of a memory area.
    # @details Obtains the CRC of a memory area.
    # @param ptr - Start of memory area.
    # @param num - Number of bytes to CRC.
    # @returns The caclulated CRC.
    def LIB_MemCrc(self, ptr, num):
        self.CMD_MEMCRC(ptr, num, 0)
        return self.previous()

    # CMD_MEMSET(uint32_t ptr, uint32_t value, uint32_t num)
    def CMD_MEMSET(self, *args):
        self.cmd(0x19, 'III', [ int(arg) for arg in args ])

    # CMD_MEMWRITE(uint32_t ptr, uint32_t num!)
    def CMD_MEMWRITE(self, *args):
        self.cmd(0x18, 'II', [ int(arg) for arg in args ])

    # CMD_MEMZERO(uint32_t ptr, uint32_t num)
    def CMD_MEMZERO(self, *args):
        self.cmd(0x1a, 'II', [ int(arg) for arg in args ])

    # CMD_NEWLIST(uint32_t a)
    def CMD_NEWLIST(self, *args):
        self.cmd(0x5c, 'I', [ int(arg) for arg in args ])

    # CMD_NOP()
    def CMD_NOP(self, *args):
        self.cmd0(0x53)

    # CMD_NUMBER(int16_t x, int16_t y, int16_t font, uint16_t options, int32_t n)
    def CMD_NUMBER(self, *args):
        self.cmd(0x2a, 'hhhHi', [ int(arg) for arg in args ])

    # CMD_PLAYVIDEO(uint32_t options!)
    def CMD_PLAYVIDEO(self, *args):
        self.cmd(0x35, 'I', [ int(arg) for arg in args ])

    # CMD_PLAYWAV(uint32_t options!)
    def CMD_PLAYWAV(self, *args):
        self.cmd(0x79, 'I', [ int(arg) for arg in args ])

    # CMD_PROGRESS(int16_t x, int16_t y, int16_t w, int16_t h, uint16_t options, uint16_t val, uint16_t range)
    def CMD_PROGRESS(self, *args):
        self.cmd(0x0d, 'hhhhHHHH', [ int(arg) for arg in args ] + [0])

    # CMD_REGREAD(uint32_t ptr, uint32_t result)
    def CMD_REGREAD(self, *args):
        self.cmd(0x17, 'II', [ int(arg) for arg in args ])

    # @brief EVE API: Read a register.
    # @details Reads a register value.
    # @param addr - Address of register to read.
    # @returns Contents of the register.
    def LIB_RegRead(self, ptr):
        self.CMD_REGREAD(ptr, 0)
        return self.previous()

    # CMD_REGWRITE(uint32_t dst, uint32_t value)
    def CMD_REGWRITE(self, *args):
        self.cmd(0x86, 'II', [ int(arg) for arg in args ])

    # CMD_RENDERTARGET(uint32_t a, uint16_t fmt, int16_t w, int16_t h)
    def CMD_RENDERTARGET(self, *args):
        self.cmd(0x8d, 'IHhhH', [ int(arg) for arg in args ] + [0])

    # CMD_RESETFONTS()
    def CMD_RESETFONTS(self, *args):
        self.cmd0(0x4c)

    # CMD_RESTORECONTEXT()
    def CMD_RESTORECONTEXT(self, *args):
        self.cmd0(0x7d)

    # CMD_RESULT(uint32_t dst)
    def CMD_RESULT(self, *args):
        self.cmd(0x89, 'I', [ int(arg) for arg in args ])

    # CMD_RETURN()
    def CMD_RETURN(self, *args):
        self.cmd0(0x5a)

    # CMD_ROMFONT(uint32_t font, uint32_t romslot)
    def CMD_ROMFONT(self, *args):
        self.cmd(0x39, 'II', [ int(arg) for arg in args ])

    # CMD_ROTATE(int32_t a)
    def CMD_ROTATE(self, *args):
        self.cmd(0x26, 'i', [ int(arg) for arg in args ])

    # CMD_ROTATEAROUND(int32_t x, int32_t y, int32_t a, int32_t s)
    def CMD_ROTATEAROUND(self, *args):
        self.cmd(0x4b, 'iiii', [ int(arg) for arg in args ])

    # CMD_RUNANIM(uint32_t waitmask, uint32_t play)
    def CMD_RUNANIM(self, *args):
        self.cmd(0x60, 'II', [ int(arg) for arg in args ])

    # CMD_SAVECONTEXT()
    def CMD_SAVECONTEXT(self, *args):
        self.cmd0(0x7c)

    # CMD_SCALE(int32_t sx, int32_t sy)
    def CMD_SCALE(self, *args):
        self.cmd(0x25, 'ii', [ int(arg) for arg in args ])

    # CMD_SCREENSAVER()
    def CMD_SCREENSAVER(self, *args):
        self.cmd0(0x2b)

    # CMD_SCROLLBAR(int16_t x, int16_t y, int16_t w, int16_t h, uint16_t options, uint16_t val, uint16_t size, uint16_t range)
    def CMD_SCROLLBAR(self, *args):
        self.cmd(0x0f, 'hhhhHHHH', [ int(arg) for arg in args ])

    # CMD_SDATTACH(uint32_t options, uint32_t result)
    def CMD_SDATTACH(self, *args):
        self.cmd(0x6e, 'II', [ int(arg) for arg in args ])

    def LIB_SDAttach(self, options):
        self.CMD_SDATTACH(options, 0)
        return self.previous()

    # CMD_SDBLOCKREAD(uint32_t dst, uint32_t src, uint32_t count, uint32_t result)
    def CMD_SDBLOCKREAD(self, *args):
        self.cmd(0x6f, 'IIII', [ int(arg) for arg in args ])

    def LIB_SDBlockRead(self, dst, src, count):
        self.CMD_SDBLOCKREAD(dst, src, count, 0)
        return self.previous()

    # CMD_SETBASE(uint32_t b)
    def CMD_SETBASE(self, *args):
        self.cmd(0x33, 'I', [ int(arg) for arg in args ])

    # CMD_SETBITMAP(uint32_t source, uint16_t fmt, uint16_t w, uint16_t h)
    def CMD_SETBITMAP(self, *args):
        self.cmd(0x3d, 'IHHHH', [ int(arg) for arg in args ] + [0])

    # CMD_SETFONT(uint32_t font, uint32_t ptr, uint32_t firstchar)
    def CMD_SETFONT(self, *args):
        self.cmd(0x36, 'III', [ int(arg) for arg in args ])

    # CMD_SETMATRIX()
    def CMD_SETMATRIX(self, *args):
        self.cmd0(0x27)

    # CMD_SETROTATE(uint32_t r)
    def CMD_SETROTATE(self, *args):
        self.cmd(0x31, 'I', [ int(arg) for arg in args ])

    # CMD_SETSCRATCH(uint32_t handle)
    def CMD_SETSCRATCH(self, *args):
        self.cmd(0x37, 'I', [ int(arg) for arg in args ])

    # CMD_SKETCH(int16_t x, int16_t y, uint16_t w, uint16_t h, uint32_t ptr, uint16_t format)
    def CMD_SKETCH(self, *args):
        self.cmd(0x2c, 'hhHHIHH', [ int(arg) for arg in args ] + [0])

    # CMD_SKIPCOND(uint32_t a, uint32_t func, uint32_t ref, uint32_t mask, uint32_t num)
    def CMD_SKIPCOND(self, *args):
        self.cmd(0x8c, 'IIIII', [ int(arg) for arg in args ])

    # CMD_SLIDER(int16_t x, int16_t y, int16_t w, int16_t h, uint16_t options, uint16_t val, uint16_t range)
    def CMD_SLIDER(self, *args):
        self.cmd(0x0e, 'hhhhHHHH', [ int(arg) for arg in args ] + [0])

    # CMD_SNAPSHOT(uint32_t ptr)
    def CMD_SNAPSHOT(self, *args):
        self.cmd(0x1d, 'I', [ int(arg) for arg in args ])

    # CMD_SPINNER(int16_t x, int16_t y, uint16_t style, uint16_t scale)
    def CMD_SPINNER(self, *args):
        self.cmd(0x14, 'hhHH', [ int(arg) for arg in args ])

    # CMD_STOP()
    def CMD_STOP(self, *args):
        self.cmd0(0x15)

    # CMD_SWAP()
    def CMD_SWAP(self, *args):
        self.cmd0(0x01)

    # CMD_SYNC()
    def CMD_SYNC(self, *args):
        self.cmd0(0x3c)

    # CMD_TESTCARD()
    def CMD_TESTCARD(self, *args):
        self.cmd0(0x57)

    # CMD_TEXT(int16_t x, int16_t y, int16_t font, uint16_t options, const char* s)
    def CMD_TEXT(self, *args):
        self.cmd(0x0a, 'hhhH', [ int(arg) for arg in args[:4] ])
        self.fstring(args[4:])

    # CMD_TEXTDIM(uint32_t dimensions, int16_t font, uint16_t options, const char* s)
    def CMD_TEXTDIM(self, *args):
        self.cmd(0x84, 'IhH', [ int(arg) for arg in args[:3] ])
        self.fstring(args[3:])

    # CMD_TOGGLE(int16_t x, int16_t y, int16_t w, int16_t font, uint16_t options, uint16_t state, const char* s)
    def CMD_TOGGLE(self, *args):
        self.cmd(0x10, "hhhhHH", [ int(arg) for arg in args[0:6] ])
        label = (args[6].encode() + b'\xff' + args[7].encode())
        self.fstring((label,) + [ int(arg) for arg in args[8:] ])

    # CMD_TRACK(int16_t x, int16_t y, int16_t w, int16_t h, int16_t tag)
    def CMD_TRACK(self, *args):
        self.cmd(0x28, 'hhhhhH', [ int(arg) for arg in args ] + [0])

    # CMD_TRANSLATE(int32_t tx, int32_t ty)
    def CMD_TRANSLATE(self, *args):
        self.cmd(0x24, 'ii', [ int(arg) for arg in args ])

    # CMD_VIDEOFRAME(uint32_t dst, uint32_t ptr)
    def CMD_VIDEOFRAME(self, *args):
        self.cmd(0x3b, 'II', [ int(arg) for arg in args ])

    # CMD_VIDEOSTART(uint32_t options)
    def CMD_VIDEOSTART(self, *args):
        self.cmd(0x3a, 'I', [ int(arg) for arg in args ])

    # CMD_WAIT(uint32_t us)
    def CMD_WAIT(self, *args):
        self.cmd(0x59, 'I', [ int(arg) for arg in args ])

    # CMD_WAITCHANGE(uint32_t a)
    def CMD_WAITCHANGE(self, *args):
        self.cmd(0x67, 'I', [ int(arg) for arg in args ])

    # CMD_WAITCOND(uint32_t a, uint32_t func, uint32_t ref, uint32_t mask)
    def CMD_WAITCOND(self, *args):
        self.cmd(0x78, 'IIII', [ int(arg) for arg in args ])

    # CMD_WATCHDOG(uint32_t init_val)
    def CMD_WATCHDOG(self, *args):
        self.cmd(0x83, 'I', [ int(arg) for arg in args ])

    # Extension commands

    # CMD_LOADPATCH(uint32_t options)
    def CMD_LOADPATCH(self, *args):
        self.cmd(0x82, 'I', [ int(arg) for arg in args ])

    # CMD_REGION(void)
    def CMD_REGION(self, *args):
        self.cmd0(0x8f)

    # CMD_ENDREGION(int16_t x, int16_t y, int16_t w, int16_t h)
    def CMD_ENDREGION(self, *args):
        self.cmd(0x90, 'hhhh', [ int(arg) for arg in args ])

    # CMD_SDBLOCKWRITE(uint32_t dst, uint32_t src, uint32_t count, uint32_t result)
    def CMD_SDBLOCKWRITE(self, *args):
        self.cmd(0x70, 'IIII', [ int(arg) for arg in args ])

    def LIB_SDBlockWrite(self, dst, src, count):
        self.CMD_SDBLOCKWRITE(dst, src, count, 0)
        return self.previous()

    # CMD_FSWRITE (uint32_t dst, const char* filename, uint32_t result)
    def CMD_FSWRITE(self, *args):
        self.cmd(0x91, 'I', [int(args[0])])
        self.cstring(args[1])
        self.c4(int(args[2]))

    def LIB_FSWrite(self, dst, filename):
        self.CMD_FSWRITE(dst, filename, 0)
        return self.previous()

    # CMD_FSFILE (uint32_t size, const char* filename, uint32_t result)
    def CMD_FSFILE(self, *args):
        self.cmd(0x92, 'I', [int(args[0])])
        self.cstring(args[1])
        self.c4(int(args[2]))

    def LIB_FSFile(self, size, filename):
        self.CMD_FSFILE(size, filename, 0)
        return self.previous()
        
    # CMD_FSSNAPSHOT (uint32_t temp, const char* filename, uint32_t result)
    def CMD_FSSNAPSHOT(self, *args):
        self.cmd(0x93, 'I', [int(args[0])])
        self.cstring(args[1])
        self.c4(int(args[2]))

    def LIB_FSSnapShot(self, temp, filename):
        self.CMD_FSSNAPSHOT(temp, filename, 0)
        return self.previous()

    # CMD_FSCROPSHOT (uint32_t temp, const char* filename, int16_t x, int16_t y, uint16_t w, uint16_t h)
    def CMD_FSCROPSHOT(self, *args):
        self.cmd(0x94, 'I', [int(args[0])])
        self.cstring(args[1])
        self.cc(struct.pack('hhHH', [ int(arg) for arg in args[2:6] ] ))
        self.c4(int(args[6]))

    def LIB_FSCropShot(self, temp, filename, x, y, w, h):
        self.CMD_FSCROPSHOT(temp, filename, x, y, w, h, 0)
        return self.previous()

    # CMD_SEVENSEG(int16_t x, int16_t y, uint16_t s, uint16_t n)
    def CMD_SEVENSEG(self, *args):
        self.cmd(0x98, 'hhHH', [ int(arg) for arg in args ])

    # CMD_MESSAGEBOX(int16_t font, uint16_t options, const char* s)
    def CMD_MESSAGEBOX(self, *args):
        self.cmd(0x99, 'hH', [ int(arg) for arg in args[:2] ])
        self.fstring(args[2:])

    # CMD_TOOLTIP(int16_t x, int16_t y, int16_t font, uint16_t options, const char* s)
    def CMD_TOOLTIP(self, *args):
        self.cmd(0x9a, 'hhhH', [ int(arg) for arg in args[:4] ])
        self.fstring(args[4:])

    # CMD_TEXTSCALE(int16_t x, int16_t y, int16_t font, uint16_t options, uint32_t scale, const char* s)
    def CMD_TEXTSCALE(self, *args):
        self.cmd(0x95, 'hhhHI', [ int(arg) for arg in args[:5] ])
        self.fstring(args[5:])

    # CMD_TEXTANGLE(int16_t x, int16_t y, int16_t font, uint16_t options, uint32_t angle, const char* s)
    def CMD_TEXTANGLE(self, *args):
        self.cmd(0x96, 'hhhHI', [ int(arg) for arg in args[:5] ])
        self.fstring(args[5:])

    # CMD_TEXTTICKER(int16_t x, int16_t y, uint16_t w, uint16_t h, int16_t font, uint16_t options, uint32_t pos, const char* s)
    def CMD_TEXTTICKER(self, *args):
        self.cmd(0x97, 'hhHHhHi', [ int(arg) for arg in args[:7] ])
        self.fstring(args[7:])

    # CMD_TEXTSIZE(int16_t font, uint16_t options, const char* s, uint16_t w, uint16_t h)
    def CMD_TEXTSIZE(self, *args):
        self.cmd(0xaa, 'hH', [ int(arg) for arg in args[:2] ])
        self.fstring((args[2],))
        self.c4(args[3])

    def LIB_TextSize(self, font, options, s):
        self.CMD_TEXTSIZE(font, options, s, 0)
        wh = self.previous()
        return ((wh >> 16) & 0xffff, wh & 0xffff)

    # CMD_KEYBOARD(int16_t x, int16_t y, uint16_t w, uint16_t h, int16_t font, uint16_t options, const char* s)
    def CMD_KEYBOARD(self, *args):
        self.cmd(0x9b, 'hhHHhH', [ int(arg) for arg in args[:6] ])
        self.fstring(args[6:])

    # CMD_MEMORYINIT(uint32_t address, uint32_t size)
    def CMD_MEMORYINIT(self,*args):
        self.cmd(0x9c, "II", [ int(arg) for arg in args ])

    # CMD_MEMORYMALLOC(uint32_t size, uint32_t address)
    def CMD_MEMORYMALLOC(self, *args):
        self.cmd(0x9d, "II", [ int(arg) for arg in args ])

    def LIB_MemoryMalloc(self, size):
        self.CMD_MEMORYMALLOC(size, 0);
        return self.previous()

    # CMD_MEMORYFREE(uint32_t address, uint32_t size)
    def CMD_MEMORYFREE(self, *args):
        self.cmd(0x9e, "II", [ int(arg) for arg in args ])

    def LIB_MemoryFree(self, address):
        self.CMD_MEMORYFREE(address, 0);
        return self.previous()

    # CMD_MEMORYBITMAP(uint16_t fmt, uint16_t w, uint16_t h, uint16_t addn, uint32_t address)
    def CMD_MEMORYBITMAP(self, *args):
        self.cmd(0xa9, "HHHHI", [ int(arg) for arg in args ])

    def LIB_MemoryBitmap(self, fmt, w, h, addn):
        self.CMD_MEMORYBITMAP(fmt, w, h, addn, 0);
        return self.previous()
    
    # CMD_PLOTDRAW(uint32_t addr, uint16_t len, uint16_t opt, int16_t x, int16_t y, uint32_t xscale, uint32_t yscale)
    def CMD_PLOTDRAW(self, *args):
        self.cmd(0xab, "IHHhhIII", [ int(arg) for arg in args ])

    # CMD_PLOTSTREAM(uint16_t len, uint16_t opt, int16_t x, int16_t y, uint32_t xscale, uint32_t yscale")
    def CMD_PLOTSTREAM(self, *args):
        self.cmd(0xac, "HHhhIII", [ int(arg) for arg in args ])

    # CMD_PLOTBITMAP(uint32_t addr, uint16_t len, uint16_t opt, uint32_t handle)
    def CMD_PLOTBITMAP(self, *args):
        self.cmd(0xad, "IHHI", [ int(arg) for arg in args ])

    # CMD_LVDSINIT(uint16_t setup, uint16_t ctrl)
    def CMD_LVDSINIT(self, *args):
        self.cmd(0x9f, 'HH', [ int(arg) for arg in args ])

    # CMD_LVDSCONN(uint32_t connected")
    def CMD_LVDSCONN(self, *args):
        self.cmd(0xa0, 'I', [ int(arg) for arg in args ])

    # CMD_LVDSSTOP(void)
    def CMD_LVDSSTOP(self, *args):
        self.cmd0(0xa1)

    # CMD_LVDSSTART(void)
    def CMD_LVDSSTART(self, *args):
        self.cmd0(0xa2)

# EVE Registers

OPT_CENTER                     = 0x600

class REG:

    TRACKER                    = 0x7f004000   #   Tracker register 0
    TRACKER_1                  = 0x7f004004   #   Tracker register 1
    TRACKER_2                  = 0x7f004008   #   Tracker register 2
    TRACKER_3                  = 0x7f00400c   #   Tracker register 3
    TRACKER_4                  = 0x7f004010   #   Tracker register 4
    MEDIAFIFO_READ             = 0x7f004014   #   media FIFO read offset
    MEDIAFIFO_WRITE            = 0x7f004018   #   media FIFO write offset
    FLASH_SIZE                 = 0x7f004024   #   Detected flash capacity, in Mbytes
    ANIM_ACTIVE                = 0x7f00402c   #   32-bit mask of currently playing animations
    OBJECT_COMPLETE            = 0x7f004038   #   Used with OPT_COMPLETEREG
    EXTENT_X0                  = 0x7f00403c   #   Previous widget pixel extents
    EXTENT_Y0                  = 0x7f004040   #   Previous widget pixel extents
    EXTENT_X1                  = 0x7f004044   #   Previous widget pixel extents
    EXTENT_Y1                  = 0x7f004048   #   Previous widget pixel extents
    PLAY_CONTROL               = 0x7f004050   #   Video playback control
    ID                         = 0x7f006000   #   Identification register, always reads as 0x7c
    FRAMES                     = 0x7f006004   #   Frame counter, since reset
    CLOCK                      = 0x7f006008   #   Clock cycles, since reset
    FREQUENCY                  = 0x7f00600c   #   Main clock frequency
    RE_DEST                    = 0x7f006010   #   RE destination address
    RE_FORMAT                  = 0x7f006014   #   RE format, as bitmap format
    RE_ROTATE                  = 0x7f006018   #   RE rotate control
    RE_W                       = 0x7f00601c   #   RE target width, in pixels
    RE_H                       = 0x7f006020   #   RE target height, in pixels
    RE_DITHER                  = 0x7f006024   #   RE target dither enable
    RE_ACTIVE                  = 0x7f006028   #   RE write path active
    RE_RENDERS                 = 0x7f00602c   #   RE render counter
    SC0_RESET                  = 0x7f006034   #   Swapchain 0, write to reset
    SC0_SIZE                   = 0x7f006038   #   Swapchain 0, ring size 1-4
    SC0_PTR0                   = 0x7f00603c   #   Swapchain 0, pointer 0
    SC0_PTR1                   = 0x7f006040   #   Swapchain 0, pointer 1
    SC0_PTR2                   = 0x7f006044   #   Swapchain 0, pointer 2
    SC0_PTR3                   = 0x7f006048   #   Swapchain 0, pointer 3
    SC1_RESET                  = 0x7f00604c   #   Swapchain 0, write to reset
    SC1_SIZE                   = 0x7f006050   #   Swapchain 0, ring size 1-4
    SC1_PTR0                   = 0x7f006054   #   Swapchain 0, pointer 0
    SC1_PTR1                   = 0x7f006058   #   Swapchain 0, pointer 1
    SC1_PTR2                   = 0x7f00605c   #   Swapchain 0, pointer 2
    SC1_PTR3                   = 0x7f006060   #   Swapchain 0, pointer 3
    SC2_RESET                  = 0x7f006064   #   Swapchain 0, write to reset
    SC2_SIZE                   = 0x7f006068   #   Swapchain 0, ring size 1-4
    SC2_PTR0                   = 0x7f00606c   #   Swapchain 0, pointer 0
    SC2_PTR1                   = 0x7f006070   #   Swapchain 0, pointer 1
    SC2_PTR2                   = 0x7f006074   #   Swapchain 0, pointer 2
    SC2_PTR3                   = 0x7f006078   #   Swapchain 0, pointer 3
    CPURESET                   = 0x7f006088   #   Coprocessor reset bits 2:JA 1:JT 0:J1
    HCYCLE                     = 0x7f00608c   #   Horizontal total cycle count
    HOFFSET                    = 0x7f006090   #   Horizontal display start offset
    HSIZE                      = 0x7f006094   #   Horizontal display pixel count
    HSYNC0                     = 0x7f006098   #   Horizontal sync fall offset
    HSYNC1                     = 0x7f00609c   #   Horizontal sync rise offset
    VCYCLE                     = 0x7f0060a0   #   Vertical total cycle count
    VOFFSET                    = 0x7f0060a4   #   Vertical display start offset
    VSIZE                      = 0x7f0060a8   #   Vertical display line count
    VSYNC0                     = 0x7f0060ac   #   Vertical sync fall offset
    VSYNC1                     = 0x7f0060b0   #   Vertical sync rise offset
    DLSWAP                     = 0x7f0060b4   #   DISPLAY list swap control
    PCLK_POL                   = 0x7f0060b8   #   PCLK polarity, 0 = clock on rising, 1 = falling
    TAG_X                      = 0x7f0060bc   #   Tag query X coordinate
    TAG_Y                      = 0x7f0060c0   #   Tag query Y coordinate
    TAG                        = 0x7f0060c4   #   Tag query result
    VOL_L_PB                   = 0x7f0060c8   #   Volume for playback left
    VOL_R_PB                   = 0x7f0060cc   #   Volume for playback right
    VOL_SOUND                  = 0x7f0060d0   #   Volume for synth sound
    SOUND                      = 0x7f0060d4   #   Sound effect select
    PLAY                       = 0x7f0060d8   #   Start effect playback
    GPIO_DIR                   = 0x7f0060dc   #   GPIO pin direction, 1 = output
    GPIO                       = 0x7f0060e0   #   GPIO read/write
    DISP                       = 0x7f0060e4   #   DISP output
    INT_FLAGS                  = 0x7f006100   #   Interrupt flags
    INT_EN                     = 0x7f006104   #   Global interrupt enable
    INT_MASK                   = 0x7f006108   #   Interrupt enable mask
    PLAYBACK_START             = 0x7f00610c   #   Audio playback RAM start address
    PLAYBACK_LENGTH            = 0x7f006110   #   Audio playback sample length (bytes)
    PLAYBACK_READPTR           = 0x7f006114   #   Audio playback current read pointer
    PLAYBACK_FREQ              = 0x7f006118   #   Audio playback frequency (Hz)
    PLAYBACK_FORMAT            = 0x7f00611c   #   Audio playback format
    PLAYBACK_LOOP              = 0x7f006120   #   Audio playback loop enable
    PLAYBACK_PLAY              = 0x7f006124   #   Start audio playback
    PWM_HZ                     = 0x7f006128   #   PWM output frequency (Hz)
    PWM_DUTY                   = 0x7f00612c   #   PWM output duty cycle 0=0\%, 128=100\%
    MACRO_0                    = 0x7f006130   #   DISPLAY list macro command 0
    MACRO_1                    = 0x7f006134   #   DISPLAY list macro command 1
    CMD_READ                   = 0x7f00614c   #   Command buffer read pointer
    CMD_WRITE                  = 0x7f006150   #   Command buffer write pointer
    CMD_DL                     = 0x7f006154   #   Command DL offset
    CTOUCH_EXTENDED            = 0x7f00615c   #   0: single-touch, 1: multi-touch
    CTOUCH_TOUCH0_XY           = 0x7f006160   #   Touchscreen screen $(x,y)$ (16, 16)
    TOUCH_SCREEN_XY            = 0x7f006160   #   Touchscreen screen $(x,y)$ (16, 16)
    CTOUCH_TOUCHA_XY           = 0x7f006164   #   Touchscreen raw $(x,y)$ (16, 16)
    TOUCH_RAW_XY               = 0x7f006164   #   Touchscreen raw $(x,y)$ (16, 16)
    CTOUCH_TOUCHB_XY           = 0x7f006168   #   Touchscreen touch 2
    CTOUCH_TOUCHC_XY           = 0x7f00616c   #   Touchscreen touch 3
    CTOUCH_TOUCH4_XY           = 0x7f006170   #   Touchscreen touch 4
    TOUCH_TAG_XY               = 0x7f006174   #   Touchscreen screen $(x,y)$ used for tag lookup
    TOUCH_TAG                  = 0x7f006178   #   Touchscreen tag result 0
    TOUCH_TAG1_XY              = 0x7f00617c   #   Touchscreen screen $(x,y)$ used for tag lookup
    TOUCH_TAG1                 = 0x7f006180   #   Touchscreen tag result 1
    TOUCH_TAG2_XY              = 0x7f006184   #   Touchscreen screen $(x,y)$ used for tag lookup
    TOUCH_TAG2                 = 0x7f006188   #   Touchscreen tag result 2
    TOUCH_TAG3_XY              = 0x7f00618c   #   Touchscreen screen $(x,y)$ used for tag lookup
    TOUCH_TAG3                 = 0x7f006190   #   Touchscreen tag result 3
    TOUCH_TAG4_XY              = 0x7f006194   #   Touchscreen screen $(x,y)$ used for tag lookup
    TOUCH_TAG4                 = 0x7f006198   #   Touchscreen tag result 4
    TOUCH_TRANSFORM_A          = 0x7f00619c   #   Touchscreen transform coefficient (s15.16)
    TOUCH_TRANSFORM_B          = 0x7f0061a0   #   Touchscreen transform coefficient (s15.16)
    TOUCH_TRANSFORM_C          = 0x7f0061a4   #   Touchscreen transform coefficient (s15.16)
    TOUCH_TRANSFORM_D          = 0x7f0061a8   #   Touchscreen transform coefficient (s15.16)
    TOUCH_TRANSFORM_E          = 0x7f0061ac   #   Touchscreen transform coefficient (s15.16)
    TOUCH_TRANSFORM_F          = 0x7f0061b0   #   Touchscreen transform coefficient (s15.16)
    TOUCH_CONFIG               = 0x7f0061b4   #   Touchscreen configuration
    CMDB_SPACE                 = 0x7f006594   #   Command DL (bulk) space available
    PLAYBACK_PAUSE             = 0x7f0065d0   #   audio playback pause, 0=play 1=pause
    FLASH_STATUS               = 0x7f0065d4   #   Flash status 0=INIT 1=DETACHED 2=BASIC 3=FULL
    SO_MODE                    = 0x7f0065f4   #   Scanout pixel mode
    SO_SOURCE                  = 0x7f0065f8   #   Scanout 0 source
    SO_FORMAT                  = 0x7f0065fc   #   Scanout 0 format
    SO_EN                      = 0x7f006600   #   Scanout 0 enable
    I2S_EN                     = 0x7f006714   #   I2S interface enable
    I2S_FREQ                   = 0x7f006718   #   I2S sample frequency
    SC2_STATUS                 = 0x7f006780   #   Swapchain 2 status, write to reset
    SC2_ADDR                   = 0x7f006784   #   Swapchain 2 status, write to reset

    # System Registers

    LVDSRX_CORE_ENABLE         = 0x7f006670   #   LVDSRX enable register
    LVDSRX_CORE_CAPTURE        = 0x7f006674   #   LVDSRX enable capture register
    LVDSRX_CORE_SETUP          = 0x7f006678   #   LVDSRX pixel setup control register
    LVDSRX_CORE_DEST           = 0x7f00667c   #   LVDSRX destination frame address register
    LVDSRX_CORE_FORMAT         = 0x7f006680   #   LVDSRX output pixel format register
    LVDSRX_CORE_DITHER         = 0x7f006684   #   LVDSRX enable dither register
    LVDSRX_CORE_FRAMES         = 0x7f006698   #   LVDSRX frame counter
    LVDSRX_SETUP               = 0x7F800500   #   LVDSRX system set-up
    LVDSRX_CTRL                = 0x7F800504   #   LVDSRX analog block configuration
    LVDSRX_STAT                = 0x7F800508   #   LVDSRX status register
    LVDSTX_EN                  = 0x7f800300   #   LVDS enables
    LVDSTX_PLLCFG              = 0x7f800304   #   LVDS PLL and Clock configuration
    LVDSTX_CTRL_CH0            = 0x7f800314   #   LVDS channel 0 control
    LVDSTX_CTRL_CH1            = 0x7f800318   #   LVDS channel 1 control
    LVDSTX_STAT                = 0x7f80031c   #   LVDS status
    LVDSTX_ERR_STAT            = 0x7f800320   #   LVDS error status

    PIN_DRV_0                  = 0x7f800408   #   Pin drive strength setting
    PIN_DRV_1                  = 0x7f80040C   #   Pin drive strength setting
    PIN_SLEW_0                 = 0x7f800410   #   Pin output slew rate setting
    PIN_TYPE_0                 = 0x7f800414   #   Pin type setting
    PIN_TYPE_1                 = 0x7f800418   #   Pin type setting
    SYS_CFG                    = 0x7f800420   #   Miscellaneous system configuration
    SYS_STAT                   = 0x7f800424   #   System status
    CHIP_ID                    = 0x7f800448   #   CHIP_ID info
    BOOT_STATUS                = 0x7f80044C   #   EVE boot status
    DDR_TYPE                   = 0x7f800454   #   DDR DRAM type setting
    PIN_DRV_2                  = 0x7f800464   #   Pin drive strength setting
    PIN_SLEW_1                 = 0x7f800468   #   Pin output slew rate setting
    PIN_TYPE_2                 = 0x7f80046C   #   Pin type setting
    I2S_CFG                    = 0x7f800800   #   I2S configuration registers
    I2S_CTL                    = 0x7f800804   #   I2S control registers
    I2S_STAT                   = 0x7f800810   #   I2S status
    I2S_PAD_CFG                = 0x7f800814   #   I2S padding configuration

    # Enums

    CMDBUF_SIZE                    = 0x4000
    RAM_CMD                        = 0x7f000000
    RAM_DL                         = 0x7f008000
    RAM_G                          = 0
    RAM_REPORT                     = 0x7f004800
    CMDB_WRITE                     = 0x7f010000
    SWAPCHAIN_0                    = 0xffff00ff
    SWAPCHAIN_1                    = 0xffff01ff
    SWAPCHAIN_2                    = 0xffff02ff

class KEYS:
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

    pass

class OPT:
    _3D                         = 0
    _1BIT                       = 0
    _4BIT                       = 2
    BASELINE                   = 0x8000
    CASESENSITIVE              = 2
    CENTER                     = 0x600
    CENTERX                    = 0x200
    CENTERY                    = 0x400
    COMPLETEREG                = 0x1000
    DIRECT                     = 0x800
    DIRSEP_UNIX                = 8
    DIRSEP_WIN                 = 4
    DITHER                     = 0x100
    FILL                       = 0x2000
    FLASH                      = 0x40
    FLAT                       = 0x100
    FORMAT                     = 0x1000
    FS                         = 0x2000
    FULLSCREEN                 = 8
    FULLSPEED                  = 0
    HALFSPEED                  = 4
    IS_MMC                     = 16
    IS_SD                      = 32
    MEDIAFIFO                  = 16
    MONO                       = 1
    NOBACK                     = 0x1000
    NODL                       = 2
    NOHANDS                    = 0xc000
    NOHM                       = 0x4000
    NOKERN                     = 0x4000
    NOPOINTER                  = 0x4000
    NOSECS                     = 0x8000
    NOTICKS                    = 0x2000
    OVERLAY                    = 0x80
    QUARTERSPEED               = 8
    RGB565                     = 0
    RIGHTX                     = 0x800
    SFNLOWER                   = 1
    SIGNED                     = 0x100
    SIMULATION                 = 1
    SOUND                      = 32
    TRUECOLOR                  = 0x200
    YCBCR                      = 0x400

    # patch-sevenseg
    DECIMAL                    = 0x10   #   Option to draw a decimal point to the immediate right of the 7 segment.
    TIMECOLON                  = 0x20   # Option to draw a time colon to the immediate right of the 7 segment.
    NUMBER                     = 0x0f   # Option of BCD number to show in segments.
    SEGMENTMASK                = 0x2030 # Mask for above options and vc.OPT_FILL

    # patch-dialogs
    # The amount of alpha to apply to the background box rectangle 
    # behind the text of the message. Set to zero to not apply
    # any alpha.
    MSGBGALPHA                 = 0x00ff   
    # Option to place the message box in the top third of the screen.
    # This is useful to allow space to draw feedback buttons below.
    MSGTOP                     = 0x0200   
    # Option to place the message box in the bottom third of the screen.
    # This is useful to allow space to draw feedback buttons above.
    MSGBOTTOM                  = 0x0400   
    # Option to place the message box aligned to the top or bottom edge of the screen.
    # This gives maximum space below or above the message.
    MSGEDGE                    = 0x0800   

    # patch-keyboard
    EXTEND_EDGE                = 0x1000 # Option to extend edge keys to fill spaces.
    NO_EXTEND_SPACE            = 0x2000 # Option to not expand space character to maximum extent.
    MAP_SPECIAL_KEYS           = 0x4000 # Options to map special key tags and use premade text instead of mapped font character (Ret, Del, Esc, Aa, ?123, Abc)
    INVERT_SPECIAL             = 0x8000 # Option to invert colours of special keys.
    PRESSED                    = 0x00ff # Option to show key with matching tag code in this byte as pressed.

    # patch-plotgraph
    PLOTHORIZONTAL             = 0x0000      # Option to plot graph horizontally, data on Y-axis
    PLOTVERTICAL               = 0x1000      # Option to plot graph vertically, data on X-axis
    PLOTFILTER                 = 0x2000      # Option to remove duplicate points
    PLOTINVERT                 = 0x4000      # Option to invert data
    PLOTOVERLAY                = 0x8000

class BITMAP_FORMAT:
    ARGB1555                       = 0
    L1                             = 1
    L4                             = 2
    L8                             = 3
    RGB332                         = 4
    ARGB2                          = 5
    ARGB4                          = 6
    RGB565                         = 7
    PALETTED                       = 8
    TEXT8X8                        = 9
    TEXTVGA                        = 10
    BARGRAPH                       = 11
    PALETTED565                    = 14
    PALETTED4444                   = 15
    PALETTED8                      = 16
    L2                             = 17
    RGB8                           = 19
    ARGB8                          = 20
    PALETTEDARGB8                  = 21
    RGB6                           = 22
    ARGB6                          = 23
    LA1                            = 24
    LA2                            = 25
    LA4                            = 26
    LA8                            = 27
    YCBCR                          = 28
    GLFORMAT                       = 31
    COMPRESSED_RGBA_ASTC_10x10_KHR = 0x93bb
    COMPRESSED_RGBA_ASTC_10x5_KHR  = 0x93b8
    COMPRESSED_RGBA_ASTC_10x6_KHR  = 0x93b9
    COMPRESSED_RGBA_ASTC_10x8_KHR  = 0x93ba
    COMPRESSED_RGBA_ASTC_12x10_KHR = 0x93bc
    COMPRESSED_RGBA_ASTC_12x12_KHR = 0x93bd
    COMPRESSED_RGBA_ASTC_4x4_KHR   = 0x93b0
    COMPRESSED_RGBA_ASTC_5x4_KHR   = 0x93b1
    COMPRESSED_RGBA_ASTC_5x5_KHR   = 0x93b2
    COMPRESSED_RGBA_ASTC_6x5_KHR   = 0x93b3
    COMPRESSED_RGBA_ASTC_6x6_KHR   = 0x93b4
    COMPRESSED_RGBA_ASTC_8x5_KHR   = 0x93b5
    COMPRESSED_RGBA_ASTC_8x6_KHR   = 0x93b6
    COMPRESSED_RGBA_ASTC_8x8_KHR   = 0x93b7

class PRIMATIVE:
    BITMAPS                        = 1
    POINTS                         = 2
    LINES                          = 3
    LINE_STRIP                     = 4
    EDGE_STRIP_R                   = 5
    EDGE_STRIP_L                   = 6
    EDGE_STRIP_A                   = 7
    EDGE_STRIP_B                   = 8
    RECTS                          = 9

class TEST:
    NEVER                          = 0
    LESS                           = 1
    LEQUAL                         = 2
    GREATER                        = 3
    GEQUAL                         = 4
    EQUAL                          = 5
    NOTEQUAL                       = 6
    ALWAYS                         = 7

class FILTER:
    NEAREST                        = 0
    BILINEAR                       = 1

class WRAP:
    BORDER                         = 0
    REPEAT                         = 1

class BLEND:
    ZERO                           = 0
    ONE                            = 1
    SRC_ALPHA                      = 2
    DST_ALPHA                      = 3
    ONE_MINUS_SRC_ALPHA            = 4
    ONE_MINUS_DST_ALPHA            = 5

class STENCIL:
    ZERO                           = 0
    KEEP                           = 1
    REPLACE                        = 2
    INCR                           = 3
    DECR                           = 4
    INVERT                         = 5

class TOUCHMODE:
    OFF                  = 0
    ONESHOT              = 1
    FRAME                = 2
    CONTINUOUS           = 3

class TOUCH:
    _100KHZ                   = 0x800
    _400KHZ                   = 0x000
    FOCALTECH                = 1
    GOODIX                   = 2
    AR1021                   = 3
    ILI2511                  = 4
    TSC2007                  = 5
    QUICKSIM                 = 0x8000

class DLSWAP:
    DONE                    = 0
    FRAME                   = 2

class INT:
    SWAP                       = 0x01
    TOUCH                      = 0x02
    TAG                        = 0x04
    SOUND                      = 0x08
    PLAYBACK                   = 0x10
    CMDEMPTY                   = 0x20
    CMDFLAG                    = 0x40
    CONVCOMPLETE               = 0x80

class SAMPLES:
    LINEAR                 = 0
    ULAW                   = 1
    ADPCM                  = 2
    S16                    = 3
    S16S                   = 4

class CHANNEL:
    RED                            = 2
    GREEN                          = 3
    BLUE                           = 4
    ALPHA                          = 5

class ADC:
    SINGLE_ENDED           = 0
    DIFFERENTIAL           = 1

class ANIM:
    ONCE                      = 0
    LOOP                      = 1
    HOLD                      = 2

class CGRADIENT_SHAPE:
    CORNER_ZERO                    = 0
    EDGE_ZERO                      = 1

class CTOUCH_MODE:
    EXTENDED           = 0
    COMPATIBILITY      = 1
    
class FLASH_STATUS:
    INIT              = 0
    DETACHED          = 1
    BASIC             = 2
    FULL              = 3

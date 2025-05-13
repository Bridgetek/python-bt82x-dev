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

CHANNEL_RED                            = 2
CHANNEL_GREEN                          = 3
CHANNEL_BLUE                           = 4
CHANNEL_ALPHA                          = 5

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

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
REG_RE_TESTMODE                = 0x7f006030
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
REG_SC1_I_VALID                = 0x7f00607c   #   Swapchain 1, input valid (rd)
REG_SC1_I_READY                = 0x7f006080   #   Swapchain 1, input ready (wr)
REG_SC1_I_PTR                  = 0x7f006084   #   Swapchain 1, input pointer (rd)
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
REG_DLSWAP                     = 0x7f0060b4   #   Display list swap control
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
REG_MACRO_0                    = 0x7f006130   #   Display list macro command 0
REG_MACRO_1                    = 0x7f006134   #   Display list macro command 1
REG_CYA1                       = 0x7f00613c   #   bit 0: disable audio filter bank, 2: true PWM out, 3: e0ready testmode
REG_CMD_READ                   = 0x7f00614c   #   Command buffer read pointer
REG_CMD_WRITE                  = 0x7f006150   #   Command buffer write pointer
REG_CMD_DL                     = 0x7f006154   #   Command DL offset
REG_TOUCH_MODE                 = 0x7f006158   #   Touchscreen sampling mode
REG_CTOUCH_EXTENDED            = 0x7f00615c   #   0: single-touch, 1: multi-touch
REG_CTOUCH_TOUCH0_XY           = 0x7f006160   #   Touchscreen screen $(x,y)$ (16, 16)
REG_TOUCH_SCREEN_XY            = 0x7f006160   #   Touchscreen screen $(x,y)$ (16, 16)
REG_CTOUCH_TOUCHA_XY           = 0x7f006164   #   Touchscreen raw $(x,y)$ (16, 16)
REG_TOUCH_RAW_XY               = 0x7f006164   #   Touchscreen raw $(x,y)$ (16, 16)
REG_CTOUCH_TOUCHB_XY           = 0x7f006168   #   Touchscreen touch 2
REG_CTOUCH_TOUCHC_XY           = 0x7f00616c   #   Touchscreen touch 3
REG_CTOUCH_TOUCH4_XY           = 0x7f006170   #   Touchscreen touch 4
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
REG_CRC                        = 0x7f0061b8   #   CPU CRC
REG_DATESTAMP                  = 0x7f006584   #   Compilation datestamp
REG_CMDB_SPACE                 = 0x7f006594   #   Command DL (bulk) space available
REG_PLAYBACK_PAUSE             = 0x7f0065d0   #   audio playback pause, 0=play 1=pause
REG_FLASH_STATUS               = 0x7f0065d4   #   Flash status 0=INIT 1=DETACHED 2=BASIC 3=FULL
REG_FLASH_DTR                  = 0x7f0065ec   #   Flash DTR (Double Transfer Rate) enable
REG_SO_MODE                    = 0x7f0065f4   #   Scanout pixel mode
REG_SO_SOURCE                  = 0x7f0065f8   #   Scanout 0 source
REG_SO_FORMAT                  = 0x7f0065fc   #   Scanout 0 format
REG_SO_EN                      = 0x7f006600   #   Scanout 0 enable
REG_BOOT_CONTROL               = 0x7f006628   #   Boot control byte
REG_I2S_EN                     = 0x7f006714   #   I2S interface enable
REG_I2S_FREQ                   = 0x7f006718   #   I2S sample frequency
REG_FREQUENCY_A                = 0x7f00671c   #   I2S adjusted main frequency
REG_SC2_STATUS                 = 0x7f006780   #   Swapchain 2 status, write to reset
REG_SC2_ADDR                   = 0x7f006784   #   Swapchain 2 status, write to reset

REG_BRIDGE_EN                  = 0x7f00669c

# System Registers

DDR_BASE_ADDR                  = 0x7f800000
DDR_REG_MCCR                   = 0x7f800000
DDR_REG_MCSR                   = 0x7f800004
DDR_REG_MRSVR0                 = 0x7f800008
DDR_REG_MRSVR1                 = 0x7f80000c
DDR_REG_EXRANKR                = 0x7f800010
DDR_REG_TMPR0                  = 0x7f800014
DDR_REG_TMPR1                  = 0x7f800018
DDR_REG_TMPR2                  = 0x7f80001c
DDR_REG_PHYCR0                 = 0x7f800020
DDR_REG_PHYRDTR                = 0x7f800024
DDR_REG_COMPBLKCR              = 0x7f800028
DDR_REG_APDCR                  = 0x7f80002c
DDR_REG_CHARBRA                = 0x7f800030
DDR_REG_CHGNTRA                = 0x7f800034
DDR_REG_CHGNTRB                = 0x7f800038
DDR_REG_PHYWRTMR               = 0x7f80003c
DDR_REG_FLUSHCR                = 0x7f800040
DDR_REG_FLUSHSR                = 0x7f800044
DDR_REG_SPLITCR                = 0x7f800048
DDR_REG_UPDCR                  = 0x7f80004c
DDR_REG_REVR                   = 0x7f800050
DDR_REG_FEATR1                 = 0x7f800054
DDR_REG_FEATR2                 = 0x7f800058
DDR_REG_UDEFR                  = 0x7f80005c
DDR_REG_WLEVELCR               = 0x7f800060
DDR_REG_WLEVELBHR              = 0x7f800064
DDR_REG_WLEVELBLR              = 0x7f800068
DDR_REG_PHYMISCR1              = 0x7f80006c
DDR_REG_RLEVELCR               = 0x7f800070
DDR_REG_MSDLYCR                = 0x7f800074
DDR_REG_WRDLLCR                = 0x7f800078
DDR_REG_TRAFMR                 = 0x7f80007c
DDR_REG_CMDCNTR0               = 0x7f800080
DDR_REG_CMDCNTR1               = 0x7f800084
DDR_REG_CMDCNTR2               = 0x7f800088
DDR_REG_CMDCNTR3               = 0x7f80008c
DDR_REG_CMDCNTR4               = 0x7f800090
DDR_REG_CMDCNTR5               = 0x7f800094
DDR_REG_CMDCNTR6               = 0x7f800098
DDR_REG_CMDCNTR7               = 0x7f80009c
DDR_REG_AHBRPRER1              = 0x7f8000a0
DDR_REG_AHBRPRER2              = 0x7f8000a4
DDR_REG_INITWCR1               = 0x7f8000a8
DDR_REG_INITWCR2               = 0x7f8000ac
DDR_REG_QOSCR                  = 0x7f8000b0
DDR_REG_QOSCNTRA               = 0x7f8000b4
DDR_REG_QOSCNTRB               = 0x7f8000b8
DDR_REG_QOSCNTRC               = 0x7f8000bc
DDR_REG_QOSCNTRD               = 0x7f8000c0
DDR_REG_CHARBRB                = 0x7f8000c4
DDR_REG_CHGNTRC                = 0x7f8000c8
DDR_REG_CHGNTRD                = 0x7f8000cc
DDR_REG_DBGADR                 = 0x7f8000d0
DDR_REG_DBGADMR                = 0x7f8000d4
DDR_REG_DBGWDR                 = 0x7f8000d8
DDR_REG_DBGWDMR                = 0x7f8000dc
DDR_REG_DBGMSTR                = 0x7f8000e0
DDR_REG_DBGACCR                = 0x7f8000e4
DDR_REG_DBGPCR                 = 0x7f8000e8
DDR_REG_DBGENR                 = 0x7f8000ec
DDR_REG_DBGADSR                = 0x7f8000f0
DDR_REG_DBGWDSR                = 0x7f8000f4
DDR_REG_DBGMSTSR               = 0x7f8000f8
DDR_REG_DBGACCSR               = 0x7f8000fc
DDR_REG_LP2MRA                 = 0x7f800100
DDR_REG_LP2MRB                 = 0x7f800104
DDR_REG_LP2MRC                 = 0x7f800108
DDR_REG_LP2MRD                 = 0x7f80010c
DDR_REG_LP2MRE                 = 0x7f800110
DDR_REG_LP2MRCR                = 0x7f800114
DDR_REG_LP2MRVR                = 0x7f800118
DDR_REG_LP2ADLR                = 0x7f80011c
DDR_REG_LP2WCR1                = 0x7f800120
DDR_REG_LP2WCR2                = 0x7f800124
DDR_REG_REARBDISR              = 0x7f80012c
DDR_REG_PHYRDTFR               = 0x7f800130
DDR_REG_PHYMISCR2              = 0x7f800134
DDR_REG_EFIFOCR                = 0x7f800138
DDR_REG_RB0DSKW                = 0x7f800160
DDR_REG_RB1DSKW                = 0x7f800164
DDR_REG_RB2DSKW                = 0x7f800168
DDR_REG_RB3DSKW                = 0x7f80016c
DDR_REG_RB4DSKW                = 0x7f800170
DDR_REG_RB5DSKW                = 0x7f800174
DDR_REG_RB6DSKW                = 0x7f800178
DDR_REG_RB7DSKW                = 0x7f80017c
DDR_REG_WB0DSKW                = 0x7f800180
DDR_REG_WB1DSKW                = 0x7f800184
DDR_REG_WB2DSKW                = 0x7f800188
DDR_REG_WB3DSKW                = 0x7f80018c
DDR_REG_WB4DSKW                = 0x7f800190
DDR_REG_WB5DSKW                = 0x7f800194
DDR_REG_WB6DSKW                = 0x7f800198
DDR_REG_WB7DSKW                = 0x7f80019c
DDR_REG_WDMDSKW                = 0x7f8001a0
DDR_REG_RB8DSKW                = 0x7f8001a4
DDR_REG_WB8DSKW                = 0x7f8001a8
DDR_REG_B8_PHYCR               = 0x7f8001ac
DDR_REG_BIST_CTRL              = 0x7f8001b0
DDR_REG_BIST_START_ADDR        = 0x7f8001b4
DDR_REG_BIST_SIZE              = 0x7f8001b8
DDR_REG_BIST_RESULT            = 0x7f8001c0
DDR_REG_BIST_FAIL_ADDR         = 0x7f8001c4
DDR_REG_BIST_FAIL_DATA_LOW     = 0x7f8001c8
DDR_REG_BIST_FAIL_DATA_HIGH    = 0x7f8001cc
DDR_REG_BIST_EXP_DATA_LOW      = 0x7f8001d0
DDR_REG_BIST_EXP_DATA_HIGH     = 0x7f8001d4
DDR_REG_ECC_CTRLR              = 0x7f8001e0
DDR_REG_ECC_INTCR              = 0x7f8001e4
DDR_REG_ECC_CHR                = 0x7f8001e8
DDR_REG_ECC_ERROR_ADDR         = 0x7f8001ec
DDR_REG_ECC_EBPLR              = 0x7f8001f0
DDR_REG_ECC_EBPHR              = 0x7f8001f4
DDR_REG_ECC_ERR1_COUNT         = 0x7f8001f8
DDR_REG_ECC_ERR2_COUNT         = 0x7f8001fc
DREG_BASE_ADDR                 = 0x7f800200
DREG_DDR_RST_CTL               = 0x7f800200
DREG_DDR_MODE                  = 0x7f800204
DREG_DDR_PLL_CFG               = 0x7f800208
DREG_DDR_PLL_LOCK_DLY          = 0x7f80020c
DREG_PHYPLL_PDN_DLY            = 0x7f800210
DREG_PHYPLL_LOCK_DLY           = 0x7f800214
DREG_PHYDLL_PDN_DLY            = 0x7f800218
DREG_PHY_RST_DLY               = 0x7f80021c
DREG_CTL_RST_DLY               = 0x7f800220
DREG_AXI_CFG                   = 0x7f800224
DREG_AXI_WSTAT_0               = 0x7f800228
DREG_AXI_WSTAT_1               = 0x7f80022c
DREG_AXI_RSTAT_0               = 0x7f800230
DREG_AXI_RSTAT_1               = 0x7f800234
DREG_MC_STAT                   = 0x7f800238
DREG_ERR_STAT                  = 0x7f80023c
LVDS_EN                        = 0x7f800300
LVDSPLL_CFG                    = 0x7f800304
LVDS_CFG                       = 0x7f800308
LVDS_TGEN_HCFG_0               = 0x7f80030c
LVDS_TGEN_VCFG_0               = 0x7f800310
LVDS_CTRL_CH0                  = 0x7f800314
LVDS_CTRL_CH1                  = 0x7f800318
LVDS_STAT                      = 0x7f80031c
LVDS_ERR_STAT                  = 0x7f800320
LVDS_TGEN_HCFG_1               = 0x7f800324
LVDS_TGEN_VCFG_1               = 0x7f800328
LVDS_TGEN_HCFG_2               = 0x7f80032c
LVDS_TGEN_VCFG_2               = 0x7f800330
DDR_PD_CFG                     = 0x7f800404
SYS_CFG                        = 0x7f800420
SYS_STAT_0                     = 0x7f800424
SYS_STAT_1                     = 0x7f800428
BOOT_STATUS                    = 0x7f80044c
SYS_FREQ                       = 0x7f800450
DDR_TYPE                       = 0x7f800454
SYS_STAT_2                     = 0x7f800458
SYS_GPREG                      = 0x7f80045c
SYS_STAT_3                     = 0x7f800460
PIN_DRV_2                      = 0x7f800464
PIN_SLEW_1                     = 0x7f800468
PIN_TYPE_2                     = 0x7f80046c
I2S_CFG                        = 0x7f800800
I2S_CTL                        = 0x7f800804
I2S_IRQ_EN                     = 0x7f800808
I2S_IRQ_STAT                   = 0x7f80080c
I2S_STAT                       = 0x7f800810
I2S_FIFO                       = 0x7f800830

# Enums

ADPCM_SAMPLES                  = 2
ALPHA                          = 5
ALWAYS                         = 7
ANIM_HOLD                      = 2
ANIM_LOOP                      = 1
ANIM_ONCE                      = 0
ARGB1555                       = 0
ARGB2                          = 5
ARGB4                          = 6
ARGB6                          = 23
ARGB8                          = 20
BARGRAPH                       = 11
BILINEAR                       = 1
BITMAPS                        = 1
BLUE                           = 4
BOOT_AUD                       = 32
BOOT_DDR                       = 0x80
BOOT_FLASH                     = 4
BOOT_FLASHFAST                 = 5
BOOT_HALT                      = 7
BOOT_JT                        = 0x40
BOOT_RAM0                      = 2
BOOT_REGULAR                   = 0
BOOT_SAFETY                    = 3
BOOT_SD                        = 6
BOOT_WARM                      = 1
BOOT_WD                        = 16
BORDER                         = 0
CMDBUF_SIZE                    = 0x4000
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
CORNER_ZERO                    = 0
CTOUCH_MODE_COMPATIBILITY      = 1
CTOUCH_MODE_EXTENDED           = 0
DECR                           = 4
DLSWAP_DONE                    = 0
DLSWAP_FRAME                   = 2
DREG_DDR_DISABLED_BIT          = 4
DREG_DDR_ENABLED_BIT           = 5
DST_ALPHA                      = 3
EDGE_STRIP_A                   = 7
EDGE_STRIP_B                   = 8
EDGE_STRIP_L                   = 6
EDGE_STRIP_R                   = 5
EDGE_ZERO                      = 1
EQUAL                          = 5
FLASH_STATUS_BASIC             = 2
FLASH_STATUS_DETACHED          = 1
FLASH_STATUS_FULL              = 3
FLASH_STATUS_INIT              = 0
GEQUAL                         = 4
GLFORMAT                       = 31
GREATER                        = 3
GREEN                          = 3
INCR                           = 3
INT_CMDEMPTY                   = 32
INT_CMDFLAG                    = 0x40
INT_CONVCOMPLETE               = 0x80
INT_G8                         = 18
INT_L8C                        = 12
INT_PLAYBACK                   = 16
INT_SOUND                      = 8
INT_SWAP                       = 1
INT_TAG                        = 4
INT_TOUCH                      = 2
INT_VGA                        = 13
INVERT                         = 5
KEEP                           = 1
L1                             = 1
L2                             = 17
L4                             = 2
L8                             = 3
LA1                            = 24
LA2                            = 25
LA4                            = 26
LA8                            = 27
LEQUAL                         = 2
LESS                           = 1
LINEAR_SAMPLES                 = 0
LINES                          = 3
LINE_STRIP                     = 4
NEAREST                        = 0
NEVER                          = 0
NOTEQUAL                       = 6
ONE                            = 1
ONE_MINUS_DST_ALPHA            = 5
ONE_MINUS_SRC_ALPHA            = 4
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
OPT_RIGHTX                     = 0x800
OPT_SFNLOWER                   = 1
OPT_SIGNED                     = 0x100
OPT_SIMULATION                 = 1
OPT_SOUND                      = 32
OPT_TRUECOLOR                  = 0x200
OPT_YCBCR                      = 0x400
PALETTED                       = 8
PALETTED4444                   = 15
PALETTED565                    = 14
PALETTED8                      = 16
PALETTEDARGB8                  = 21
POINTS                         = 2
RAM_CMD                        = 0x7f000000
RAM_DL                         = 0x7f008000
RAM_G                          = 0
RAM_HIMEM                      = 0x7f004800
RAM_J1CODE                     = 0x7f020000
RAM_J1RAM                      = 0x7f004000
RAM_JTBOOT                     = 0x7f005000
RAM_OTPSTAGE                   = 0x7f004c00
RAM_REG                        = 0x7f006000
RAM_ROMSUB                     = 0x7f027800
RAM_TOP                        = 0x304000
RECTS                          = 9
RED                            = 2
REG_CMDB_WRITE                 = 0x7f010000
REPEAT                         = 1
REPLACE                        = 2
RGB332                         = 4
RGB565                         = 7
RGB6                           = 22
RGB8                           = 19
ROM_ROMIMAGE                   = 0x7f100000
S16S_SAMPLES                   = 4
S16_SAMPLES                    = 3
SRC_ALPHA                      = 2
SS_A0                          = 19
SS_A1                          = 20
SS_A10                         = 30
SS_A2                          = 21
SS_A3                          = 22
SS_A32                         = 29
SS_A4                          = 23
SS_A5                          = 24
SS_A54                         = 28
SS_A6                          = 25
SS_A7                          = 26
SS_A76                         = 27
SS_PAUSE                       = 18
SS_Q0                          = 0
SS_Q1                          = 1
SS_Q2                          = 2
SS_Q3                          = 3
SS_Q4                          = 4
SS_Q5                          = 5
SS_Q6                          = 6
SS_Q7                          = 7
SS_Q8                          = 8
SS_Q9                          = 9
SS_QA                          = 10
SS_QB                          = 11
SS_QC                          = 12
SS_QD                          = 13
SS_QE                          = 14
SS_QF                          = 15
SS_QI                          = 31
SS_S0                          = 16
SS_S1                          = 17
SWAPCHAIN_0                    = 0xffff00ff
SWAPCHAIN_1                    = 0xffff01ff
SWAPCHAIN_2                    = 0xffff02ff
TC_100KHZ                      = 0x104
TC_BENCH                       = 0x106
TC_DEVICE                      = 0x103
TC_ECHO                        = 0x100
TC_I2CSCAN                     = 0x105
TC_REGREAD                     = 0x102
TC_REGWRITE                    = 0x101
TEXT8X8                        = 9
TEXTVGA                        = 10
TOUCHMODE_CONTINUOUS           = 3
TOUCHMODE_FRAME                = 2
TOUCHMODE_OFF                  = 0
TOUCHMODE_ONESHOT              = 1
TOUCH_100KHZ                   = 0x800
TOUCH_AR1021                   = 3
TOUCH_FOCALTECH                = 1
TOUCH_GOODIX                   = 2
TOUCH_ILI2511                  = 4
TOUCH_QUICKSIM                 = 0x8000
TOUCH_TSC2007                  = 5
ULAW_SAMPLES                   = 1
YCBCR                          = 28
ZERO                           = 0

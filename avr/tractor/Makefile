##########################################
# Makefile for robbus-connected project  #
# (c) Kamil Rezac 2009                   #
##########################################

# target file prefix (main source is $(TRG).c, output $(TRG).hex
	TRG = tractor

# directory with common code (modify as needed)
	COMMON_DIR = ../common

# command definitions
	CC	= avr-gcc
	AS	= avr-gcc -x assembler-with-cpp	
	RM	= rm -f
	RN	= mv
	CP	= cp
	BIN	= avr-objcopy
	SIZE	= avr-size
	INCDIR	= .

# output format can be srec, ihex (avrobj is always created)
	FORMAT = ihex

# MCU type
	MCU = atmega8

# common includes (modify as needed)
	COMMON_INC = $(COMMON_DIR)

	COMMON_SRC = $(COMMON_DIR)/robbus.c $(COMMON_DIR)/tick2.c $(COMMON_DIR)/adc.c $(COMMON_DIR)/i2c.c

# list of source files, add application-specific files here
	SRC= $(COMMON_SRC) $(TRG).c

# additional directory with includes
	INC	= $(COMMON_INC)

# compiler flags
	CPFLAGS	= -g -Os -Wall -Wstrict-prototypes -I$(INC) -Wa,-ahlms=$(<:.c=.lst) -mmcu=$(MCU)

# linker flags
	LDFLAGS = -Wl,-Map=$(TRG).map,--cref -mmcu=$(MCU)

# list of object file (no need to modify)
	OBJ	= $(SRC:.c=.o)

#main build target (build starts here)
all:	$(TRG).elf $(TRG).hex $(TRG).ok

# generic object file build rule for c source file
%.o : %.c 
	$(CC) -c $(CPFLAGS) -I$(INCDIR) $< -o $@

# generic assembly file build rule for c source file
%.s : %.c
	$(CC) -S $(CPFLAGS) -I$(INCDIR) $< -o $@

# link rule to create elf file form object files
%.elf: $(OBJ)
	$(CC) $(OBJ) $(LIB) $(LDFLAGS) -o $@

# rule for creating output file (for programming into device)
%.hex: %.elf
	$(BIN) -O $(FORMAT) -R .eeprom $< $@

# all target passed, display program size
%ok:
	$(SIZE) $(TRG).elf
	@echo "Errors: none"

# clean target (remove all files created during build
clean:
	$(RM) $(OBJ)
	$(RM) $(SRC:.c=.s)
	$(RM) $(SRC:.c=.lst)
	$(RM) $(TRG).map
	$(RM) $(TRG).elf
	$(RM) $(TRG).cof
	$(RM) $(TRG).obj
	$(RM) $(TRG).a90
	$(RM) $(TRG).hex
	$(RM) $(TRG).sym
	$(RM) $(TRG).eep
	$(RM) $(TRG).hex
	$(RM) *.bak
	$(RM) *.log
	@echo "Errors: none"

 
# include makefile for common robbus dependencies, modify according to placement

robbus.o: $(COMMON_DIR)/robbus.c $(COMMON_INC)/robbus.h robbus_config.h
tick0.o: $(COMMON_DIR)/tick0.c tick0.h
tick2.o: $(COMMON_DIR)/tick2.c tick2.h
adc.o: $(COMMON_DIR)/adc.c adc.h
i2c.o: $(COMMON_DIR)/i2c.c i2c.h robbus_config.h
$(TRG).o: $(TRG).c robbus_config.h

prog: all
	avrdude -p m8 -c stk500v2 -P /dev/biprog  -U flash:w:$(TRG).hex

prog_fuses:
	avrdude -p m8 -c stk500v2 -P /dev/biprog  -U lfuse:w:0x3f:m -U hfuse:w:0xD9:m

##########################################
# Makefile for robbus-connected project  #
# (c) Kamil Rezac 2009                   #
##########################################

# target file prefix (main source is $(TRG).c, output $(TRG).hex
	TRG = bridge

# directory with common code (modify as needed)

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
	MCU = atmega128

# MCU freq
 	F_CPU = 16000000L
# list of source files, add application-specific files here
	SRC= $(TRG).c

# additional directory with includes
	INC	= 

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

$(TRG).o: $(TRG).c 

prog: all
	avrdude -p m128 -c stk500v2 -b 115200 -P /dev/biprog  -U flash:w:$(TRG).hex

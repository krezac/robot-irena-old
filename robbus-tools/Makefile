OPTIMIZE       = -O2
WARNINGS       = -Wall #--pedantic

DEFS           =
LIBS           =

# You should not have to change anything below here.

CC             = gcc

CFLAGS         = -g $(WARNINGS) $(OPTIMIZE) $(DEFS) -I. -I..
CPPFLAGS       = $(CFLAGS)
LDFLAGS        = 

all: robbus_scan robbus_print robbus_sync robbus_set

OBJS           = 

clean:
	rm -rf robbus_scan robbus_sync robbus_print robbus_set
	rm -rf *.o

robbus_scan: robbus_scan.o RobbusComm.o RobbusNodeList.o RobbusShm.o SerialApiLinux.o
	$(CC) $(LDFLAGS) $^ -o $@

robbus_print: robbus_print.o RobbusShm.o RobbusNodeList.o
	$(CC) $(LDFLAGS) $^ -o $@

robbus_set: robbus_set.o RobbusShm.o RobbusNodeList.o
	$(CC) $(LDFLAGS) $^ -o $@

robbus_sync: robbus_sync.o RobbusComm.o RobbusNodeList.o RobbusShm.o SerialApiLinux.o
	$(CC) $(LDFLAGS) $^ -o $@

dep :
	makedepend -Y -- $(CPPFLAGS) -- $(OBJS:.o=.c) 2>/dev/null

# DO NOT DELETE

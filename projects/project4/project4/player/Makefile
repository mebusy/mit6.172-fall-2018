CC := /Volumes/eWORK/SDKs/opencilk-2.1.0/bin/clang -I/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include -L/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib
TARGET := leiserchess
SRC := util.c tt.c fen.c move_gen.c search.c eval.c end_game.c
OBJ := $(SRC:.c=.o)
UNAME := $(shell uname)




ifeq ($(PARALLEL),1)
	OS_TYPE := Parallel Linux
	PFLAG := -DPARALLEL -D_BSD_SOURCE -D_XOPEN_SOURCE=700
	# -g needed for test framework assertions
	#
	# switch -fdetach to -ftapir to enable Tapir optimization passes for better
	# performance.
	CFLAGS := -std=gnu99 -Wall -g -fcilkplus
	LDFLAGS= -Wall -lm  -ldl -lpthread 
else
ifeq ($(UNAME),Darwin)
	OS_TYPE := Mac
	PFLAG := -DMACPORT -D__MACH__ -D_XOPEN_SOURCE
	CFLAGS := -std=gnu99  -Wall -DNDEBUG -g
	LDFLAGS=  -Wall
else
	OS_TYPE := Linux
	#PFLAG := -D_XOPEN_SOURCE
	CFLAGS := -std=gnu99 -Wall -g
	LDFLAGS= -Wall -lm  -ldl -lpthread
endif
endif



include cilkutils.mk


ifeq ($(DEBUG),1)
	CFLAGS += -O0 -DDEBUG $(PFLAG)
else
	CFLAGS += -O3 -fcilkplus -DNDEBUG $(PFLAG)
endif

ifeq ($(REFERENCE),1)
	CFLAGS += -DRUN_REFERENCE_CODE=1
endif

CFLAGS += $(OTHER_CFLAGS)

LDFLAGS= -Wall -lm  -ldl -lpthread 

.PHONY : default clean


default : $(TARGET)

# Each C source file will have a corresponding file of prerequisites.
# Include the prerequisites for each of our C source files.
-include $(SRC:.c=.d)

# This rule generates a file of dependencies (i.e., a makefile) %.d
# from the C source file %.c.
%.d : %.c
	@set -e; rm -f $@; \
	$(CC) -MM -MT *.o -MP -MF $@.$$$$ $(CFLAGS) $<; \
	sed -e 's|\($*\)\.o[ :]*|\1.o $@ : |g' < $@.$$$$ > $@; \
	rm -f $@.$$$$*

# We could use the -MMD and -MP flags here to have this rule generate
# the dependencies file.
%.o : %.c
	$(CC) $(CFLAGS) -c $< -o $@

search.c: search_scout.c


leiserchess : leiserchess.o $(OBJ)
	$(CC) $^ $(LDFLAGS) -o $@ 

clean :
	rm -f *.o *.d* *~ $(TARGET)

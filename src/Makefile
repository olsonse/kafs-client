CFLAGS		= -g -O2 -Wall -Wsign-compare
INSTALL		= install
DESTDIR		=
ETCDIR		= /etc/kafs
BINDIR		= /usr/bin
DATADIR		= /usr/share/kafs-client
SPECFILE	= ../redhat/kafs-client.spec

LNS		:= ln -sf

###############################################################################
#
# Determine the current package version from the specfile
#
###############################################################################
VERSION		:= $(word 2,$(shell grep "^Version:" $(SPECFILE)))
CPPFLAGS	+= -DVERSION="\"$(VERSION)\""

###############################################################################
#
# Guess at the appropriate word size
#
###############################################################################
BUILDFOR	:= $(shell file /usr/bin/make | sed -e 's!.*ELF \(32\|64\)-bit.*!\1!')-bit

ifeq ($(BUILDFOR),32-bit)
CFLAGS		+= -m32
else
ifeq ($(BUILDFOR),64-bit)
CFLAGS		+= -m64
endif
endif

###############################################################################
#
# Build stuff
#
###############################################################################
all: aklog-kafs

aklog-kafs: aklog-kafs.c Makefile
	$(CC) $(CPPFLAGS) $(CFLAGS) $(LDFLAGS) -o $@ $< -lkrb5 -lcrypto -lkeyutils

###############################################################################
#
# Install everything
#
###############################################################################
install: all
	$(INSTALL) -D -m 0755 aklog-kafs $(DESTDIR)$(BINDIR)/aklog-kafs

###############################################################################
#
# Clean up
#
###############################################################################
clean:
	$(RM) aklog-kafs
	$(RM) *.o *~

distclean: clean

###############################################################################
#
# Build debugging
#
###############################################################################
show_vars:
	@echo VERSION=$(VERSION)

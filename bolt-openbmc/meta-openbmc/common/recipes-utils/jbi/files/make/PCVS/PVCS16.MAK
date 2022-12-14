#
#	Module:			makefile
#
#					Copyright (C) Altera Corporation 1998-2001
#
#	Description:	Makefile for JAM Bytecode Player
#

OBJS = \
	jbistub.obj \
	jbimain.obj \
	jbicomp.obj \
	jbijtag.obj


%if "$(MEM_TRACKER)" && "$(STATIC_MEMORY_SIZE)"
# MEMORY TRACKER ON, USE 'STATIC_MEMORY_SIZE' KB OF STATIC MEMORY
.c.obj :
	cl /W4 /AL /c /O2 /Zp1 /DPORT=DOS /DMEM_TRACKER /DUSE_STATIC_MEMORY=$(STATIC_MEMORY_SIZE) $<
%elseif "$(MEM_TRACKER)" && !"$(STATIC_MEMORY_SIZE)"
# MEMORY TRACKER ON, USE DYNAMIC MEMORY
.c.obj :
	cl /W4 /AL /c /O2 /Zp1 /DPORT=DOS /DMEM_TRACKER $<
%elseif !"$(MEM_TRACKER)" && "$(STATIC_MEMORY_SIZE)"
# MEMORY TRACKER OFF, USE 'STATIC_MEMORY_SIZE' KB OF STATIC MEMORY
.c.obj :
	cl /W4 /AL /c /O2 /Zp1 /DPORT=DOS /DUSE_STATIC_MEMORY=$(STATIC_MEMORY_SIZE) $<
%else !"$(MEM_TRACKER)" && !"$(STATIC_MEMORY_SIZE)"
# MEMORY TRACKER OFF, USE DYNAMIC MEMORY
.c.obj :
	cl /W4 /AL /c /O2 /Zp1 /DPORT=DOS $<
%endif

jbi.exe : $(OBJS)
	link /STACK:0x8000 $(OBJS), jbi.exe,,,,

# Dependencies:

jbistub.obj : \
	jbistub.c \
	jbiport.h \
	jbiexprt.h

jbimain.obj : \
	jbimain.c \
	jbiport.h \
	jbiexprt.h \
	jbijtag.h \
	jbicomp.h

jamcomp.obj : \
	jamcomp.c \
	jbiport.h \
	jbiexprt.h \
	jbicomp.h

jbijtag.obj : \
	jbijtag.c \
	jbiport.h \
	jbiexprt.h \
	jbijtag.h

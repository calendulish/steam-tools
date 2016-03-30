 PYTHONPATH =
CHMOD = /bin/chmod
MV = /bin/mv

define check_python_path
	@if [ ! -f $(PYTHONPATH)/python.exe ]; \
	then \
		echo -e "\n*********************************************"; \
		echo "I cannot found PYTHON in $(PYTHONPATH)"            ; \
		echo "Please, check if your python path is correct."     ; \
		echo -e "*********************************************\n"; \
		exit 1; \
	fi;
endef

define check_python
ifeq ($(OS),Windows_NT)
ifneq ($(PWD),)
ifdef PYTHONPATH
OK=1
else
$$(info *****************************************************************)
$$(info Set python version with: make PYTHONPATH=<WINDOWS-PYTHON-FOLDER> )
$$(info (NEVER USE Cygwin Python for build it. Use Windows Python)       )
$$(info *****************************************************************)
$$(error "")
endif
endif
endif

ifndef OK
$$(error This Makefile is only for Cygwin. Please, use the setup.py)
endif
endef

all: check_python steam-tools

check_python:
	$(eval $(call check_python))
	$(call check_python_path)

winpty:
	@if [ -f $@/build/winpty.dll ]; \
	then \
		echo "Nothing to be done for $@"; \
	else \
		$(CHMOD) +x ./$@/configure; \
		./$@/configure; \
		$(MV) -f config.mk $@/; \
		$(MAKE) -C $@; \
	fi;

steam-tools: winpty
	@if [ -f dist/library.zip ]; \
	then \
		echo "Nothing to be done for $@"; \
	else \
		$(PYTHONPATH)/python.exe setup.py py2exe CMK; \
	fi;

clean:
	rm -rf dist/ winpty/build/
	rm -f winpty/config.mk

.PHONY: winpty clean

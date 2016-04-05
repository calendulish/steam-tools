#
# Lara Maia <dev@lara.click> 2015 ~ 2016
#
# The Steam Tools is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The Steam Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

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
		./$@/configure 1>/dev/null; \
		$(MV) -f config.mk $@/; \
		if [ "$(FORCE32BITS)" == "1" ]; \
		then \
		    echo -e 'UNIX_CXX=i686-pc-cygwin-g++\nMINGW_CXX=i686-w64-mingw32-g++'; \
		    $(MAKE) UNIX_CXX=i686-pc-cygwin-g++ MINGW_CXX=i686-w64-mingw32-g++ -C $@; \
		else \
		    echo -e 'UNIX_CXX=x86_64-pc-cygwin-g++\nMINGW_CXX=x86_64-w64-mingw32-g++'; \
		    $(MAKE) -C $@; \
	    fi; \
	fi;

steam-tools: winpty
	@if [ -f dist/library.zip ]; \
	then \
		echo "Nothing to be done for $@"; \
	else \
		$(PYTHONPATH)/python.exe -u setup.py py2exe CMK FORCECYG; \
	fi;

clean:
	rm -rf dist/ winpty/build/
	rm -f winpty/config.mk

.PHONY: winpty clean

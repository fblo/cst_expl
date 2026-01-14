# This Makefile is part of Interact-IV's IV2US Tools.
# Interact-IV.com (c) 2014
# Authors:
#     - Sebastian Lauwers <slau@interact-iv.com>

SHELL := /bin/sh
ifeq ($(PREFIX),)
	PREFIX := /usr/local
endif
ifeq ($(PYTHON),)
	PYTHON := python
endif

# Small documentation for fellow developers:
# This is a very short and easy Makefile that will ensure that everything gets
# installed in the right place.
# 
# There are two actions that can be called in this
# Makefile: install and uninstall. The first one (install) is the default action
# which will be called if nothing is specified.
#
# The second way to interact with the Makefile is by passing two variables on
# the command line: DESTDIR and PREFIX. DESTDIR doesn't have a default value, as
# it is mainly used when building RPMs (and has no real usage outside of
# packaging). PREFIX, on the other hand, does have a default value: /usr/local.
# This means that the scripts will by default be installed to /usr/local/bin. If
# you wish to change the location, simply call:
#
#   PREFIX=/usr make install
#
# A full example, for example, could be:
#   DESTDIR=$RPM_BUILD_ROOT PREFIX=/usr make install
#
# The script below makes massive use of PHONY targets. This is a technique which
# allows to work with virtual targets, just because it's handy. The $^ variable
# means "all the dependencies". For example, inside install_scripts, $^ means
# $(script_sources).
#
# A number of helpers are provided by the Makefile as well:
#
#     make uninstall # deletes the scripts and non-python files
#     make version   # echoes the version of the package
#     make pybuild   # calls the build script for the python package
#     make pyinstall # calls the install script for the python package
#     make dist      # create a .tar.gz'd source distribution
#     make clean     # delete temporary files
#
# Please note that the pyinstall target is automatically called by make install.
# Another thing to note is that the python package can't be uninstalled. If you
# need the ability to uninstall, either use virtualenvs or the RPM package. If
# available, the PYTHON environment variable will be used as python interpreter.

# Add installable scripts on the following line
script_targets := iv-new-project iv-static-ports
# Add documentation files on the following line
doc_targets    := README.md

# Don't edit under this line, unless you're awesome.
install        := @install
install_exec   := $(install) -m 755
install_dir    := @mkdir -p
install_doc    := $(install) -m 644
binary_path    := $(DESTDIR)$(PREFIX)/bin
doc_path       := $(DESTDIR)$(PREFIX)/share/doc/interact-iv/iv2us-tools
rm             := @rm -f
cp             := @cp
untar          := @tar xf
archive        := @tar czf
pysetup        := $(PYTHON) setup.py
pyversion      := @$(pysetup) --version
package_name    = iv2us-tools-$(shell make version)
archive_name    = $(package_name).tar.gz

# Prepend src/ to all values in $(script_targets).
# Example: src/iv-new-project src/iv-static-ports
script_sources := $(addprefix src/,$(script_targets))
# Prepend $(binary_path) to all values in $(script_targets)
# Example: /usr/local/bin/iv-new-project /usr/local/bin/iv-static-ports
script_dests   := $(addprefix $(binary_path)/,$(script_targets))

# Main action
install: create_directories install_scripts install_docs pyinstall

# Uninstall
uninstall: remove_scripts remove_docs

# Build python extensions, if necessary
pybuild:
	@echo "Building python extensions."
	@CFLAGS="$(CFLAGS)" $(pysetup) build

# Install the python package
pyinstall:
	@echo "Installing python package."
	@$(pysetup) install --skip-build --root $(DESTDIR) --prefix $(PREFIX)

version:
	$(pyversion)

# Phony targets to organise Makefile
create_directories:
	@echo "Creating directory $(binary_path)."
	$(install_dir) $(binary_path)
	@echo "Creating directory $(doc_path)."
	$(install_dir) $(doc_path)

# Another phony target
install_scripts: $(script_sources)
	@echo "Installing $^ to $(binary_path)."
	$(install_exec) $^ $(binary_path)

install_docs: $(doc_targets)
	@echo "Installing $^ to $(doc_path)."
	$(install_doc) $^ $(doc_path)

# And yet another one
remove_scripts: $(script_dests)
	@echo "Removing $^."
	$(rm) $^

remove_docs:
	@echo "Removing $(doc_path)."
	$(rm) -r $(doc_path)

clean:
	@echo "Cleaning temporary files."
	$(rm) -r dist iv2us_tools.egg-info

dist:
	@echo "Creating source archive: dist/$(archive_name)"
	@# Create the python dist archive
	@$(pysetup) sdist >/dev/null 2>&1
	@# Extract the data it contains
	$(untar) dist/$(archive_name) -C dist
	@# Add the missing files (bash scripts and documentation)
	$(cp) $(doc_targets) Makefile dist/$(package_name)
	$(cp) $(script_sources) dist/$(package_name)/src
	@# Delete the old archive
	$(rm) -r dist/$(archive_name)
	@# Create the new archive
	$(archive) dist/$(archive_name) -C dist -- $(package_name)
	@# Delete the temporary files
	$(rm) -r dist/$(package_name)
	@# All done!

.PHONY: install create_directories install_scripts install_docs
.PHONY: uninstall remove_scripts remove_docs
.PHONY: pybuild pyinstall version
.PHONY: dist clean
.PHONY: $(script_sources) $(script_dests) $(doc_sources)

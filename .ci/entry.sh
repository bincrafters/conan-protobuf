#!/bin/bash

set -ex

# make sure that recipes are available even for new versions, not yet published
conan export conanfile.py bincrafters/stable
conan export conanfile_installer.py bincrafters/stable

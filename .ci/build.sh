#!/bin/bash

set -ex

conan create . conanfile.py bincrafters/testing -tf test_pacakge

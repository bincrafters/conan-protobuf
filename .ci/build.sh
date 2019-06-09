#!/bin/bash

set -ex

conan create . conanfile.py -tf test_pacakge

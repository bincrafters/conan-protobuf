#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os


class ProtobufConan(ConanFile):
    name = "protobuf"
    version = "3.5.1"
    url = "https://github.com/bincrafters/conan-protobuf"
    description = "Conan.io recipe for Google Protocol Buffers"
    license = "MIT"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    settings = "os", "arch", "compiler", "build_type"
    short_paths=True
    options = { "shared": [True, False],  
        "with_zlib": [True, False],
        "build_tests": [True, False],
        "build_binaries": [True, False],
        "static_rt": [True, False],
    }
    default_options = "with_zlib=False", "build_tests=False", "static_rt=True", "build_binaries=True"
    
    def configure(self):
        # Todo: re-enable shared builds when issue resolved
        if self.options.shared == True:
            raise ConanException("Shared builds not currently supported, see github issue: https://github.com/google/protobuf/issues/2502")
    
    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11]@conan/stable")
        if self.options.build_tests:
            self.requires("gtest/[>=1.7.0]@bincrafters/stable")

    def source(self):
        source_url = "https://github.com/google/protobuf"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version

        #Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["protobuf_BUILD_TESTS"] = self.options.build_tests
        cmake.definitions["protobuf_BUILD_PROTOC_BINARIES"] = self.options.build_binaries
        cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = self.options.static_rt
        cmake.definitions["protobuf_WITH_ZLIB"] = self.options.with_zlib
        # TODO: option 'shared' not enabled  cmake.definitions["protobuf_BUILD_SHARED_LIBS"] = self.options.shared
        cmake.configure(build_folder=self.build_subfolder)
        cmake.build()
        if self.options.build_tests:
            self.run("ctest")
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)


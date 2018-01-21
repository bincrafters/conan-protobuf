#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class ProtobufConan(ConanFile):
    name = "protobuf"
    version = "3.5.1"
    url = "https://github.com/bincrafters/conan-protobuf"
    description = "Conan.io recipe for Google Protocol Buffers"

    # Indicates License type of the packaged library
    license = "MIT"

    # Packages the license for the conanfile.py
    exports = ["LICENSE.md"]

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {"with_zlib": [True, False],
               "build_tests": [True, False],
               "static_rt": [True, False],
               # "shared": [True, False],  # Watch: https://github.com/google/protobuf/issues/2502
               }
    default_options = "with_zlib=False","build_tests=False","static_rt=True",
    
    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11@conan/stable")  # TODO: Make a range
        if self.options.build_tests:
            self.requires("gtest/1.7.0@bincrafters/stable")  # TODO: Make a range

    def source(self):
        repo_url = "https://github.com/google/protobuf.git"
        self.run("git clone -b v{0} {1} {2}".format(self.version, repo_url, self.source_subfolder))

    def build(self):
        cmake = CMake(self)
        cmake.definitions["protobuf_BUILD_TESTS"] = self.options.build_tests
        cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = self.options.static_rt
        # TODO: option 'shared' not enabled  cmake.definitions["protobuf_BUILD_SHARED_LIBS"] = self.options.shared  
        cmake.configure(build_folder=self.build_subfolder)
        cmake.build()
        if self.options.build_tests:
            self.run("ctest")
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["libprotobuf",]  # "protobuf-lite" too, but they are incompatible.


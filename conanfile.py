#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class ProtobufConan(ConanFile):
    name = "protobuf"
    version = "3.5.1"
    url = "https://github.com/bincrafters/conan-protobuf"
    homepage = "https://github.com/protocolbuffers/protobuf"
    author = "Bincrafters <bincrafters@gmail.com>"
    description = "Conan.io recipe for Google Protocol Buffers"
    topics = ("protocol-buffers", "protocol-compiler", "serialization", "rpc")
    license = "BSD-3-Clause"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True
    options = {"with_zlib": [True, False], "static_rt": [True, False], "fPIC": [True, False]}
    default_options = {"with_zlib": False, "static_rt": True, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11@conan/stable")

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["protobuf_BUILD_TESTS"] = False
        cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = self.options.static_rt
        cmake.definitions["protobuf_WITH_ZLIB"] = self.options.with_zlib
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        if self.options.build_tests:
            self.run("ctest")

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.defines = ["PROTOBUF_USE_DLLS"]

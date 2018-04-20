#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class ProtobufConan(ConanFile):
    name = "protobuf"
    version = "3.5.2"
    url = "https://github.com/bincrafters/conan-protobuf"
    homepage = "https://developers.google.com/protocol-buffers/"
    author = "Bincrafters <bincrafters@gmail.com>"
    description = "Protocol Buffers - Google's data interchange format"
    license = "BSD"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    settings = "os", "arch", "compiler", "build_type"
    short_paths=True
    options = {
        "shared": [True, False],
        "with_zlib": [True, False],
        "fPIC": [True, False],
    }
    default_options = (
        "with_zlib=False",
        "shared=False", "fPIC=True")

    def configure(self):
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11@conan/stable")

    def source(self):
        source_url = "https://github.com/google/protobuf"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_INSTALL_LIBDIR"] = "lib"
        cmake.definitions["protobuf_BUILD_TESTS"] = False
        cmake.definitions["protobuf_WITH_ZLIB"] = self.options.with_zlib
        if self.settings.compiler != 'Visual Studio':
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        else:
            cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = "MT" in self.settings.compiler.runtime
        cmake.configure(build_folder=self.build_subfolder)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self.build_subfolder)
        cmake = self.configure_cmake()
        cmake.install()
        if self.settings.os == "Macos" and self.options.shared:
            protoc = os.path.join(self.package_folder, "bin", "protoc")
            libprotoc = 'libprotocd.dylib' if self.settings.build_type == 'Debug' else 'libprotoc.dylib'
            libprotobuf = 'libprotobufd.dylib' if self.settings.build_type == 'Debug' else 'libprotobuf.dylib'
            for lib in [libprotoc, libprotobuf]:
                self.run("install_name_tool -change %s @executable_path/../lib/%s %s" % (lib, lib, protoc))
            libprotoc = os.path.join(self.package_folder, "lib", libprotoc)
            self.run("install_name_tool -change %s @loader_path/%s %s" % (libprotobuf, libprotobuf, libprotoc))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

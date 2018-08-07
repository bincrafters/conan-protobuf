#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import glob


class ProtobufConan(ConanFile):
    name = "protobuf"
    version = "3.6.1"
    url = "https://github.com/bincrafters/conan-protobuf"
    homepage = "https://github.com/google/protobuf"
    author = "Bincrafters <bincrafters@gmail.com>"
    description = "Protocol Buffers - Google's data interchange format"
    license = "BSD"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True
    options = {
        "shared": [True, False],
        "with_zlib": [True, False],
        "fPIC": [True, False],
    }
    default_options = (
        "with_zlib=False",
        "shared=False",
        "fPIC=True"
    )

    def _is_clang_x86(self):
        return self.settings.compiler == "clang" and self.settings.arch == "x86"

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC
            compiler_version = int(str(self.settings.compiler.version))
            if compiler_version < 14:
                raise tools.ConanException("On Windows, the protobuf/3.6.0 package can only be built with the Visual Studio 2015 or higher.")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11@conan/stable")

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_INSTALL_LIBDIR"] = "lib"
        cmake.definitions["protobuf_BUILD_TESTS"] = False
        cmake.definitions["protobuf_WITH_ZLIB"] = self.options.with_zlib
        if self.settings.compiler == 'Visual Studio':
            cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = "MT" in self.settings.compiler.runtime
        cmake.configure(build_folder=self.build_subfolder)
        return cmake

    def build(self):
        if self._is_clang_x86():
            cmake_file = os.path.join(self.source_subfolder, "cmake", "protoc.cmake")
            source = "target_link_libraries(protoc libprotobuf libprotoc)"
            target = "target_link_libraries(protoc libprotobuf libprotoc atomic)"
            tools.replace_in_file(cmake_file, source, target)
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self.source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()
        if self.settings.os == "Macos" and self.options.shared:
            protoc = os.path.join(self.package_folder, "bin", "protoc")
            with tools.chdir(os.path.join(self.package_folder, 'lib')):
                for l in glob.glob("*.dylib"):
                    command = 'otool -L %s' % l
                    self.output.warn(command)
                    self.run(command)
            libprotoc = 'libprotocd.%s.dylib' % self.version if self.settings.build_type == 'Debug'\
                else 'libprotoc.%s.dylib' % self.version
            libprotobuf = 'libprotobufd.%s.dylib' % self.version if self.settings.build_type == 'Debug'\
                else 'libprotobuf.%s.dylib' % self.version
            for lib in [libprotoc, libprotobuf]:
                command = "install_name_tool -change %s @executable_path/../lib/%s %s" % (lib, lib, protoc)
                self.output.warn(command)
                self.run(command)
            libprotoc = os.path.join(self.package_folder, "lib", libprotoc)
            command = "install_name_tool -change %s @loader_path/%s %s" % (libprotobuf, libprotobuf, libprotoc)
            self.output.warn(command)
            self.run(command)
            with tools.chdir(os.path.join(self.package_folder, 'lib')):
                for l in glob.glob("*.dylib"):
                    command = 'otool -L %s' % l
                    self.output.warn(command)
                    self.run(command)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
            if self._is_clang_x86():
                self.cpp_info.libs.append("atomic")

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class ProtobufConan(ConanFile):
    name = "protobuf"
    version = "3.5.2"
    url = "https://github.com/bincrafters/conan-protobuf"
    homepage = "https://github.com/protocolbuffers/protobuf"
    author = "Bincrafters <bincrafters@gmail.com>"
    description = "Protocol Buffers - Google's data interchange format"
    topics = ("protocol-buffers", "protocol-compiler", "serialization", "rpc")
    license = "BSD-3-Clause"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True
    options = {"shared": [True, False], "with_zlib": [True, False], "fPIC": [True, False]}
    default_options = {"with_zlib": False, "shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    @property
    def _is_clang_x86(self):
        return self.settings.compiler == "clang" and self.settings.arch == "x86"

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11@conan/stable")
        self.requires("protoc_installer/3.5.2@bincrafters/stable")

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self, set_cmake_flags=True)
        cmake.definitions["protobuf_BUILD_TESTS"] = False
        cmake.definitions["protobuf_WITH_ZLIB"] = self.options.with_zlib
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = "MT" in self.settings.compiler.runtime
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        if self._is_clang_x86:
            cmake_file = os.path.join(self._source_subfolder, "cmake", "protoc.cmake")
            source = "target_link_libraries(protoc libprotobuf libprotoc)"
            target = "target_link_libraries(protoc libprotobuf libprotoc atomic)"
            tools.replace_in_file(cmake_file, source, target)
        if "arm" in str(self.settings.arch):
            cmake_file = os.path.join(self._source_subfolder, "cmake", "libprotobuf.cmake")
            source = "target_link_libraries(libprotobuf ${CMAKE_THREAD_LIBS_INIT})"
            target = "target_link_libraries(libprotobuf ${CMAKE_THREAD_LIBS_INIT} atomic)"
            tools.replace_in_file(cmake_file, source, target)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        if self.settings.os == "Macos" and self.options.shared:
            protoc = os.path.join(self.package_folder, "bin", "protoc")
            libprotoc = "libprotocd.dylib" if self.settings.build_type == "Debug" else "libprotoc.dylib"
            libprotobuf = "libprotobufd.dylib" if self.settings.build_type == "Debug" else "libprotobuf.dylib"
            for lib in [libprotoc, libprotobuf]:
                self.run("install_name_tool -change %s @executable_path/../lib/%s %s" % (lib, lib, protoc))
            libprotoc = os.path.join(self.package_folder, "lib", libprotoc)
            self.run("install_name_tool -change %s @loader_path/%s %s" % (libprotobuf, libprotobuf, libprotoc))

        # quirks to use protoc from protoc installer
        targets = os.path.join(self.package_folder, "lib", "cmake", "protobuf",
                               "protobuf-targets-%s.cmake" % str(self.settings.build_type).lower())
        if not os.path.isfile(targets):
            targets = os.path.join(self.package_folder, "cmake",
                                   "protobuf-targets-%s.cmake" % str(self.settings.build_type).lower())
        protoc = "protoc.exe" if self.settings.os == "Windows" else "protoc"
        build_type_upper = str(self.settings.build_type).upper()
        tools.replace_in_file(targets,
                              'IMPORTED_LOCATION_%s "${_IMPORT_PREFIX}/bin/%s"' % (build_type_upper, protoc),
                              'IMPORTED_LOCATION_%s "${PROTOC_BINARY}"' % build_type_upper)
        tools.replace_in_file(targets,
                              "set_property(TARGET protobuf::protoc APPEND PROPERTY IMPORTED_CONFIGURATIONS %s)"
                              % build_type_upper,
                              'find_program(PROTOC_BINARY protoc)\n'
                              'message(STATUS "PROTOC_BINARY ${PROTOC_BINARY}")\n'
                              'if(NOT PROTOC_BINARY)\n'
                              '    set(PROTOC_BINARY ${_IMPORT_PREFIX}/bin/%s)\n'
                              'endif()\n'
                              'set_property(TARGET protobuf::protoc APPEND PROPERTY IMPORTED_CONFIGURATIONS %s)'
                              % (build_type_upper, protoc))
        tools.replace_in_file(targets,
                              'list(APPEND _IMPORT_CHECK_FILES_FOR_protobuf::protoc "${_IMPORT_PREFIX}/bin/%s" )'
                              % protoc,
                              'list(APPEND _IMPORT_CHECK_FILES_FOR_protobuf::protoc "${PROTOC_BINARY}" )')

        os.unlink(os.path.join(self.package_folder, 'bin', protoc))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

            if self._is_clang_x86 or "arm" in str(self.settings.arch):
                self.cpp_info.libs.append("atomic")

        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.defines = ["PROTOBUF_USE_DLLS"]

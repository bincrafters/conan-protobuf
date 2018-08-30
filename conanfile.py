#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class ProtobufConan(ConanFile):
    name = "protobuf"
    version = "3.6.1"
    url = "https://github.com/bincrafters/conan-protobuf"
    homepage = "https://github.com/protocolbuffers/protobuf"
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

    @property
    def is_clang_x86(self):
        return self.settings.compiler == "clang" and self.settings.arch == "x86"

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC
            compiler_version = int(str(self.settings.compiler.version))
            if compiler_version < 14:
                raise tools.ConanException("On Windows, the protobuf/3.6.x package can only be built with the "
                                           "Visual Studio 2015 or higher.")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11@conan/stable")
        self.requires('protoc_installer/3.6.1@bincrafters/stable')

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
        if self.is_clang_x86:
            cmake_file = os.path.join(self.source_subfolder, "cmake", "protoc.cmake")
            source = "target_link_libraries(protoc libprotobuf libprotoc)"
            target = "target_link_libraries(protoc libprotobuf libprotoc atomic)"
            tools.replace_in_file(cmake_file, source, target)
        if "arm" in str(self.settings.arch):
            cmake_file = os.path.join(self.source_subfolder, "cmake", "libprotobuf.cmake")
            source = "target_link_libraries(libprotobuf ${CMAKE_THREAD_LIBS_INIT})"
            target = "target_link_libraries(libprotobuf ${CMAKE_THREAD_LIBS_INIT} atomic)"
            tools.replace_in_file(cmake_file, source, target)

        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self.source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()
        if self.settings.os == "Macos" and self.options.shared:
            protoc = os.path.join(self.package_folder, "bin", "protoc")
            libprotoc = 'libprotocd.%s.dylib' % self.version if self.settings.build_type == 'Debug'\
                else 'libprotoc.%s.dylib' % self.version
            libprotobuf = 'libprotobufd.%s.dylib' % self.version if self.settings.build_type == 'Debug'\
                else 'libprotobuf.%s.dylib' % self.version
            for lib in [libprotoc, libprotobuf]:
                command = "install_name_tool -change %s @executable_path/../lib/%s %s" % (lib, lib, protoc)
                self.run(command)
            libprotoc = os.path.join(self.package_folder, "lib", libprotoc)
            command = "install_name_tool -change %s @loader_path/%s %s" % (libprotobuf, libprotobuf, libprotoc)
            self.run(command)

        # quirks to use protoc from protoc installer
        targets = os.path.join(self.package_folder, "lib", "cmake", "protobuf",
                               "protobuf-targets-%s.cmake" % str(self.settings.build_type).lower())
        build_type_upper = str(self.settings.build_type).upper()
        tools.replace_in_file(targets,
                              'IMPORTED_LOCATION_%s "${_IMPORT_PREFIX}/bin/protoc"' % build_type_upper,
                              'IMPORTED_LOCATION_%s "${PROTOC_BINARY}"' % build_type_upper)
        tools.replace_in_file(targets,
                              'set_property(TARGET protobuf::protoc APPEND PROPERTY IMPORTED_CONFIGURATIONS %s)' % build_type_upper,
                              'find_program(PROTOC_BINARY protoc)\n'
                              'message(STATUS "PROTOC_BINARY ${PROTOC_BINARY}")\n'
                              'if(NOT PROTOC_BINARY)\n'
                              '    set(PROTOC_BINARY ${_IMPORT_PREFIX}/bin/protoc)\n'
                              'endif()\n'
                              'set_property(TARGET protobuf::protoc APPEND PROPERTY IMPORTED_CONFIGURATIONS %s)' % build_type_upper)
        tools.replace_in_file(targets,
                              'list(APPEND _IMPORT_CHECK_FILES_FOR_protobuf::protoc "${_IMPORT_PREFIX}/bin/protoc" )',
                              'list(APPEND _IMPORT_CHECK_FILES_FOR_protobuf::protoc "${PROTOC_BINARY}" )')

        os.unlink(os.path.join(self.package_folder, 'bin', 'protoc'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
            if self.is_clang_x86 or "arm" in str(self.settings.arch):
                self.cpp_info.libs.append("atomic")

        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.defines = ["PROTOBUF_USE_DLLS"]

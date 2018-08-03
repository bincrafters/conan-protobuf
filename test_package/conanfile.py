#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools, RunEnvironment
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def imports(self):
        self.copy(pattern="*.dylib", dst="bin", src="lib")

    def build(self):
        with tools.environment_append(RunEnvironment(self).vars):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        with tools.environment_append(RunEnvironment(self).vars):
            bin_path = os.path.abspath(os.path.join("bin", "test_package"))
            if self.settings.os == "Windows":
                self.run(bin_path)
            elif self.settings.os == "Macos":
                self.run("otool -L %s" % bin_path)
                # https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/DynamicLibraries/100-Articles/LoggingDynamicLoaderEvents.html
                debug_info = "DYLD_PRINT_LIBRARIES=1 " \
                             "DYLD_PRINT_LIBRARIES_POST_LAUNCH=1 " \
                             "DYLD_PRINT_APIS=1 " \
                             "DYLD_PRINT_STATISTICS=1 " \
                             "DYLD_PRINT_INITIALIZERS=1 " \
                             "DYLD_PRINT_SEGMENTS=1 " \
                             "DYLD_PRINT_BINDINGS=1"
                self.run("%s DYLD_LIBRARY_PATH=%s %s" % (debug_info, os.environ.get('DYLD_LIBRARY_PATH', ''), bin_path))
            else:

                self.run("LD_LIBRARY_PATH=%s %s" % (os.environ.get('LD_LIBRARY_PATH', ''), bin_path))

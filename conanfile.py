#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
import os


class ProtobufConan(ConanFile):
    name = "protobuf"
    version = "3.5.1"
    url = "https://github.com/bincrafters/conan-protobuf"
    description = "Conan.io recipes for Google Protocol Buffers"

    # Indicates License type of the packaged library
    license = "MIT"

    # Packages the license for the conanfile.py
    exports = ["LICENSE.md"]

    # Options may need to change depending on the packaged library.
    settings = "os", # "arch", "compiler", "build_type"
    """
    options = # TODO: compile for cpp, python, java,...
    default_options = "shared=False"
    """
    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def source(self):
        source_url = "https://github.com/google/protobuf"
        if self.settings.os == "Windows":
            raise NotImplementedError
        else:
            tools.get("{0}/releases/download/v{1}/protobuf-cpp-{1}.tar.gz".format(source_url, self.version))
            extracted_dir = self.name + "-" + self.version
            #Rename to "source_subfolder" is a convention to simplify later steps
            os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        if self.settings.os == "Windows":
            raise NotImplementedError
        else:
            with tools.chdir(self.source_subfolder):
                env_build = AutoToolsBuildEnvironment(self)
                env_build.configure(args=['--prefix', self.package_folder]) # ("../", build=False, host=False, target=False)
                env_build.make()
                env_build.make(args=['check',])
                env_build.make(args=['install',])

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)


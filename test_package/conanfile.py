#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools, RunEnvironment


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    requires = "protoc_installer/3.6.1@bincrafters/stable"

    def build(self):
        with tools.environment_append(RunEnvironment(self).vars):
            cmake = CMake(self, parallel=False)
            cmake.definitions["OPTIMIZED_FOR"] = "LITE_RUNTIME" if self.options["protobuf"].lite else "SPEED"
            cmake.configure()
            cmake.build()

    def test(self):
        bin_path = os.path.abspath(os.path.join("bin", "test_package"))
        self.run(bin_path, run_environment=True)

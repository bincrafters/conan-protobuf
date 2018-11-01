#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools, RunEnvironment


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        with tools.environment_append(RunEnvironment(self).vars):
            cmake = CMake(self, set_cmake_flags=True)
            cmake.configure()
            cmake.build()

    def test(self):
        bin_path = os.path.abspath(os.path.join("bin", "test_package"))
        self.run(bin_path, run_environment=True)
        self.run("protoc --version")

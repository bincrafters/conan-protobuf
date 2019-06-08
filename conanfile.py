#!/usr/bin/env python

from conans import tools
from conanfile_base import ConanFileBase
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class ConanFileDefault(ConanFileBase):
    name = ConanFileBase._base_name
    version = ConanFileBase.version
    exports = ConanFileBase.exports + ["conanfile_base.py"]

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "with_zlib": [True, False],
               "fPIC": [True, False],
               "lite": [True, False]}
    default_options = {"with_zlib": False,
                       "shared": False,
                       "fPIC": True,
                       "lite": False}

    @property
    def _is_clang_x86(self):
        return self.settings.compiler == "clang" and self.settings.arch == "x86"

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC
            compiler_version = Version(self.settings.compiler.version.value)
            if compiler_version < "14":
                raise ConanInvalidConfiguration("On Windows, the protobuf/3.6.x package can only be built with the "
                                           "Visual Studio 2015 or higher.")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11@conan/stable")

    def package(self):
        super(ConanFileDefault, self).package()
        self.copy("*.pdb", dst="lib", src=self._build_subfolder, keep_path=False)

        bindir = os.path.join(self.package_folder, "bin")
        if os.path.isdir(bindir):
            shutil.rmtree(bindir)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs.sort(reverse=True)

        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
            if self._is_clang_x86 or "arm" in str(self.settings.arch):
                self.cpp_info.libs.append("atomic")

        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.defines = ["PROTOBUF_USE_DLLS"]

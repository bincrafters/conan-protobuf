from conans import CMake, tools
from conanfile_base import ConanFileBase
import os
import shutil


class ConanFileInstaller(ConanFileBase):
    name = "protoc_installer"
    version = ConanFileBase.version
    exports = ConanFileBase.exports + ["protoc.patch"]

    settings = "os_build", "arch_build", "compiler", "arch"

    def requirements(self):
        self.requires.add("protobuf/{}@bincrafters/stable".format(self.version), private=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["protobuf_BUILD_TESTS"] = False
        cmake.definitions["protobuf_WITH_ZLIB"] = False
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = "MT" in self.settings.compiler.runtime
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        tools.patch(base_path=self._source_subfolder, patch_file="protoc.patch")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        super(ConanFileInstaller, self).package()

        libdir = os.path.join(self.package_folder, "lib")
        if os.path.isdir(libdir):
            shutil.rmtree(libdir)

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.arch

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        protoc = "protoc.exe" if self.settings.os_build == "Windows" else "protoc"
        self.env_info.PROTOC_BIN = os.path.normpath(os.path.join(self.package_folder, "bin", protoc))

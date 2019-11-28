from conans import CMake, tools
from conanfile_base import ConanFileBase
import os


class ConanFileInstaller(ConanFileBase):
    name = "protoc_installer"
    version = ConanFileBase.version
    exports = ConanFileBase.exports + ["protoc.patch"]

    settings = "os_build", "arch_build", "compiler", "arch", "build_type"

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
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.arch
        self.info.include_build_settings()

    def package_info(self):
        cmakedir = os.path.join("lib", "cmake", "protoc")
        protoc = "protoc"
        if self.settings.os_build == "Windows":
            cmakedir = "cmake"
            protoc = "protoc.exe"

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
        self.env_info.PROTOC_BIN = os.path.normpath(os.path.join(self.package_folder, "bin", protoc))

        self.cpp_info.builddirs = [cmakedir]
        self.cpp_info.build_modules = [
            os.path.join(cmakedir, "protoc-config.cmake"),
            os.path.join(cmakedir, "protoc-module.cmake"),
            os.path.join(cmakedir, "protoc-options.cmake"),
            os.path.join(cmakedir, "protoc-targets.cmake"),
            os.path.join(cmakedir, "protoc-targets-{}.cmake".format(str(self.settings.build_type).lower()))
        ]

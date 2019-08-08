from conans import ConanFile, tools
import os


class ConanFileBase(ConanFile):
    _base_name = "protobuf"
    version = "3.6.1"
    description = "Protocol Buffers - Google's data interchange format"
    topics = ("conan", "protobuf", "protocol-buffers", "protocol-compiler", "serialization", "rpc", "protocol-compiler")
    url = "https://github.com/bincrafters/conan-protobuf"
    homepage = "https://github.com/protocolbuffers/protobuf"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "BSD-3-Clause"
    exports = ["LICENSE.md", "conanfile_base.py"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    short_paths = True

    # Custom attributes for Bincrafters recipe conventions
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        sha256 = "3d4e589d81b2006ca603c1ab712c9715a76227293032d05b26fca603f90b3f5b"
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        extracted_dir = self._base_name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

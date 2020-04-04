from conans import ConanFile, tools
import os


class ConanFileBase(ConanFile):
    _base_name = "protobuf"
    version = "3.11.4"
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

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        sha256 = "A79D19DCDF9139FA4B81206E318E33D245C4C9DA1FFED21C87288ED4380426F9"
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        extracted_dir = self._base_name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os
import platform

import spack.compilers
from spack.package import *

_versions = {
    "9.0.0": {
        "Linux-aarch64": "e326b7800bfef47bdeefd2e3ec85804fc7aff163c0e577ba75bf18e905535b4c",
        "Linux-x86_64": "0945ee224a22ceeec42c7af27ae0952807bd8d01ac69b8ece51b68d25afa4d6a",
    },
    "8.1.32": {
        "Linux-aarch64": "e326b7800bfef47bdeefd2e3ec85804fc7aff163c0e577ba75bf18e905535b4c",
        "Linux-x86_64": "0945ee224a22ceeec42c7af27ae0952807bd8d01ac69b8ece51b68d25afa4d6a",
    },
    "8.1.30": {
        "Linux-aarch64": "aff06f4e5ed1d56d7e879052ba46fdfba06c20ea9c8a1267ca5114cd06207afb",
        "Linux-x86_64": "5497bbd41c0e1158800c0d4ed894cb7f113a7eb54a4ba0dc2ce47dd23ee6aaa1",
    },
}


class CrayGtl(Package):
    """Install cray-gtl"""

    homepage = "https://www.hpe.com/us/en/compute/hpc/hpc-software.html"
    url = "https://jfrog.svc.cscs.ch/artifactory/cray-mpich/cray-gtl-8.1.26.tar.gz"
    maintainers = ["bcumming", "simonpintarelli"]

    for ver, packages in _versions.items():
        key = "{0}-{1}".format(platform.system(), platform.machine())
        sha = packages.get(key)
        if sha:
            version(
                ver,
                sha256=sha,
                preferred=(ver == "8.1.32"),
                url=f"file:///data/user/ext-pintar_s/cray-mpich/cray-gtl-{ver}.{platform.machine()}.tar.gz",
            )

    variant("cuda", default=False)
    variant("rocm", default=False)
    conflicts("+cuda", when="+rocm", msg="Pick either CUDA or ROCM")

    # Fix up binaries with patchelf.
    depends_on("patchelf", type="build")

    conflicts("+cuda", when="+rocm", msg="Pick either CUDA or ROCM")

    with when("+cuda"):
        depends_on("cuda@11.0:11", type="link", when="@:8.1.26")
        depends_on("cuda@12.0:12", type="link", when="@8.1.27:")

    with when("+rocm"):
        # libamdhip64.so.5
        depends_on("hip@5:", type="link")
        # libhsa-runtime64.so.1
        depends_on("hsa-rocr-dev", type="link")

    def get_rpaths(self):
        # Those rpaths are already set in the build environment, so
        # let's just retrieve them.
        pkgs = os.getenv("SPACK_RPATH_DIRS", "").split(":")
        pkgs_store = os.getenv("SPACK_STORE_RPATH_DIRS", "").split(":")
        compilers = os.getenv("SPACK_COMPILER_IMPLICIT_RPATHS", "").split(":")
        return ":".join([p for p in pkgs + compilers + pkgs_store if p])

    def should_patch(self, file):
        # Returns true if non-symlink ELF file.
        if os.path.islink(file):
            return False
        try:
            with open(file, "rb") as f:
                return f.read(4) == b"\x7fELF"
        except OSError:
            return False

    def install(self, spec, prefix):
        install_tree(".", prefix)

    @property
    def libs(self):
        if "+cuda" in self.spec:
            return find_libraries("libmpi_gtl_cuda", root=self.prefix, shared=True)
        if "+rocm" in self.spec:
            return find_libraries("libmpi_gtl_hsa", root=self.prefix, shared=True)

    @run_after("install")
    def fixup_binaries(self):
        patchelf = which("patchelf")
        rpath = self.get_rpaths()
        for root, _, files in os.walk(self.prefix):
            for name in files:
                f = os.path.join(root, name)
                if not self.should_patch(f):
                    continue
                patchelf("--force-rpath", "--set-rpath", rpath, f, fail_on_error=False)
                # The C compiler wrapper can fail because libmpi_gtl_cuda refers to the symbol
                # __gxx_personality_v0 but wasn't linked against libstdc++.
                if "libmpi_gtl_cuda.so" in str(f):
                    patchelf("--add-needed", "libstdc++.so", f, fail_on_error=False)
                if "@8.1.27+cuda" in self.spec:
                    patchelf("--add-needed", "libcudart.so", f, fail_on_error=False)
                    patchelf("--add-needed", "libcuda.so", f, fail_on_error=False)

    @run_after("install")
    def fixup_pkgconfig(self):
        for root, _, files in os.walk(self.prefix):
            for name in files:
                if name[-3:] == ".pc":
                    f = os.path.join(root, name)
                    filter_file("@@PREFIX@@", self.prefix, f, string=True)

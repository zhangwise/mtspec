#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python bindings for multitaper `mtspec` f90 Library.

Python wrapper for the multitaper `mtspec` Fortran library::

    Prieto, G. A., R. L. Parker, F. L. Vernon. (2009),
    A Fortran 90 library for multitaper spectrum analysis,
    Computers and Geosciences, 35, pp. 1701-1710.

For more information see: https://github.com/krischer/mtspec

::

    Main Changes in 0.2.6
    ---------------------
    * Bugfix #6, access violation on windows
    * Refactoring parts of the underlying fortran code, now memchecked
    * Bugfix for NaNs in spectra
    * Bugfix RMS calculation in tests


:copyright:
    Lion Krischer, Moritz Beyreuther, and German A. Prieto
:license:
    GNU General Public License (GPL)
"""
from distutils.ccompiler import CCompiler
from distutils.errors import DistutilsExecError, CompileError
from distutils.unixccompiler import UnixCCompiler
from setuptools import find_packages, setup
from setuptools.extension import Extension

import inspect
import os
import platform
from subprocess import Popen, PIPE
import sys


# Import the version string.
path = os.path.join(os.path.abspath(os.path.dirname(inspect.getfile(
    inspect.currentframe()))), "mtspec")
with open(os.path.join(path, "VERSION.txt"), "rt") as fh:
    VERSION = fh.read().strip()


DOCSTRING = __doc__.strip().split("\n")


# Monkey patch the compilers to treat Fortran files like C files.
CCompiler.language_map['.f90'] = "c"
UnixCCompiler.src_extensions.append(".f90")


def _compile(self, obj, src, ext, cc_args, extra_postargs, pp_opts):
    compiler_so = self.compiler_so
    arch = platform.architecture()[0].lower()
    if ext == ".f90":
        if sys.platform == 'darwin' or sys.platform == 'linux2':
            compiler_so = ["gfortran"]
            cc_args = ["-O", "-fPIC", "-c", "-ffree-form"]
            # Force architecture of shared library.
            if arch == "32bit":
                cc_args.append("-m32")
            elif arch == "64bit":
                cc_args.append("-m64")
            else:
                print("\nPlatform has architecture '%s' which is unknown to "
                      "the setup script. Proceed with caution\n" % arch)
    try:
        self.spawn(compiler_so + cc_args + [src, '-o', obj] +
                   extra_postargs)
    except DistutilsExecError as msg:
        raise CompileError(msg)
UnixCCompiler._compile = _compile


# Hack to prevent build_ext from trying to append "init" to the export symbols.
class finallist(list):
    def append(self, object):
        return


class MyExtension(Extension):
    def __init__(self, *args, **kwargs):
        Extension.__init__(self, *args, **kwargs)
        self.export_symbols = finallist(self.export_symbols)


def get_libgfortran_dir():
    """
    Helper function returning the library directory of libgfortran. Useful
    on OSX where the C compiler oftentimes has no knowledge of the library
    directories of the Fortran compiler. I don't think it can do any harm on
    Linux.
    """
    for ending in [".3.dylib", ".dylib", ".3.so", ".so"]:
        try:
            p = Popen(['gfortran', "-print-file-name=libgfortran" + ending],
                      stdout=PIPE, stderr=PIPE)
            p.stderr.close()
            line = p.stdout.readline().decode().strip()
            p.stdout.close()
            if os.path.exists(line):
                return [os.path.dirname(line)]
        except:
            continue
        return []


src = os.path.join('mtspec', 'src', 'src') + os.sep
lib = MyExtension('mtspec',
                  libraries=["gfortran"],
                  library_dirs=get_libgfortran_dir(),
                  sources=[
                      src + 'spectra.f90', src + 'adaptspec.f90',
                      src + 'atanh2.f90',
                      src + 'df_spec.f90', src + 'dpss.f90',
                      src + 'dpss_ev.f90', src + 'dpss_spline.f90',
                      src + 'eigenft.f90', src + 'fdis.f90', src + 'fft.f90',
                      src + 'ftest.f90', src + 'ifft.f90',
                      src + 'jackspec.f90', src + 'mt_cohe.f90',
                      src + 'mt_deconv.f90', src + 'mt_transfer.f90',
                      src + 'mtspec.f90', src + 'nearn.f90',
                      src + 'nnls.f90', src + 'nsinv.f90',
                      src + 'nsqi.f90', src + 'oct_spec.f90',
                      src + 'psd_reshape.f90', src + 'pythag.f90',
                      src + 'qiinv.f90', src + 'qrfac.f90',
                      src + 'qsnorm.f90', src + 'qtdis.f90',
                      src + 'rsm_eig.f90', src + 'set_xint.f90',
                      src + 'sft.f90', src + 'sine_cohe.f90',
                      src + 'sine_psd.f90',
                      src + 'spline.f90', src + 'sym_fft.f90',
                      src + 'tinvit.f90', src + 'trbak1.f90',
                      src + 'tred1.f90', src + 'tridib.f90',
                      src + 'wv_spec.f90', src + 'wv_spec_to_array.f90',
                      src + 'xint.f90', src + 'yule.f90',
                      src + 'zqrfac.f90'])

setup_config = dict(
    name='mtspec',
    version=VERSION,
    description=DOCSTRING[0],
    long_description="\n".join(DOCSTRING[2:]),
    author=' Lion Krischer, Moritz Beyreuther, and German A. Prieto',
    author_email='krischer@geophysik.uni-muenchen.de',
    url='https://github.com/krischer/mtspec',
    license='GNU General Public License, version 3 (GPLv3)',
    platforms='OS Independent',
    install_requires=[
        'numpy',
    ],
    ext_package='mtspec.lib',
    ext_modules=[lib],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    keywords=['mtspec', 'multitaper', 'seismology', 'waveform',
              'signal', 'processing', 'taper', 'wigner', 'ville',
              'multitaper', 'seismology', 'signal processing'],
    packages=find_packages(),
    zip_safe=False,
    # this is needed for "pip install instaseis==dev"
    download_url=("https://github.com/krischer/mtspect/zipball/master"
                  "#egg=instaseis=dev"),
    include_package_data=True
)


if __name__ == "__main__":
    setup(**setup_config)

    # Attempt to remove the mod files once again.
    for filename in ["mvspectra.mod", "spectra.mod"]:
        try:
            os.remove(filename)
        except:
            pass

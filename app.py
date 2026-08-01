import sys
import types

# Parche temporal para evitar el error de distutils en Python 3.14 con librerías antiguas
if "distutils" not in sys.modules:
    distutils_mod = types.ModuleType("distutils")
    distutils_version = types.ModuleType("distutils.version")
    
    class LooseVersion:
        def __init__(self, vstring=None):
            self.vstring = vstring
        def __str__(self):
            return self.vstring or ""
        def __repr__(self):
            return f"LooseVersion ('{self.vstring}')"
        def _cmp(self, other):
            if isinstance(other, LooseVersion):
                return 0
            return -1
        def __lt__(self, other): return self._cmp(other) < 0
        def __le__(self, other): return self._cmp(other) <= 0
        def __gt__(self, other): return self._cmp(other) > 0
        def __ge__(self, other): return self._cmp(other) >= 0
        def __eq__(self, other): return self._cmp(other) == 0
        def __ne__(self, other): return self._cmp(other) != 0

    distutils_version.LooseVersion = LooseVersion
    sys.modules["distutils"] = distutils_mod
    sys.modules["distutils.version"] = distutils_version

# A partir de aquí puedes hacer tus importaciones normales
from quotexpy import Quotex
import streamlit as st
import pandas as pd

"""NPA Early Warning System -- RBI SupTech prototype package."""
import os
import tempfile

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "matplotlib")

__version__ = "0.5.0"


from enum import Enum


class ModuleTag(Enum):
    """
    Enumeration representing different types of built-in modules:

    - MONITOR (0): Modules need you monitor.
    - NORMAL (1): Modules work normally.
    - RISK (2): Modules have risk behaviors.
    - BLOCKED (3): Modules should be blocked or restricted .
    """
    MONITOR = 0
    NORMAL = 1
    RISK = 2
    BLOCKED = 3

module_levels = {
    "string": 1,
    "re": 2,
    "difflib": 1,
    "textwrap": 1,
    "unicodedata": 1,
    "stringprep": 1,
    "readline": 1,
    "rlcompleter": 1,
    "struct": 2,
    "codecs": 2,
    "datetime": 1,
    "zoneinfo": 1,
    "calendar": 1,
    "collections": 1,
    "collections.abc": 1,
    "heapq": 1,
    "bisect": 1,
    "array": 1,
    "weakref": 1,
    "types": 2,
    "copy": 2,
    "pprint": 1,
    "reprlib": 1,
    "enum": 1,
    "graphlib": 1,
    "numbers": 1,
    "math": 1,
    "cmath": 1,
    "decimal": 1,
    "fractions": 1,
    "random": 1,
    "statistics": 1,
    "itertools": 1,
    "functools": 1,
    "operator": 1,
    "pathlib": 3,
    "os.path": 3,
    "stat": 3,
    "filecmp": 3,
    "tempfile": 3,
    "glob": 3,
    "fnmatch": 3,
    "linecache": 1,
    "shutil": 3,
    "pickle": 2,
    "copyreg": 2,
    "shelve": 2,
    "marshal": 2,
    "dbm": 3,
    "sqlite3": 3,
    "zlib": 1,
    "gzip": 1,
    "bz2": 1,
    "lzma": 1,
    "zipfile": 3,
    "tarfile": 3,
    "csv": 1,
    "configparser": 1,
    "tomllib": 1,
    "netrc": 1,
    "plistlib": 1,
    "hashlib": 1,
    "hmac": 1,
    "secrets": 1,
    "os": 3,
    "io": 3,
    "time": 1,
    "logging": 1,
    "logging.config": 1,
    "logging.handlers": 1,
    "platform": 1,
    "errno": 1,
    "ctypes": 3,
    "argparse": 1,
    "optparse": 1,
    "getpass": 1,
    "fileinput": 1,
    "curses": 1,
    "curses.textpad": 1,
    "curses.ascii": 1,
    "curses.panel": 1,
    "threading": 2,
    "multiprocessing": 3,
    "multiprocessing.shared_memory": 3,
    "concurrent": 2,
    "concurrent.futures": 2,
    "subprocess": 3,
    "sched": 1,
    "queue": 1,
    "contextvars": 1,
    "_thread": 2,
    "asyncio": 3,
    "socket": 3,
    "ssl": 3,
    "select": 3,
    "selectors": 3,
    "signal": 3,
    "mmap": 3,
    "email": 1,
    "json": 1,
    "mailbox": 1,
    "mimetypes": 1,
    "base64": 1,
    "binascii": 1,
    "quopri": 1,
    "html": 1,
    "html.parser": 1,
    "html.entities": 1,
    "xml.etree.ElementTree": 1,
    "xml.dom": 1,
    "xml.dom.minidom": 1,
    "xml.dom.pulldom": 1,
    "xml.sax": 1,
    "xml.sax.handler": 1,
    "xml.sax.saxutils": 1,
    "xml.sax.xmlreader": 1,
    "xml.parsers.expat": 1,
    "webbrowser": 1,
    "wsgiref": 1,
    "urllib": 3,
    "urllib.request": 3,
    "urllib.response": 1,
    "urllib.parse": 1,
    "urllib.error": 1,
    "urllib.robotparser": 1,
    "http": 3,
    "http.client": 3,
    "ftplib": 3,
    "poplib": 3,
    "imaplib": 3,
    "smtplib": 3,
    "uuid": 1,
    "socketserver": 3,
    "http.server": 3,
    "http.cookies": 1,
    "http.cookiejar": 1,
    "xmlrpc": 3,
    "xmlrpc.client": 3,
    "xmlrpc.server": 3,
    "ipaddress": 1,
    "wave": 1,
    "colorsys": 1,
    "gettext": 1,
    "locale": 1,
    "turtle": 1,
    "cmd": 1,
    "shlex": 1,
    "tkinter": 1,
    "tkinter.colorchooser": 1,
    "tkinter.font": 1,
    "tkinter.messagebox": 1,
    "tkinter.scrolledtext": 1,
    "tkinter.dnd": 1,
    "tkinter.ttk": 1,
    "typing": 1,
    "pydoc": 1,
    "doctest": 1,
    "unittest": 1,
    "unittest.mock": 1,
    "test": 1,
    "test.support": 1,
    "test.support.socket_helper": 1,
    "test.support.script_helper": 1,
    "test.support.bytecode_helper": 1,
    "test.support.threading_helper": 1,
    "test.support.os_helper": 1,
    "test.support.import_helper": 1,
    "test.support.warnings_helper": 1,
    "bdb": 1,
    "faulthandler": 1,
    "pdb": 1,
    "timeit": 1,
    "trace": 1,
    "tracemalloc": 1,
    "ensurepip": 1,
    "venv": 1,
    "zipapp": 1,
    "sys": 2,
    "sys.monitoring": 2,
    "sysconfig": 1,
    "builtins": 0,
    "warnings": 1,
    "dataclasses": 1,
    "contextlib": 1,
    "abc": 1,
    "atexit": 1,
    "traceback": 2,
    "gc": 1,
    "inspect": 2,
    "site": 1,
    "code": 2,
    "codeop": 2,
    "zipimport": 2,
    "pkgutil": 2,
    "modulefinder": 2,
    "runpy": 2,
    "importlib": 2,
    "importlib.resources": 2,
    "importlib.resources.abc": 2,
    "importlib.metadata": 2,
    "ast": 1,
    "symtable": 1,
    "token": 1,
    "keyword": 1,
    "tokenize": 1,
    "tabnanny": 1,
    "pyclbr": 1,
    "py_compile": 1,
    "compileall": 1,
    "dis": 1,
    "pickletools": 1,
    "msvcrt": 1,
    "winreg": 3,
    "winsound": 1,
    "posix": 3,
    "pwd": 3,
    "grp": 3,
    "termios": 3,
    "tty": 3,
    "pty": 3,
    "fcntl": 3,
    "resource": 3,
    "syslog": 3
}

def get_module_by_level(tag:ModuleTag)->set[str]:
    return {module for module, level in module_levels.items() if level == tag.value}

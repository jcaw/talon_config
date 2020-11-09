from talon import Module, Context

from user.utils import dictify, expand_acronym


module = Module()
module.list(
    "file_suffixes", desc='Suffixes for file types (or URLs), e.g. "py" or "com".'
)


# Extensions that sound like they look
file_suffix_dict = dictify(
    [
        # Files
        "asp",
        "avi",
        "bak",
        "bat",
        "bin",
        "bin",
        "c",
        "cab",
        "class",
        "cur",
        "deb",
        "doc",
        "el",  # Elisp
        "exe",
        "gadget",
        "gif",
        "ico",
        "ini",
        "iso",
        "jar",
        "java",
        "log",
        "midi",
        "mov",
        "ogg",
        "part",
        "py",
        "rar",
        "sav",
        "swift",
        "talon",
        "tar",
        "tiff",
        "toast",
        "vob",
        "wav",
        "zip",
        "zip",
        # URLs
        "co",
        "com",
        "net",
        "org",
        "wiki",
    ]
)


# Filetypes spoken as acronyms
file_suffix_dict.update(
    {
        expand_acronym(s): s
        for s in [
            # Files
            "3g2",
            "3gp",
            "7z",
            "apk",
            "bmp",
            "cfg",
            "cfm",
            "cgi",
            "cgi",
            "cl",
            "cpl",
            "cpp",
            "cs",
            "css",
            "csv",
            "db",
            "dbf",
            "dll",
            "dmg",
            "dmp",
            "drv",
            "eml",
            "flv",
            "fnt",
            "fon",
            "h",
            "htm",
            "html",
            "icns",
            "js",
            "jsp",
            "lnk",
            "mdb",
            "mkv",
            "mp3",
            "mp4",
            "mpg",
            "msi",
            "odp",
            "ods",
            "odt",
            "oft",
            "ost",
            "otf",
            "pdf",
            "php",
            "pkg",
            "pl",
            "png",
            "pps",
            "ppt",
            "pptx",
            "ps",
            "psd",
            "pst",
            "rb",
            "rm",
            "rpm",
            "rss",
            "rtf",
            "sh",
            "sql",
            "svg",
            "swf",
            "tex",
            "tmp",
            "ttf",
            "tv",
            "txt",
            "txt",
            "vb",
            "vcd",
            "wma",
            "wmv",
            "wpd",
            "wpl",
            "wsf",
            "xhtml",
            "xls",
            "xlsm",
            "xlsx",
            "xml",
            "xml",
            # URLs
            "ca",
        ]
    }
)
# Phonetically different extensions
file_suffix_dict.update(
    {
        # Files
        "M peg": "mpeg",
        "a V": "avi",
        "ah vee": "avi",
        "asp X": "aspx",
        "avy": "avi",
        "doc X": "docx",
        "dump": "dmp",
        "ex ee": "exe",
        "eye co": "ico",
        "icons": "icns",
        "in ee": "ini",
        "jason": "json",
        "jay peg": "jpg",  # "jpeg" is inaccessible.
        "jif": "gif",
        "L": "el",
        "link": "lnk",
        "sir": "cer",
        "sis": "sys",
        "swiff": "swf",
        "tar dot G Z": "tar.gz",
        "temp": "tmp",
        # URLs
        "co dot UK": "co.uk",
    }
)

context = Context()
context.lists["user.file_suffixes"] = file_suffix_dict


@module.capture(rule="(dot | point) {user.file_suffixes}")
def file_suffix(m) -> str:
    return "." + m.file_suffixes

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
        "py",
        "el",  # Elisp
        "talon",
        "c",
        "exe",
        "midi",
        "ogg",
        "wav",
        "rar",
        "deb",
        "zip",
        "bin",
        "iso",
        "toast",
        "zip",
        "log",
        "sav",
        "tar",
        "bat",
        "bin",
        "gadget",
        "jar",
        "gif",
        "tiff",
        "asp",
        "part",
        "class",
        "java",
        "swift",
        "bak",
        "cab",
        "cur",
        "ini",
        "ico",
        "avi",
        "mov",
        "vob",
        "doc",
        # URLs
        "com",
        "co",
        "org",
        "net",
        "wiki",
    ]
)


# Filetypes spoken as acronyms
file_suffix_dict.update(
    dictify(
        map(
            expand_acronym,
            [
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
            ],
        )
    )
)
# Phonetically different extensions
file_suffix_dict.update(
    {
        # Files
        "jason": "json",
        "ex ee": "exe",
        "tar dot G Z": "tar.gz",
        "jif": "gif",
        "eye co": "ico",
        "jay peg": "jpg",  # "jpeg" is inaccessible.
        "asp X": "aspx",
        "sir": "cer",
        "dump": "dmp",
        "icons": "icns",
        "in ee": "ini",
        "link": "lnk",
        "temp": "tmp",
        "sis": "sys",
        "ah vee": "avi",
        "a V": "avi",
        "avy": "avi",
        "M peg": "mpeg",
        "swiff": "swf",
        "doc X": "docx",
        # URLs
        "co dot UK": "co.uk",
    }
)

context = Context()
context.lists["user.file_suffixes"] = file_suffix_dict


@module.capture(rule="dot {user.file_suffixes}")
def file_suffix(m) -> str:
    return "." + m.file_suffixes

import platform, shutil, subprocess

from talon import Module, Context


module = Module()
module.tag(
    "arch",
    "Active when the OS is Arch Linux. Will NOT match on derivatives like Manjaro.",
)
module.tag("manjaro", "Active when the OS is Manjaro.")
module.tag("ubuntu", "Active when the OS is Ubuntu.")
module.tag("debian", "Active when the OS is Debian.")
module.tag("fedora", "Active when the OS is Fedora.")


context = Context()


if platform.system() == "Linux" and shutil.which("lsb_release"):
    release_id_output = subprocess.run(
        ["lsb_release", "-i"], capture_output=True
    ).stdout.decode("utf-8")
    release_id = release_id_output.split(":", 1)[1].strip()

    if "arch" in release_id.lower():
        # TODO: Arch matching untested
        context.tags = ["user.arch"]
    elif "manjaro" in release_id.lower():
        # Manjaro matching is tested & works
        context.tags = ["user.manjaro"]
    elif "ubuntu" in release_id.lower():
        # TODO: Ubuntu matching untested
        context.tags = ["user.ubuntu"]
    elif "debian" in release_id.lower():
        # TODO: Debian matching untested
        context.tags = ["user.debian"]
    elif "fedora" in release_id.lower():
        # TODO: Fedora matching untested
        context.tags = ["user.fedora"]

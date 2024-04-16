from SimbioReader.constants import VERSION


def shVersion():
    code = {"a": "alpha", "b": "beta", "rc": "ReleaseCandidate", "f": "Final"}
    nVer = f"{VERSION[0]}.{VERSION[1]}"
    if VERSION[2] != 0:
        nVer += f".{VERSION[2]}"
    if VERSION[3].lower() != "f":
        nVer += f".{code[VERSION[3].lower()]}"
        if VERSION[4] != 0:
            nVer += f".{VERSION[4]}"
    return nVer


code = {"d": "dev", "a": "alpha", "b": "beta",
        "rc": "ReleaseCandidate", "f": "Final"}


class Vers:
    def __init__(self, ver: tuple):
        self.major = ver[0]
        self.minor = ver[1]
        self.bug = ver[2]
        self.type = ver[3]
        self.build = ver[4]

    def full(self):
        if self.type.lower()=='f':
            nVer = f"{self.major}.{self.minor}.{self.bug}"
        else:
            nVer = f"{self.major}.{self.minor}.{self.bug}.{code[self.type]}.{self.build}"
        return nVer

    def short(self):
        return f"{self.major}.{self.minor}"
    
    def __str__(self):
        return self.full()


version = Vers(VERSION)

# def get_version(version=None):
#     version = get_complete_version(version)
#     main = get_main_version(version)
#     sub = ''
#     if version[3] == 'alpha' and version[4] == 0:
#         git_changeset = get_git_changeset()
#         if git_changeset:
#             sub = f".dev{git_changeset}"
#     elif version[3] != 'final':
#         mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'rc'}
#         sub = f"{mapping[version[3]]}.{version[4]}"
#     return f"{main}.{sub}"


# def get_main_version(version=None):
#     version = get_complete_version(version)
#     parts = 2 if version[2] == 0 else 3
#     return '.'.join(str(x) for x in version[:parts])


# def get_complete_version(version=None):
#     if version is None:
#         version= VERSION
#     else:
#         assert len(version) == 5
#         assert version[3] in ('alpha', 'beta', 'rc', 'final')
#     return version


# @functools.lru_cache()
# def get_git_changeset():
#     """Return a numeric identifier of the latest git changeset.

#     The result is the UTC timestamp of the changeset in YYYYMMDDHHMMSS format.
#     This value isn't guaranteed to be unique, but collisions are very unlikely,
#     so it's sufficient for generating the development version numbers.
#     """
#     # Repository may not be found if __file__ is undefined, e.g. in a frozen
#     # module.
#     if '__file__' not in globals():
#         return None
#     repo_dir = path.dirname(path.dirname(path.abspath(__file__)))
#     git_log = subprocess.run(
#         'git log --pretty=format:%ct --quiet -1 HEAD',
#         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
#         shell=True, cwd=repo_dir+'/..', universal_newlines=True,
#     )
#     timestamp = git_log.stdout
#     tz = timezone.utc
#     try:
#         timestamp = datetime.fromtimestamp(int(timestamp), tz=tz)
#     except ValueError:
#         return None
#     return timestamp.strftime('%Y%m%d%H%M%S')


# types = {
#     'd': 'dev',
#     'a': 'alpha',
#     'b': 'beta',
#     'f': 'final',
# }


# class Version:
#     """Version Class
#         respecting the semantic versioning 2.0.0
#     """

#     def __init__(self, version: tuple):
#         self.version = version

#     @property
#     def version(self):
#         if self._type is None:
#             adv = ""
#         else:
#             adv = f"-{self._type}"
#             if self._build is not None:
#                 adv += f".{self._build}"
#         return f"{self._major}.{self._minor}.{self._patch}{adv}"

#     @version.setter
#     def version(self, version):
#         tags = ('_major', '_minor', '_patch', '_type', '_build')
#         for tag in tags:
#             setattr(self, tag, 0)
#         # version=version.split(".")
#         for i in range(len(version[0:3])):
#             if type(version[i]) is str:
#                 if version[i].isdigit():
#                     setattr(self, tags[i], int(version[i]))
#                 else:
#                     raise ValueError(
#                         f"{tags[i][1:].title()} version must be a number")
#             elif type(version[i]) is float:
#                 setattr(self, tags[i], int(version[i]))
#             elif type(version[i]) is int:
#                 setattr(self, tags[i], version[i])
#         if len(version) > 3:
#             if len(version[3]) == 1:
#                 if not version[3] in types.keys():
#                     raise ValueError(f"Unknown type {version[3]}")
#                 else:
#                     self._type = types[version[3]]
#             else:
#                 if not version[3] in types.values():
#                     raise ValueError(f"Unknown type {version[3]}")
#                 self._type = version[3]
#         else:
#             self._type = None
#         if len(version) == 5:
#             self._build = version[4]
#         else:
#             self._build = None

#     def __str__(self) -> str:
#         if self._type == "final":
#             return f"{self._major}.{self._minor}.{self._patch}"
#         else:
#             return self.version

#     def full(self) -> str:
#         return self.version

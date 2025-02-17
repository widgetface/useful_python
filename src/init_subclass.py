# __init_subclass__ is just a hook method. You can use it for anything you want.
# It is useful for both registering subclasses in some way, and for setting default attribute values on those subclasses.

from enum import Enum, auto

class RepositoryType(Enum):
    HG = auto()
    GIT = auto()
    SVN = auto()
    PERFORCE = auto()


class Repository:
    _registry = {t: {} for t in RepositoryType}

    def __init_subclass__(cls, scm_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if scm_type is not None:
            cls._scm_type = scm_type
            cls._registry[scm_type] = {}


class MainHgRepository(Repository, scm_type=RepositoryType.HG):
    def __init__(self, repo_name: str = None):
        self.repo_name = repo_name if repo_name else "main"
        self._registry[self._scm_type][repo_name] = self


class GenericGitRepository(Repository, scm_type=RepositoryType.GIT):
    pass


mr = MainHgRepository(repo_name="Dev")

print(mr._registry)

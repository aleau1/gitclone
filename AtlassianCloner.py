#!/usr/bin/env python 3.11.2
from abc import abstractmethod, abstractproperty, ABCMeta

class AbstractRegularExpression(metaclass=ABCMeta):
    @abstractproperty
    def pattern(self): ...


class HTTP_Pattern(AbstractRegularExpression):
    @property
    def pattern(self):
        return r"(?P<nose>^http\:)"

class HTTPS_Pattern(AbstractRegularExpression):
    @property
    def pattern(self):
        return r"(?P<nose>^https\:)"

class AtlassianURLCore_Pattern(AbstractRegularExpression):
    @property
    def pattern(self):
        return r"\/\/(?P<core>\w+@\w+\.\w{2,3})"
    
class URLTail_Pattern(AbstractRegularExpression):
    @property
    def pattern(self):
        return r"\/(?P<tail>[\w+|\_|\/|-]+\.git$)"


from re import search as re_search
from re import compile as re_compile
from re import Pattern

class TextParser:
    def readlines(self, filename):
        with open(filename, 'r') as target_handler:
            lines = target_handler.readlines()
        return lines

    def parse_lines(self, lines:list, regex_to_search:'Pattern'):
        self._regex_pattern = regex_to_search
        parsed_lines = []
        parsed_researches = []
        for line in lines:
            research = re_search(re_compile(regex_to_search), line)
            if research is not None:
                parsed_lines.append(line)
                parsed_researches.append(research)
        self._occurrences, self._researches = parsed_lines, parsed_researches
        return self._occurrences, self._researches

    def parse_file(self, filename:str, regex_to_search:'Pattern'):
        self._occurences, self._researches = self.parse_lines(self.readlines(filename), regex_to_search)

    @property
    def regex(self):
        return self._regex_pattern
    @property
    def occurrences(self):
        return self._occurrences
    @property
    def researches(self):
        return self._researches

class PatternValidator(TextParser):
    def verify(self, string:str, pattern:Pattern):
        if isinstance(string, str):
            super().parse_lines([string], pattern)
            if len(self.occurrences):
                return True
            else:
                return False
        else:
            raise TypeError()

class BaseURLPatternValidator(PatternValidator):
    def verify_nose_pattern(self, URL:str):
        nose_exists_within_url = False
        if super().verify(URL, HTTP_Pattern().pattern)\
            or super().verify(URL, HTTPS_Pattern().pattern):
            nose_exists_within_url = True
        return nose_exists_within_url

    @abstractmethod
    def verify_core_pattern(self, URL:str):
        pass

    def verify_tail_pattern(self, URL:str):
        tail_exists_within_url = False
        if super().verify(URL, URLTail_Pattern().pattern):
            tail_exists_within_url = True
        return tail_exists_within_url

    def verify_URL(self, URL:str):
        nose_exists_within_url = self.verify_nose_pattern(URL)
        core_exists_within_url = self.verify_core_pattern(URL)
        tail_exists_within_url = self.verify_tail_pattern(URL)
        if nose_exists_within_url and core_exists_within_url and tail_exists_within_url:
                return True
        else:
            return False


class AtlassianURLPatternValidator(BaseURLPatternValidator):
    def verify_core_pattern(self, URL:str):
        core_exists_within_url = False
        if super().verify(URL, AtlassianURLCore_Pattern().pattern):
            core_exists_within_url = True
        return core_exists_within_url
    

class AtlassianRepositoryURL:
    def __init__(self, URL:str):
        if AtlassianURLPatternValidator().verify_URL(URL):
            self._GitRepositoryURL = URL
        else:
            raise ValueError()
    @property
    def repository(self) -> str:
        return self._GitRepositoryURL


class AtlassianRepositoryFactory:
    def __init__(self):
        self.user_name = None
        self.project_name = None

    def __base_URL__(self):
        return "https://<user_name>@bitbucket.org/<project_name>/<repository_name>"

    def __URL_composer__(self, repository_name:str):
        base_URL = self.__base_URL__()
        if self.user_name != None and self.project_name != None:
            base_URL = base_URL.replace('<user_name>', self.user_name)
            base_URL = base_URL.replace('<project_name>', self.project_name)
            base_URL = base_URL.replace('<repository_name>', repository_name)
            return base_URL
        else:
            raise ValueError("Set corresponding properties first: self.user_name, self.project_name")

    def __URL_generator__(self, repository_name:str):
        URL = self.__URL_composer__(repository_name)
        return AtlassianRepositoryURL(URL).repository

    def list_generator(self, repo_names:list[str]):
        return [self.__URL_generator__(repo) for repo in repo_names]


from os.path import exists
from os import system
class AtlassianGitClone(AtlassianRepositoryFactory):
    def __init__(self, user_name:str):
        AtlassianRepositoryFactory.__init__(self)
        self.URL_pool = []
        self.repo_names = []
        self.user_name = user_name

    @staticmethod
    def component_cloning_message(URL:str, repo_name:str):
        print(f"Cloning {repo_name} @ {URL}")

    @staticmethod
    def component_already_installed_message(URL:str, repo_name:str):
        print(f"Component {repo_name} @ {URL} is already cloned locally!")

    def populate_URL_pool(self, project_name:str, repo_names:list[str]):
        self.project_name = project_name
        self.URL_pool += super().list_generator(repo_names)
        self.repo_names += repo_names

    def empty_URL_pool(self):
        self.URL_pool = []
        self.repo_names = []

    def clone(self):
        for URL, repo in zip(self.URL_pool, self.repo_names):
            repo_folder = repo.split('.')[0]
            if not exists(repo_folder):
                self.component_cloning_message(URL,repo_folder)
                system(f"git clone {URL}")
            else:
                self.component_already_installed_message(URL,repo_folder)
                continue

from os.path import realpath
from os import chdir
class AtlassianCloner(AtlassianGitClone):
    def __init__(self, user_name:str, path:str):
        AtlassianGitClone.__init__(self, user_name)
        chdir(realpath(path))


if __name__=="__main__":
    raise NotImplementedError()


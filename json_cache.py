"""
A tool for light-duty memoization, intended for use with APIs.
"""


import inspect
import json
import logging

from appdirs import AppDirs

from datetime import datetime, timezone
from functools import partial, wraps
from pathlib import Path
from typing import Any, Callable, Union

default_dirs = AppDirs()

DEFAULT_PATH = Path(default_dirs.user_cache_dir)


def cached(func = None, cache_dir: Path = None, max_size: int = 0, max_age: int = 0, force_update:bool = False) -> Callable:
    if cache_dir is None:
            frame = inspect.getframeinfo(inspect.currentframe().f_back)
            cache_dir = Path(default_dirs.user_cache_dir) / Path(frame.filename).stem
    if func is None:
        return partial(cached, cache_dir=cache_dir, max_size=max_size, max_age=max_age, force_update=force_update)
    @wraps(func)
    def cache_wrapper(*args, **kwargs):
        cache_file_path = Path(cache_dir) / f"{func.__name__}_cache"
        # Log a warning if a supplied argument does not have a good string representation
        for arg in args:
            warn_if_no_str(arg)
        for k, v in kwargs:
            warn_if_no_str(k)
            warn_if_no_str(v)
        call_string = f"{args}, {kwargs}"
        with JsonCache(cache_file_path, max_size=max_size, max_age=max_age, force_update=force_update) as cache:
            if call_string not in cache:
                cache.store(call_string, func(*args, **kwargs))
                logging.info("%s cached.", call_string)
            return cache.retrieve(call_string)
    return cache_wrapper


def warn_if_no_str(item: Any) -> None:
    """Logs a warning if the supplied item does not have a callable __str__ method."""
    if hasattr(item, "__str__") and callable(getattr(item, "__str__")):
        return
    logging.warning("%s does not have a good string representation. Cache may not behave as expected.")


def make_timestamp() -> float:
    """Returns a POSIX UTC timestamp."""
    return datetime.now(timezone.utc).timestamp()


class JsonCache:
    """
    Creates a persistent JSON based cache.
    Intended to be performant relative to a potentially slow API, not relative to built in lru_cache or similar.
    N.B. Rules for max size and max age are enforced when the file is saved, but the cache object may exceed limits while it is live in memory.
    """
    
    def __init__(self, cache_file_path:Union[Path] = DEFAULT_PATH, max_size: int = 0, max_age: int = 0, force_update: bool = False) -> None:        
        """
        Create a persistent JSON cache for a function.

        Keyword Arguments:
         - path: the path to the file in which the chache is to be stored
         - max_size: the maximum number of items the cache can store. 0 disables size checking. (default = 0)
         - max_age: the maximum age in seconds after which a cahced value must be replaced. 0 disables age checking. (default = 0)  
         - force_update: if set to True, fresh calls will be made regardless of cached status. (default = False)
        """
        self.cache_file_path = cache_file_path
        self.max_size = max_size
        self.max_age = max_age
        self.force_update = force_update
        self.cache: dict = {}
        
    def store(self, call: str, response: Any) -> None:
        """Stores the supplied call and response in the cache."""        
        self.cache[call] = (response, make_timestamp())

    def retrieve(self, call: str) -> Any:
        """Returns the response value of the supplied cached call."""
        return self.cache[call][0]

    def _purge_expired(self) -> None:
        """Deletes all entries older than max_age"""
        if not self.max_age:
            return
        old_calls = [call for call in self.cache if self._age_check(call) > self.max_age]
        for call in old_calls:
            self.cache.pop(call)

    def _age_check(self, call: str) -> float:
        """Returns the age in seconds of the supplied call in the cache."""
        return make_timestamp() - self.cache[call][-1]
    
    def _is_current(self, call: str) -> bool:
        """
        Returns True if the supplied call is current in the cache.
        If force_update is set to True, always returns False. If max_age is 0, always returns True.
        """
        if self.force_update:
            return False
        if not self.max_age:
            return True
        return self._age_check(call) < self.max_age

    def _purge_n_oldest(self, count:int = 1) -> None:
        """Deletes the oldest n entry in the cache."""
        sorted_entries = sorted(self.cache.items(), key=lambda x: x[-1][-1])
        # Entries in the cache are stored in the form {call: (response, timestamp)}
        # so x[-1][-1] grabs the entry's timestamp
        for entry in sorted_entries[:count]:
            self.cache.pop(entry[0])
    
    def _cull_to_size(self) -> None:
        """Determines if max_size has been exceeded, and if so deletes the oldest entries until the size of the cache is complient."""
        if not self.max_size:
            return
        if len(self.cache) > self.max_size:
            self._purge_n_oldest(len(self.cache) - self.max_size)
    
    def write_file(self) -> None:
        if not self.cache_file_path.parent.exists():
            self.cache_file_path.parent.mkdir(parents=True)
        with open(self.cache_file_path, "w") as cache_file:
            json.dump(self.cache, cache_file)

    def read_file(self) -> None:
        """Opens the associated cache file, and loads the file's contents to the cache dict."""
        if not self.cache_file_path.exists():
            self.cache = dict()
            return
            #self.cache_file_path.parent.mkdir(parents=True)
        with open(self.cache_file_path, "r") as cache_file:
            contents = cache_file.read()
            if contents:
                self.cache = json.loads(contents)
            else:
                self.cache = dict()

    def __contains__(self, item):
        return item in self.cache and self._is_current(item)

    def __len__(self):
        return len(self.cache)

    def __repr__(self) -> str:
        return f"<JsonCache Object {hex(id(self))} storing {len(self)} items>"

    def __str__(self) -> str:
        return str(self.cache)

    def __enter__(self):
        self.read_file()
        return self
        
    def __exit__(self, *args, **kwargs):
        self._purge_expired()
        self._cull_to_size()
        self.write_file()
        

"""

each cache has:
 - a file (defaults to ./cache/{name_of_function}.json)
 - a list of update conditions
 - a max size
 - a max age
 - the actual cache

each entry looks like:
 - {argument string: (value, age)}


at some point we need to:
- open the file for writing
- read the files contents into a new JsonCache object
- 

"""

def test_1():
    print(DEFAULT_PATH)

def import_inspect_test():
    return inspect.stack()[-2].function

#print(import_inspect_test())

if __name__ == "__main__":
    test_cache = JsonCache()
    test_cache.store("test_call", "thank you!")
    print("")
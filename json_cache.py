"""A local JSON cache"""

#! Issues
#! 
#! Design
#! - How many caches? (one per cached method?) 
#!
#! Process
#! - getting the name of the cached method
#!   - inspect.getframeinfo(f.f_back) gets the info of the calling frame
#! - generating the call string


import inspect
import json

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Union

DEFAULT_PATH = Path(__file__).parent / "cache" / "test_cache"
#DEFAULT_PATH = Path(__file__) / "cache" / str(inspect.stack()[1].filename)


def make_timestamp() -> float:
    """Returns a POSIX UTC timestamp."""
    return datetime.now(timezone.utc).timestamp()


class JsonCache:
    """
    N.B. Rules for max size and max age are enforced when the file is saved, but the cache object may exceed limits while it is live in memory.
    """
    
    def __init__(self, file_path:Union[Path, str] = DEFAULT_PATH, max_size: int = 0, max_age: int = 0, force_update: bool = False) -> None:        
        """
        Create a JSON cache for a function.

        Keyword Arguments:
         - path: the path to the file in which the chache is to be stored
         - max_size: the maximum number of items the cache can store. 0 disables size checking. (default = 0)
         - max_age: the maximum age in seconds after which a cahced value must be replaced. 0 disables age checking. (default = 0)  
         - force_update: if set to True, fresh calls will be made regardless of cached status. (default = False)
        """
        self.file_path = file_path
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
        if not self.file_path.parent.exists():
            self.file_path.parent.mkdir(parents=True)
        
        with open(self.file_path, "w") as cache_file:
            json.dump(self.cache, cache_file)

    def read_file(self) -> None:
        """Opens the associated cache file, and loads the file's contents to the cache dict."""
        if not self.file_path.parent.exists():
            self.file_path.parent.mkdir(parents=True)
        
        with open(self.file_path, "r") as cache_file:
            contents = cache_file.read()
            if contents:
                self.cache = json.loads(contents)
            else:
                self.cache = dict()

    def __contains__(self, item):
        return item in self.cache

    def __len__(self):
        return len(self.cache)

    def __repr__(self) -> str:
        return f"<JsonCache Object {hex(id(self))} storing {len(self)} items>"

    def __str__(self) -> str:
        return str(self.cache)

    def __enter__(self):
        self.read_file()
        return self
        
    def __exit__(self):
        self._purge_expired()
        self._cull_to_size()
        self.write_file()
        

"""
use a decorator to tag cahceable functions
something like:
@json_cahce(max_size = 10)

use a context manager to trigger cache cleanup


update_conditions = [
    # A series of callables that return true if the item should be updated
    is_not_cached,
    is_too_old,
    force_update,
]


Caching logic
 - on call, load the cache as a dict
 - if the item is in the cached and none of the update conditions are met, return cached value
 - else, run the fuction and cache the response
 - if the cache is over capacity, delete the oldest item until it's not
 - overwrite the cache file


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
    test_cache._store("test_call", "thank you!")
    print("")
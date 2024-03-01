# Copyright 2024 Market Logic Software AG. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
This module contains caching functions and classes used by the DeepSights API.
"""

from cachetools import LRUCache


#################################################
def create_global_lru_cache(maxsize):
    """
    Create a global LRU cache with the specified maximum size.

    Args:

        maxsize (int): The maximum number of items that can be stored in the cache.

    Returns:
    
        tuple: A tuple containing five functions: _setter, _tester, _getter, _remover, and _size.
            - _setter: A function that sets a key-value pair in the cache.
            - _tester: A function that checks if a key exists in the cache.
            - _getter: A function that retrieves the value associated with a key from the cache.
            - _remover: A function that removes a key-value pair from the cache.
            - _size: A function that returns the maximum size of the cache.
    """
    cache = LRUCache(maxsize=maxsize)

    def _setter(key, value):
        if value is None:
            if key in cache:
                del cache[key]
        else:
            cache[key] = value

    def _getter(key):
        return cache.get(key)

    def _tester(key):
        return key in cache

    def _remover(key):
        if key in cache:
            del cache[key]

    def _size():
        return maxsize

    return _setter, _tester, _getter, _remover, _size

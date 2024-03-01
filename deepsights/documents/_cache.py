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
This module contains the functions to cache documents and document pages.
"""

from deepsights.utils import create_global_lru_cache

#############################################
# a global static LRU cache for 1k docs
(
    set_document,
    has_document,
    get_document,
    remove_document,
    get_document_cache_size,
) = create_global_lru_cache(1000)

#############################################
# a global static LRU cache for 100k pages
(
    set_document_page,
    has_document_page,
    get_document_page,
    remove_document_page,
    get_document_page_cache_size,
) = create_global_lru_cache(100000)

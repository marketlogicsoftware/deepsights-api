# Copyright 2024-2025 Market Logic Software AG. All Rights Reserved.
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
This module contains resource classes for managing custom taxonomies.
"""

from deepsights.api import APIResource
from deepsights.documentstore.resources.taxonomies._taxon_crud import (
    taxon_create,
    taxon_delete,
    taxon_search,
    taxon_update,
)
from deepsights.documentstore.resources.taxonomies._taxon_type_crud import (
    taxon_type_create,
    taxon_type_delete,
    taxon_type_update,
)
from deepsights.documentstore.resources.taxonomies._taxonomy_crud import (
    taxonomy_create,
    taxonomy_delete,
    taxonomy_search,
    taxonomy_update,
)


#################################################
class TaxonomyResource(APIResource):
    """
    Resource for managing custom taxonomies.

    Provides methods to create, update, delete, and search taxonomies.
    """

    create = taxonomy_create
    update = taxonomy_update
    delete = taxonomy_delete
    search = taxonomy_search


#################################################
class TaxonTypeResource(APIResource):
    """
    Resource for managing taxon types within taxonomies.

    Provides methods to create, update, and delete taxon types.
    """

    create = taxon_type_create
    update = taxon_type_update
    delete = taxon_type_delete


#################################################
class TaxonResource(APIResource):
    """
    Resource for managing taxons within taxonomies.

    Provides methods to create, update, delete, and search taxons.
    """

    create = taxon_create
    update = taxon_update
    delete = taxon_delete
    search = taxon_search

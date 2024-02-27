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

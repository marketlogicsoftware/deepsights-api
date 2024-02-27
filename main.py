import deepsights

# create a new instance of the DeepSights API, assuming api key is set in the environment as DEEPSIGHTS_API_KEY
ds = deepsights.DeepSights()

# search document matches for an ADA-002 query vector
document_results = deepsights.documents_search(
    ds,
    query_embedding=[0.1] * 1536,  # please use a real query one!
    max_results=10,
)

# search again, but this time re-rank the results based on recency
document_results_recency = deepsights.documents_search(
    ds,
    query_embedding=[0.1] * 1536,
    max_results=10,
    recency_weight=0.7,
)

# load the docs with their pages; we might as well have passed "load_documents=True" to the search function
documents = deepsights.documents_load(
    ds,
    document_ids=[r.id for r in document_results],
    load_pages=True,
)

# get the first dod
top_document = documents[0]
print(top_document.title)

# create a new instance of the ContentStore API, assuming api key is set in the environment as CONTENTSTORE_API_KEY
cs = deepsights.ContentStore()

# search for news; no need for further loading, all content present in the search results
news_results = deepsights.news_search(
    cs,
    query_embedding=[0.1] * 1536,
    max_results=10,
)

# search for reports; no need for further loading, all content present in the search results
# news and reports also support recency weighting
report_results = deepsights.secondary_search(
    cs,
    query_embedding=[0.1] * 1536,
    max_results=10,
    recency_weight=0.9,
)

# we can also use hybrid search for news and reports; this will first combine recency weighting and then merge text & vector results
# note that document search currently does not expose the hybrid search functionality
hybrid_results = deepsights.secondary_search(
    cs,
    query_embedding=[0.1] * 1536,
    query="foo bar baz",
    max_results=10,
    vector_weight=0.7,
    recency_weight=0.9,
)

# and we can promote exact title matches to the top for hybrid or text search
# for pure full-text search, omit the query_embedding
hybrid_results_promote = deepsights.secondary_search(
    cs,
    query="foo bar baz",
    max_results=10,
    vector_weight=0.7,
    recency_weight=0.9,
    promote_exact_match=True,
)

"""Template for building a `dlt` pipeline to ingest data from a REST API."""

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig


@dlt.source
def open_library_rest_api_source(
    query: str = "harry potter",
):
    """Search for books using the Open Library Search API.

    Args:
        query: Plain-text search query, for example "harry potter".

    Example:
        pipeline.run(open_library_rest_api_source(query="harry potter"))
    """
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://openlibrary.org/",
            "headers": {
                "User-Agent": "dlt-workshop (contact@example.org)",
            },
        },
        "resources": [
            {
                "name": "books",
                "endpoint": {
                    "path": "search.json",
                    "params": {
                        "q": query,
                        "limit": 100,
                    },
                    "data_selector": "docs",
                },
                "primary_key": "key",
                "write_disposition": "replace",
            },
        ],
    }

    yield from rest_api_resources(config)


pipeline = dlt.pipeline(
    pipeline_name="open_library_pipeline",
    destination="duckdb",
    dev_mode=True,
    progress="log",
)


if __name__ == "__main__":
    load_info = pipeline.run(open_library_rest_api_source())
    print(load_info)  # noqa: T201

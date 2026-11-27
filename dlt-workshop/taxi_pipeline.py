"""Template for building a `dlt` pipeline to ingest data from a REST API."""

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig


@dlt.source
def taxi_pipeline_rest_api_source():
    """Load NYC Yellow Taxi trips from the paginated custom API."""
    config: RESTAPIConfig = {
        "client": {
            "base_url": (
                "https://us-central1-dlthub-analytics.cloudfunctions.net/"
                "data_engineering_zoomcamp_api"
            ),
        },
        "resources": [
            {
                "name": "yellow_taxi_trips",
                "write_disposition": "replace",
                "endpoint": {
                    "path": "",
                    "params": {"page_size": 1000},
                    "paginator": {
                        "type": "page_number",
                        "page_param": "page",
                        "base_page": 1,
                        "total_path": None,
                        "stop_after_empty_page": True,
                    },
                    "data_selector": "$[*]",
                },
            },
        ],
    }

    yield from rest_api_resources(config)


pipeline = dlt.pipeline(
    pipeline_name="taxi_pipeline",
    destination="duckdb",
    progress="log",
)


if __name__ == "__main__":
    load_info = pipeline.run(taxi_pipeline_rest_api_source())
    print(load_info)  # noqa: T201

import asyncio
import os
import time

import pytest

from quickbolt.clients import AioRequests

pytestmark = pytest.mark.client

root_dir = f"{os.path.dirname(__file__)}/{__name__.split('.')[-1]}"
headers = {}
url = "https://jsonplaceholder.typicode.com/users/1"


def test_request(batch=None, delay=0, report=True, **kwargs):
    pytest.aio_requests = AioRequests(root_dir=root_dir)
    pytest.run_info_path = pytest.aio_requests.logging.run_info_path

    batch = batch or {"method": "get", "headers": headers, "url": url}
    response = pytest.aio_requests.request(batch, delay=delay, report=report, **kwargs)

    assert response.get("duration")

    responses = response.get("responses")
    assert responses

    response_fields = [
        "description",
        "code_mismatch",
        "batch_number",
        "index",
        "method",
        "expected_code",
        "actual_code",
        "message",
        "url",
        "server_headers",
        "response_seconds",
        "delay_seconds",
        "utc_time",
        "headers",
    ]
    for field in response_fields:
        assert responses[0].get(field, "missing") != "missing"

    assert responses[0].get("actual_code") == "200"

    stream_path = kwargs.get("stream_path")
    if stream_path:
        assert os.path.exists(stream_path)
    else:
        assert responses[0].get("message")

    asyncio.run(pytest.aio_requests.logging.delete_run_info(root_dir))
    path = pytest.aio_requests.logging.log_file_path
    assert not os.path.exists(path)


def test_request_multiple():
    batch = [
        {"method": "get", "headers": headers, "url": url},
        {"method": "get", "headers": headers, "url": url},
    ]
    test_request(batch)


def test_request_delay():
    start = time.perf_counter()
    test_request(delay=2)
    stop = time.perf_counter() - start
    assert stop >= 2


def test_request_content_stream():
    stream_path = f"{pytest.run_info_path}/streamed_content.txt"
    test_request(stream_path=stream_path)


def test_request_report():
    test_request(report=False)
    assert not os.path.exists(pytest.aio_requests.csv_path)

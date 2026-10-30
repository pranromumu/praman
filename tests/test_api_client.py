from unittest.mock import Mock

import pytest

from framework.api.client import ApiClient


@pytest.fixture
def api_client():
    context = Mock()
    client = ApiClient(context)
    return client, context


@pytest.mark.parametrize(
    "method",
    ["get", "post", "put", "patch", "delete"],
)
def test_api_client_delegates_request(method, api_client):
    client, context = api_client
    expected_response = Mock()

    getattr(context, method).return_value = expected_response

    response = getattr(client, method)("/users")

    getattr(context, method).assert_called_once_with("/users")
    assert response is expected_response


def test_api_client_forwards_request_options(api_client):
    client, context = api_client
    expected_response = Mock()
    context.post.return_value = expected_response

    response = client.post(
        "/users",
        data={"name": "Kabir"},
        headers={"X-Client": "PRAMAN"},
    )

    context.post.assert_called_once_with(
        "/users",
        data={"name": "Kabir"},
        headers={"X-Client": "PRAMAN"},
    )
    assert response is expected_response
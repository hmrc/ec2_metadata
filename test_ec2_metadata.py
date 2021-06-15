import pytest
import mock
import httpretty
import requests
import sys

from query_ec2_metadata import (
    main,
    imds,
    instance_identity,
    instance_identity_document,
    ec2_metadata,
)


def exceptionCallback(request, uri, headers):
    raise requests.ConnectionError("Connection Error.")


@httpretty.activate
def test_imds_returns_path_content_with_retries():
    httpretty.register_uri(
        httpretty.PUT,
        "http://169.254.169.254/latest/api/token",
        responses=[
            httpretty.Response("", status=429),
            httpretty.Response("", status=429),
            httpretty.Response("TEST_TOKEN_RANDOM_STRING", status=200),
        ],
    )

    responses = [httpretty.Response("", status=429) for i in range(9)]
    responses.append(httpretty.Response("test_host", status=200))

    httpretty.register_uri(
        httpretty.GET,
        "http://169.254.169.254/latest/meta-data/hostname",
        responses=responses,
    )
    assert imds("/meta-data/hostname") == "test_host"


@pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
@httpretty.activate
def test_imds_returns_path_content_with_connection_error():
    httpretty.register_uri(
        httpretty.PUT,
        "http://169.254.169.254/latest/api/token",
        body="TEST_TOKEN_RANDOM_STRING",
    )

    httpretty.register_uri(
        httpretty.GET,
        "http://169.254.169.254/latest/meta-data/hostname",
        responses=[
            httpretty.Response(body=exceptionCallback, status=200),
            httpretty.Response(body=exceptionCallback, status=200),
            httpretty.Response(body="test_host", status=200),
        ],
    )
    assert imds("/meta-data/hostname") == "test_host"


@httpretty.activate
def test_imds_raises_on_bad_response_code():
    httpretty.register_uri(
        httpretty.PUT,
        "http://169.254.169.254/latest/api/token",
        body="TEST_TOKEN_RANDOM_STRING",
    )

    httpretty.register_uri(
        httpretty.GET,
        "http://169.254.169.254/latest/meta-data/hostname",
        responses=[
            httpretty.Response(body="", status=500),
        ],
    )
    with pytest.raises(Exception) as e:
        imds("/meta-data/hostname")


@mock.patch("query_ec2_metadata.instance_identity")
def test_main_returns_id_key(mock_id, capsys):
    mock_id.return_value = "identity_document"
    testargs = ["instance-identity", "KEY"]

    with mock.patch.object(sys, "argv", testargs):
        main()

    captured = capsys.readouterr()
    assert captured.out == "identity_document"
    mock_id.assert_called_with("KEY")


@mock.patch("query_ec2_metadata.ec2_metadata")
def test_main_returns_metadata(mock_ec2_meta, capsys):
    mock_ec2_meta.return_value = "metadata"
    testargs = ["ec2-metadata", "KEY"]

    with mock.patch.object(sys, "argv", testargs):
        main()

    captured = capsys.readouterr()
    assert captured.out == "metadata"
    mock_ec2_meta.assert_called_with("KEY")


@mock.patch("query_ec2_metadata.imds")
def test_instance_identity_document_returns_id_doc(mock_imds):
    mock_imds.return_value = '{"test_key": "test_value"}'
    assert instance_identity_document() == {"test_key": "test_value"}
    mock_imds.assert_called_with("/dynamic/instance-identity/document")


@mock.patch("query_ec2_metadata.instance_identity_document")
def test_instance_identity_returns_id_key(mock_id_doc):
    mock_id_doc.return_value = {"test_key": "test_value"}
    assert instance_identity("test_key") == "test_value"


@mock.patch("query_ec2_metadata.imds")
def test_ec2_metadata_returns_id_key(mock_imds):
    assert ec2_metadata("key") == mock_imds.return_value
    mock_imds.assert_called_with("/meta-data/key")


def test_ec2_metadata_does_not_return_secure_creds():
    with pytest.raises(Exception) as e:
        ec2_metadata("iam/security-credentials/test_creds")
    assert (
        e.__str__()
        == "<ExceptionInfo Exception('iam/security-credentials/test_creds not available using this tool',) tblen=2>"
    )

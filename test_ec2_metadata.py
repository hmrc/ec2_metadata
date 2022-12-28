import sys
import unittest.mock as mock

import boto3
import httpretty
import pytest
import requests
from moto import mock_ec2
from requests import HTTPError

from query_ec2_metadata import (
    main,
    imds,
    instance_identity,
    instance_identity_document,
    ec2_metadata,
    instance_tags_enabled,
    instance_tag, instance_tags, instance_tags_ec2
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


@mock.patch("query_ec2_metadata.instance_tag")
def test_main_returns_tag(mock_ec2_meta, capsys):
    mock_ec2_meta.return_value = "test-tag"
    testargs = ["instance-tag", "KEY"]

    with mock.patch.object(sys, "argv", testargs):
        main()

    captured = capsys.readouterr()
    assert captured.out == "test-tag"
    mock_ec2_meta.assert_called_with("KEY")


@mock.patch("query_ec2_metadata.instance_tag")
def test_main_returns_empty_when_no_tag(mock_ec2_meta, capsys):
    mock_ec2_meta.side_effect = KeyError('KEY')
    testargs = ["instance-tag", "KEY"]

    with mock.patch.object(sys, "argv", testargs):
        try:
            main()
        except KeyError:
            pass

    captured = capsys.readouterr()
    assert captured.out == ""
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
    assert 'iam/security-credentials/test_creds not available using this tool' in str(e)


@mock.patch("query_ec2_metadata.ec2_metadata")
def test_instance_tags_enabled(mock_ec2_meta):
    mock_ec2_meta.return_value = "instance"

    assert instance_tags_enabled() is True


@mock.patch("query_ec2_metadata.ec2_metadata")
def test_instance_tags_disabled(mock_ec2_meta):
    class NotFoundResponse:
        status_code = 404

    mock_ec2_meta.side_effect = HTTPError(response=NotFoundResponse())
    assert instance_tags_enabled() is False


@mock.patch("query_ec2_metadata.instance_tags_ec2")
@mock.patch("query_ec2_metadata.ec2_metadata")
@mock.patch("query_ec2_metadata.instance_tags_enabled")
def test_instance_tag_metadata(instance_tags_enabled, ec2_metadata, instance_tags_ec2):
    instance_tags_enabled.return_value = True
    ec2_metadata.return_value = 'TestInstance'

    assert instance_tag('Name') == 'TestInstance'
    ec2_metadata.assert_called_once_with('tags/instance/Name')
    instance_tags_ec2.assert_not_called()


@mock.patch("query_ec2_metadata.instance_tags_ec2")
@mock.patch("query_ec2_metadata.ec2_metadata")
@mock.patch("query_ec2_metadata.instance_tags_enabled")
def test_instance_tag_ec2(instance_tags_enabled, ec2_metadata, instance_tags_ec2):
    instance_tags_enabled.return_value = False
    instance_tags_ec2.return_value = {
        'Env': 'Test',
        'Name': 'TestInstance',
        'Type': 'Irrelevant'
    }

    assert instance_tag('Name') == 'TestInstance'

    ec2_metadata.assert_not_called()


@mock.patch("query_ec2_metadata.instance_tags_ec2")
@mock.patch("query_ec2_metadata.instance_tag")
@mock.patch("query_ec2_metadata.ec2_metadata")
@mock.patch("query_ec2_metadata.instance_tags_enabled")
def test_instance_tags_metadata(instance_tags_enabled, ec2_metadata, instance_tag, instance_tags_ec2):
    instance_tags_enabled.return_value = True
    ec2_metadata.return_value = 'Env\nName\nTestName'
    instance_tag.side_effect = ['Test', 'TestInstance', 'test_instance_tags_metadata']

    assert instance_tags() == {
        'Env': 'Test',
        'Name': 'TestInstance',
        'TestName': 'test_instance_tags_metadata'
    }
    ec2_metadata.assert_called_once_with('tags/instance')
    instance_tags_ec2.assert_not_called()
    instance_tag.assert_has_calls([mock.call('Env'), mock.call('Name'), mock.call('TestName')])


@mock.patch("query_ec2_metadata.instance_tags_ec2")
@mock.patch("query_ec2_metadata.instance_tag")
@mock.patch("query_ec2_metadata.ec2_metadata")
@mock.patch("query_ec2_metadata.instance_tags_enabled")
def test_instance_tags_via_ec2(instance_tags_enabled, ec2_metadata, instance_tag, instance_tags_ec2):
    tags = {
        'Env': 'Test',
        'Name': 'TestInstance',
        'TestName': 'test_instance_tags_metadata'
    }

    instance_tags_enabled.return_value = False
    instance_tags_ec2.return_value = tags

    assert instance_tags() == tags

    instance_tags_ec2.assert_called_once()
    ec2_metadata.assert_not_called()
    instance_tag.assert_not_called()


@mock_ec2
@mock.patch("query_ec2_metadata.ec2_metadata")
def test_instance_tags_ec2(ec2_metadata):
    instance_id = 'i-0278698c48372092d'
    tags = {
        'Env': 'Test',
        'Name': 'TestInstance',
        'TestName': 'test_instance_tags_metadata'
    }

    ec2 = boto3.client('ec2', region_name='eu-west-2')
    ec2.create_tags(
        Resources=[instance_id],
        Tags=[{'Key': k, 'Value': v} for k, v in tags.items()]
    )

    ec2_metadata.side_effect = ['eu-west-2', instance_id]

    assert instance_tags_ec2() == tags

    ec2_metadata.assert_has_calls([mock.call('placement/region'), mock.call('instance-id')])

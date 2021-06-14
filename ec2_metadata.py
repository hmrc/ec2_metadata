#!/usr/bin/env python3

import json
import os.path
import sys
from typing import Dict

import requests
from requests.packages.urllib3 import Retry
from requests.adapters import HTTPAdapter


def instance_identity_document() -> Dict[str, str]:
    """
    This returns the identity document for the instance.

    >>> instance_identity_document()
    {
        'region': 'eu-west-2',
        ...
    }
    """
    return json.loads(imds("/dynamic/instance-identity/document"))


def instance_identity(key: str) -> str:
    """
    This returns an attribute from the instance identity document.

    The key can be any of the data values from https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-identity-documents.html

    >>> instance_identity("region")
    "eu-west-2"
    """
    document = instance_identity_document()
    return document[key]


def ec2_metadata(key: str) -> str:
    """
    This returns an attribute from the instance metadata.

    The key can be any of the data values from https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-categories.html

    >>> ec2_metadata("ami-id")
    "ami-00baae30fe5ff5f87"
    """

    if key.startswith("iam/security-credentials"):
        raise Exception(f"{key} not available using this tool")

    return imds(f"/meta-data/{key}")


def imds(path):
    retry_strategy = Retry(total=14, status_forcelist=[429], backoff_factor=0.01)
    adapter = HTTPAdapter(max_retries=retry_strategy)

    http = requests.Session()
    http.mount("http://", adapter)

    token_response = http.put(
        f"http://169.254.169.254/latest/api/token",
        headers={"X-aws-ec2-metadata-token-ttl-seconds": "300"},
        timeout=10,
    )
    if token_response.status_code != 200:
        raise Exception(token_response.content.decode())

    response = http.get(
        f"http://169.254.169.254/latest{path}",
        headers={"X-aws-ec2-metadata-token": token_response.content.decode()},
        timeout=10,
    )
    if response.status_code != 200:
        raise Exception(response.content.decode())

    return response.content.decode()


def main():
    command_name = os.path.basename(sys.argv[0])

    if len(sys.argv) < 2:
        sys.stderr.write(f"Usage: {command_name} KEY\n")
        exit(1)

    if command_name == "instance-identity":
        sys.stdout.write(instance_identity(sys.argv[1]))
    else:
        sys.stdout.write(ec2_metadata(sys.argv[1]))


if __name__ == "__main__":
    main()

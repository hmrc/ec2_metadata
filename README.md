# EC2 Instance Metadata

This allows querying EC2 instance metadata.

It uses IMDSv2. Session credentials are NOT available using this.

## Installation

Available on Pypi as [query-ec2-metadata](https://pypi.org/project/query-ec2-metadata/)

  `pip install query-ec2-metadata`

## Command line tools

### ec2-metadata

Usage:
  `ec2-metadata KEY`

  This returns an attribute from the instance metadata.

  The KEY can be any of the data values from https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html

### instance-identity

Usage:
  `instance-identity KEY`

  This returns an attribute from the instance identity document.

  The key can be any of the data values from https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-identity-documents.html

### instance-tag

Usage:
  `instance-tag KEY`

  This return the instance tag with the specified key.

  This will use the metadata endpoint if tags in metadata is enabled. If it's not enabled, will try and use the EC2 API.


## Python module

### instance_identity_document() -> dict[str, str]:

This returns the identity document for the instance.

### instance_identity(key: str) -> str:

This returns an attribute from the instance identity document.

The key can be any of the data values from https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-identity-documents.html

### ec2_metadata(key: str) -> str:

This returns an attribute from the instance metadata.

The key can be any of the data values from https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html

### instance_tags() -> dict[str, str]:

This returns all the tags on the instance.

### instance_tag(key: str) -> str:

This returns the instance tag value for the specified key.

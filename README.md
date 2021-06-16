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

  The KEY can be any of the data values from https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-categories.html

### instance-identity

Usage:
  `instance-identity KEY`

  This returns an attribute from the instance identity document.

  The key can be any of the data values from https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-identity-documents.html

## Python module

### instance_identity_document() -> Dict[str, str]:
    
This returns the identity document for the instance.

### instance_identity(key: str) -> str:
   
This returns an attribute from the instance identity document.

The key can be any of the data values from https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-identity-documents.html

### ec2_metadata(key: str) -> str:

This returns an attribute from the instance metadata.

The key can be any of the data values from https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-categories.html

### Development

* `make init` to set things up  
* `make pytest` to run unit tests  
* `make test` to run all tests  

Remember to bump the version in `pyproject.toml` before merging.
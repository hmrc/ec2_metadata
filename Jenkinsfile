#!/usr/bin/env groovy
pipeline {
  agent {
    label 'docker'
  }

  stages {
    stage('Build') {
      steps {
        checkout(scm)
        sh("""eval \"\$(pyenv init --path)\"
        python3 -m venv venv
        . venv/bin/activate
        pip install wheel setuptools pip --upgrade
        pip install -r requirements-tests.txt -r requirements.txt -r requirements-dev.txt

        PYTHONPATH=. pytest -v
	    mypy --install-types --non-interactive --ignore-missing-imports query_ec2_metadata.py
        black --check *.py
        bandit query_ec2_metadata.py

        # smoke test
        pip install .
        which ec2-metadata

        METADATA_REGION=\$(ec2-metadata placement/region)
        if [ "\$METADATA_REGION" != "eu-west-2" ]; then
            echo "ec2-metadata returned unexpected region: \$METADATA_REGION"
            exit 1
        fi

        deactivate""")
      }
    }
  }
}

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

        deactivate""")
      }
    }
  }
}

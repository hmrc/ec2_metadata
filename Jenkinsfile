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
	    safety check

        deactivate""")
      }
    }
  }
  post {
    failure {
      snsPublish topicArn: 'arn:aws:sns:eu-west-2:419929493928:jenkins_build_notifications',
                  subject: env.JOB_NAME,
                  message: 'Failed',
                  messageAttributes: [
                      'BUILD_URL': env.BUILD_URL
                  ]
    }
  }
}
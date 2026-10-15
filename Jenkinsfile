
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
    }

    environment {
        CI_VOLUME = 'cloudops_ci_workspace'
        CI_IMAGE = 'cloudops-pro-api'
    }

    stages {
        stage('Checkout Verification') {
            steps {
                sh '''
                    set -eu
                    git --version
                    docker version
                    test -f Dockerfile
                    test -f requirements-prod.txt
                    test -f tests/test_api.py
                '''
            }
        }

        stage('Prepare Isolated Workspace') {
            steps {
                sh '''
                    set -eu

                    # Clear only the dedicated CI volume.
                    docker run --rm \
                      --user 1000:1000 \
                      -v "$CI_VOLUME:/workspace" \
                      alpine:3.20 \
                      sh -c 'find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +'

                    # Copy only required application and test files.
                    tar -cf - \
                      app tests requirements-prod.txt |
                    docker run --rm -i \
                      --user 1000:1000 \
                      -v "$CI_VOLUME:/workspace" \
                      -w /workspace \
                      python:3.12-slim \
                      tar -xf -
                '''
            }
        }

        stage('Automated Tests') {
            steps {
                sh '''
                    set -eu

                    docker run --rm \
                      --user 1000:1000 \
                      -e HOME=/tmp \
                      -e PYTHONDONTWRITEBYTECODE=1 \
                      -v "$CI_VOLUME:/workspace" \
                      -w /workspace \
                      python:3.12-slim \
                      sh -c 'pip install --quiet --target /tmp/ci-packages -r requirements-prod.txt pytest httpx && PYTHONPATH=/tmp/ci-packages:/workspace python -m pytest tests/test_api.py -q'
                '''
            }
        }

        stage('Docker Image Build') {
            steps {
                sh '''
                    set -eu

                    docker build --pull \
                      -t "$CI_IMAGE:ci-$BUILD_NUMBER" .
                '''
            }
        }
    }

    post {
        success {
            echo 'CloudOps Pro CI successful.'
        }
        failure {
            echo 'CloudOps Pro CI failed. Check console logs.'
        }
        always {
            echo 'Pipeline finished.'
        }
    }
}

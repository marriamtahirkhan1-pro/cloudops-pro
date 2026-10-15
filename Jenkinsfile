
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

                    echo "=== CloudOps Pro CI ==="

                    git --version
                    docker version

                    test -f Dockerfile
                    test -f requirements-prod.txt
                    test -f tests/test_api.py

                    echo "Checkout verification passed."
                '''
            }
        }

        stage('Prepare Isolated Workspace') {
            steps {
                sh '''
                    set -eu

                    echo "=== Preparing Isolated CI Workspace ==="

                    # Clean only the dedicated CI volume.
                    docker run --rm \
                      --user 0:0 \
                      -v "$CI_VOLUME:/workspace" \
                      alpine:3.20 \
                      sh -c '
                        set -e
                        find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
                      '

                    # Transfer project files using a temporary
                    # root container.
                    # Tests run separately as non-root.
                    tar -cf - app tests requirements-prod.txt |
                    docker run --rm -i \
                      --user 0:0 \
                      -v "$CI_VOLUME:/workspace" \
                      -w /workspace \
                      python:3.12-slim \
                      sh -c '
                        set -e
                        tar --no-same-owner -xf -
                        chown -R 1000:1000 \
                          /workspace/app \
                          /workspace/tests \
                          /workspace/requirements-prod.txt
                      '

                    echo "CI workspace prepared successfully."
                '''
            }
        }

        stage('Automated Tests') {
            steps {
                sh '''
                    set -eu

                    echo "=== Running Automated API Tests ==="

                    docker run --rm \
                      --user 1000:1000 \
                      -e HOME=/tmp \
                      -e PYTHONDONTWRITEBYTECODE=1 \
                      -v "$CI_VOLUME:/workspace:ro" \
                      -w /workspace \
                      python:3.12-slim \
                      sh -c '
                        set -e

                        pip install --quiet \
                          --target /tmp/ci-packages \
                          -r requirements-prod.txt \
                          pytest httpx

                        PYTHONPATH=/tmp/ci-packages:/workspace \
                          python -m pytest \
                          -p no:cacheprovider \
                          tests/test_api.py -q
                      '

                    echo "Automated tests passed."
                '''
            }
        }

        stage('Docker Image Build') {
            steps {
                sh '''
                    set -eu

                    echo "=== Building Docker Image ==="

                    docker build --pull \
                      -t "$CI_IMAGE:ci-$BUILD_NUMBER" .

                    echo "Docker image built successfully."
                '''
            }
        }

        stage('Trivy Security Scan') {
            steps {
                sh '''
                    set -eu

                    echo "=== Trivy Vulnerability Scan ==="

                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      -v trivy_cache:/root/.cache/ \
                      aquasec/trivy:0.76.0 image \
                      --image-src docker \
                      --scanners vuln \
                      --severity CRITICAL,HIGH \
                      --exit-code 0 \
                      "$CI_IMAGE:ci-$BUILD_NUMBER"

                    echo "Security scan completed (report-only mode)."
                '''
            }
        }
    }

    post {
        success {
            echo 'CloudOps Pro CI completed successfully.'
        }

        failure {
            echo 'CloudOps Pro CI failed. Review console logs.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}

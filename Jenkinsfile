
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
    }

    stages {
        stage('Checkout Verification') {
            steps {
                sh '''
                    echo "=== CloudOps Pro CI ==="
                    git --version
                    docker version
                    test -f Dockerfile
                    test -f requirements-prod.txt
                    test -f tests/test_api.py
                '''
            }
        }

        stage('Automated Tests') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$WORKSPACE:/workspace" \
                      -w /workspace \
                      python:3.12-slim \
                      sh -c 'pip install --quiet -r requirements-prod.txt pytest httpx && python -m pytest tests/test_api.py -q'
                '''
            }
        }

        stage('Docker Image Build') {
            steps {
                sh '''
                    docker build --pull \
                      -t cloudops-pro-api:ci-$BUILD_NUMBER .
                '''
            }
        }
    }

    post {
        success {
            echo 'CloudOps Pro CI completed successfully.'
        }
        failure {
            echo 'CloudOps Pro CI failed. Review stage logs.'
        }
        always {
            echo 'Pipeline execution finished.'
        }
    }
}


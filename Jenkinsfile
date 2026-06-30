pipeline {
    agent any

    stages {

        stage('Clone') {
            steps {
                echo 'Source code already checked out.'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t cicd-demo:latest .
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                docker stop web || true
                docker rm web || true

                docker run -d \
                    --name web \
                    -p 80:80 \
                    cicd-demo:latest
                '''
            }
        }
    }

    post {
        success {
            echo 'Deploy Success'
        }

        failure {
            echo 'Deploy Failed'
        }
    }
}

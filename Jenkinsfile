pipeline {
    agent any

    stages {

        stage('Clone') {
            steps {
                // Jenkins가 자동으로 SCM checkout 하므로 별도 git 명령 필요 없음
                echo 'Source checkout done'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t cicd-demo:latest .
                '''
            }
        }

        stage('Stop Old Container') {
            steps {
                sh '''
                docker stop web || true
                docker rm web || true
                '''
            }
        }

        stage('Run Container') {
            steps {
                sh '''
                docker run -d --name web -p 80:80 cicd-demo:latest
                '''
            }
        }

        stage('Verify') {
            steps {
                sh '''
                docker ps
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD SUCCESS'
        }
        failure {
            echo 'CI/CD FAILED'
        }
    }
}

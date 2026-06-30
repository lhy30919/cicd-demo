pipeline {
    agent any

    triggers {
        pollSCM('H/1 * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t cicd-demo:latest .'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                docker stop web || true
                docker rm web || true
                docker run -d --name web -p 80:80 cicd-demo:latest
                '''
            }
        }
    }
}

pipeline {
    agent any
    stages {
        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/MariamMoumen1/CollegeManagement-Django.git'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t college-django:latest .'
            }
        }
        stage('Deploy MySQL') {
            steps {
                sh 'kubectl apply -f k8s/mysql-deployment.yaml'
                sh 'kubectl apply -f k8s/mysql-service.yaml'
            }
        }
        stage('Deploy Django') {
            steps {
                sh 'kubectl apply -f k8s/web-deployment.yaml'
                sh 'kubectl apply -f k8s/web-service.yaml'
            }
        }
        stage('Run Migrations') {
            steps {
                sh 'kubectl exec deployment/django-web -- python manage.py migrate'
            }
        }
        stage('Verify Deployment') {
            steps {
                sh 'kubectl rollout status deployment/django-web'
                sh 'kubectl get pods'
                sh 'kubectl get services'
            }
        }
    }
}

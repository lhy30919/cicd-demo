# CI/CD Pipeline Project (Jenkins + Docker + GitHub)

## 1. 프로젝트 개요

GitHub에 코드 변경이 발생하면 Jenkins가 이를 감지하고 Docker 이미지를 빌드하여 Nginx 컨테이너로 자동 배포하는 CI/CD 프로젝트이다.

간단한 정적 웹페이지를 대상으로 전체 자동 배포 흐름을 구현하였다.

---

## 2. 사용 기술

| 구분 | 내용 |
|------|------|
| OS | CentOS Stream 9 |
| Web Server | Nginx (Docker Container) |
| Container | Docker |
| CI/CD | Jenkins |
| SCM | Git / GitHub |
| IDE | VS Code |
| Virtualization | VMware |

---

## 3. 시스템 구성

Windows (개발 환경)  
  │  
  │ VS Code에서 index.html 수정  
  │  
  ▼  
GitHub Repository  
  │  
  │ git push  
  ▼  
CentOS Stream 9 (CI/CD Server)  
  │  
  ├── Jenkins (8080)  
  │     │  
  │     │ Poll SCM 기반 변경 감지  
  │     ▼  
  │   Docker Build  
  │     ▼  
  │   Nginx Container (80)  
  │  
  ▼  
Web Browser  

---

## 4. 전체 구성 및 실행 과정

### 1) 시스템 준비

dnf update -y

---

### 2) Git 설치

dnf install -y git

git --version

---

### 3) Docker 설치

dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

dnf install -y docker-ce docker-ce-cli containerd.io

systemctl enable --now docker

---

### 4) 웹 페이지 생성

mkdir ~/cicd-demo  
cd ~/cicd-demo  

index.html 생성

<!DOCTYPE html>
<html>
<head>
    <title>CI/CD Test</title>
</head>
<body>
    &lt;h1&gt;Hello&lt;/h1&gt;
</body>
</html>

---

### 5) Docker 이미지 생성 및 실행

Dockerfile

FROM nginx:latest
COPY index.html /usr/share/nginx/html/index.html

docker build -t cicd-demo:latest .

docker run -d --name web -p 80:80 cicd-demo:latest

---

### 6) GitHub 연동

git init  
git config --global user.name "github username"  
git config --global user.email "github email"  

git add .  
git commit -m "first commit"  

ssh-keygen -t ed25519 -C "github email"  
cat ~/.ssh/id_ed25519.pub  

GitHub → Settings → SSH Keys 등록  

ssh -T git@github.com  

git remote add origin oooo
git branch -M main  
git push -u origin main  

---

### 7) Jenkins 설치 (Docker)

mkdir -p /docker/jenkins_home  
chmod 777 /docker/jenkins_home  

docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v /docker/jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts  

docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword  

---

### 8) Jenkins Pipeline (Jenkinsfile)

pipeline {
    agent any

    triggers {
        pollSCM('H/1 * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                deleteDir()
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

---

## 9. 동작 흐름

코드 수정 → Git push → Jenkins Poll SCM 감지 → Docker build → 컨테이너 재배포 → 웹 반영

---

## 10. 특징

- GitHub 기반 CI/CD 구성
- Poll SCM 방식으로 자동 감지
- Docker 기반 실행 환경 통일
- Jenkins를 통한 빌드/배포 자동화
- 코드 변경 시 즉시 반영되는 구조

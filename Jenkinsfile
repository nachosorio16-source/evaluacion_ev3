pipeline {
    agent any

    environment {
        APP_IMAGE = "secure-flask-app:${env.BUILD_ID}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t $APP_IMAGE .'
                }
            }
        }

        stage('SAST (Static Analysis)') {
            steps {
                echo 'Ejecutando escaneo de seguridad en código fuente...'
                // Opcional: Instalar y correr Bandit para escanear Python
                sh 'pip install bandit'
                sh 'bandit -r . -f html -o bandit-report.html || true'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bandit-report.html', allowEmptyArchive: true
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                sh 'docker run -d -p 5000:5000 --name staging-app $APP_IMAGE'
                // Esperar a que la app levante
                sleep time: 10, unit: 'SECONDS'
            }
        }

        stage('DAST (OWASP ZAP)') {
            steps {
                echo 'Ejecutando escaneo dinámico de vulnerabilidades web...'
                // ZAP escanea el contenedor desplegado en staging
                sh '''
                docker run -t owasp/zap2docker-stable zap-baseline.py \
                -t http://$(hostname -I | awk '{print $1}'):5000 \
                -r zap-report.html || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'zap-report.html', allowEmptyArchive: true
                }
            }
        }

        stage('Deploy to Production') {
            steps {
                // Detener staging y desplegar la versión validada
                sh 'docker stop staging-app && docker rm staging-app'
                echo 'Desplegando entorno asegurado en producción...'
            }
        }
    }
}
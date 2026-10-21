pipeline {
    agent any

    environment {
        NOMBRE_SISTEMA = "MONITOR-PROXMOX"
        TG_TOKEN       = credentials('telegram-token')
        TG_CHAT_ID     = credentials('telegram-chat-id')
    }

    stages {
        stage('Notificar Inicio') {
            steps {
                script {
                    env.GIT_AUTOR   = sh(script: "git log -1 --pretty=format:'%ae'", returnStdout: true).trim()
                    env.GIT_MENSAJE = sh(script: "git log -1 --pretty=format:'%s'", returnStdout: true).trim()
                    env.GIT_COMMIT = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    env.GIT_RAMA    = env.BRANCH_NAME ?: 'origin/pruebas'

                    // Guardamos el mensaje en el entorno de Jenkins para evitar choques de sintaxis
                    env.MENSAJE_INICIO = """----------------------------------------
Rama(Version): origin/${env.GIT_RAMA}
Sistema: ${env.NOMBRE_SISTEMA}
Último mensaje: ${env.GIT_MENSAJE}
Autor: ${env.GIT_AUTOR}
Commit: ${env.GIT_COMMIT}
${env.NOMBRE_SISTEMA} está desplegando..."""

                    // Usamos comillas simples (''') para que Linux maneje las variables de forma segura
                    sh '''
                        curl -4 -s -X POST "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
                            -d chat_id="${TG_CHAT_ID}" \
                            --data-urlencode "text=${MENSAJE_INICIO}" > /dev/null
                    '''
                }
            }
        }

        stage('Despliegue Automático por SSH') {
            steps {
                sshagent(['credencial-ssh-vms']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no -p 19056 root@171.0.20.5 "
                            cd /home/cop/Monitor-proxmox &&
                            git pull origin pruebas &&
                            docker stop monitor-proxmox || true &&
                            docker rm monitor-proxmox || true &&
                            docker build -t monitor-proxmox . &&
                            docker run -d --name monitor-proxmox -p 8000:8000 monitor-proxmox &&
                            docker ps
                        "
                    '''
                }
            }
        }
    }

    post {
        success {
            sh '''
                curl -4 -s -X POST "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
                    -d chat_id="${TG_CHAT_ID}" \
                    --data-urlencode "text=${NOMBRE_SISTEMA} se desplegó exitosamente en el servidor" > /dev/null
            '''
        }
        failure {
            sh '''
                curl -4 -s -X POST "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
                    -d chat_id="${TG_CHAT_ID}" \
                    --data-urlencode "text=${NOMBRE_SISTEMA} ha fallado durante el despliegue" > /dev/null
            '''
        }
    }
}

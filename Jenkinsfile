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
                    env.GIT_COMMIT  = sh(script: "git log -1 --pretty=format:'%h'", returnStdout: true).trim()
                    env.GIT_RAMA    = env.BRANCH_NAME ?: 'origin/main'

                    def mensajeInicio = """----------------------------------------
Rama(Version): origin/${env.GIT_RAMA}
Sistema: ${env.NOMBRE_SISTEMA}
Último mensaje: ${env.GIT_MENSAJE}
Autor: ${env.GIT_AUTOR}
Commit: ${env.GIT_COMMIT}
${env.NOMBRE_SISTEMA} está desplegando..."""

                    sh """
                        curl -4 -s -X POST "https://api.telegram.org/bot\${TG_TOKEN}/sendMessage" \
                            -d chat_id="\${TG_CHAT_ID}" \
                            --data-urlencode "text=${mensajeInicio}" > /dev/null
                    """
                }
            }
        }

        stage('Ejecutar Acciones / Despliegue') {
            steps {
                sh '''
                    echo "Clonado exitoso. Ejecutando acciones del sistema..."
                    python3 --version
                '''
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

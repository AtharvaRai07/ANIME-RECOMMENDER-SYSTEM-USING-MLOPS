pipeline{
    agent any

    enviroment{
        VIRTUAL_ENV = "venv"
    }

    stages{
        stage("Cloning from GitHub..."){
            steps{
                script{
                    echo "Cloning the repository..."
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github token', url: 'https://github.com/AtharvaRai07/ANIME-RECOMMENDER-SYSTEM-USING-MLOPS.git']])
                }
            }
        }
    }

    stage("Making a virtual enviroment and installing dependencies..."){
        steps{
            script{
                echo "Setting up the virtual environment and installing dependencies..."
                sh '''
                    python3 -m venv ${VIRTUAL_ENV}
                    . ${VIRTUAL_ENV}/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }
    }

    stage('DVC Pull'){
        steps{
            withCredentials([file(credentialsId: 'gcp-key-2', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]){
                script{
                    echo "Pulling data from DVC remote storage..."
                    sh '''
                    . ${VIRTUAL_ENV}/bin/activate
                    dvc pull
                    '''
                }
            }
        }
    }
}

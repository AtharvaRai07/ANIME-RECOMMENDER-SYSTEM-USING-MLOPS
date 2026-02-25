pipeline {
    agent any

    environment {
        VIRTUAL_ENV = "venv"
        GCP_PROJECT = "encoded-joy-418604"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
        KUBECTL_AUTH_PLUGIN = "/usr/lib/google-cloud-sdk/bin"
    }

    stages {

        stage("Cloning from GitHub...") {
            steps {
                script {
                    echo "Cloning the repository..."
                    checkout scmGit(
                        branches: [[name: '*/main']],
                        extensions: [],
                        userRemoteConfigs: [[
                            credentialsId: 'github token',
                            url: 'https://github.com/AtharvaRai07/ANIME-RECOMMENDER-SYSTEM-USING-MLOPS.git'
                        ]]
                    )
                }
            }
        }

        stage("Making a virtual environment and installing dependencies...") {
            steps {
                script {
                    echo "Setting up the virtual environment and installing dependencies..."
                    sh '''
                        python3 -m venv ${VIRTUAL_ENV}
                        . ${VIRTUAL_ENV}/bin/activate
                        pip install -r requirements.txt
                    '''
                }
            }
        }

        stage("DVC Pull") {
            steps {
                withCredentials([file(credentialsId: 'gcp-key-2', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo "Pulling data from DVC remote storage..."
                        sh '''
                            . ${VIRTUAL_ENV}/bin/activate
                            dvc pull
                        '''
                    }
                }
            }
        }

        stage("Build and push images to GCR") {
            steps {
                withCredentials([file(credentialsId: 'gcp-key-2', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo "Building and pushing Docker images to GCR..."
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker --quiet
                        docker build -t gcr.io/${GCP_PROJECT}/anime-recommender:latest .
                        docker push gcr.io/${GCP_PROJECT}/anime-recommender:latest
                        '''
                    }
                }
            }
        }

        stage("Deploying to GKE") {
            steps {
                withCredentials([file(credentialsId: 'gcp-key-2', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo "Deploying to GKE..."
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud container clusters get-credentials mlops-2 --region us-central1
                        kubectl apply -f deployment.yaml
                        '''
                    }
                }
            }
        }
    }
}

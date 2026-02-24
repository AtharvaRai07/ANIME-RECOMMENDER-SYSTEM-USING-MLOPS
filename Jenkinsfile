pipeline{
    agent any

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
}

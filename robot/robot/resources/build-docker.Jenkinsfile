node('default-agent') {
    stage('Checkout') {
        checkout([
            $class: 'GitSCM',
            branches: [[name: "master"]],
            doGenerateSubmoduleConfigurations: false,
            extensions: [
                [$class: 'CleanBeforeCheckout']
            ],
            submoduleCfg: [],
            userRemoteConfigs: [[credentialsId: 'creds', url: 'https://stash.com/scm/hie/data-quality-serverless-framework.git']]
        ])
    }

    stage("pushDockerfile") {
        env.PATH = """${tool name: 'dock-push-dockerfile', type: 'com.cloudbees.jenkins.plugins.customtools.CustomTool'}:${env.PATH}"""
        pushDockerfile (
            pushDockerfileCredentialsId: 'creds',
            pushDockerfileOnlyBuild: false,
            pushDockerfileBuildDir: 'robot'
        )
    }
}
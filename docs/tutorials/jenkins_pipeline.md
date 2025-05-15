# Create a new release with Jenkins Pipelines

For this we are using the modern approach of [declarative pipelines](https://www.jenkins.io/doc/book/pipeline/).

You must also ensure your jenkins instance supports docker.
Most modern jenkins systems do have support for it, [they have embraced it](https://www.jenkins.io/doc/book/pipeline/docker/).

```groovy
pipeline {
  agent {
    any
  }
  environment {
    CI = 'true'
  }
  stages {
    stage('Bump version') {
      when {
        beforeAgent true
        expression { env.BRANCH_IS_PRIMARY }
        not {
          changelog '^bump:.+'
        }
      }
      steps {
        script {
          useCz {
            sh "cz bump --changelog"
          }
         // Here push back to your repository the new commit and tag
        }
      }
    }
  }
}

def useCz(String authorName = 'Jenkins CI Server', String authorEmail = 'your-jenkins@email.com', String image =  'registry.hub.docker.com/commitizen/commitizen:latest', Closure body) {
    docker
    .image(image)
    .inside("-u 0 -v $WORKSPACE:/workspace -w /workspace -e GIT_AUTHOR_NAME='${authorName}' -e GIT_AUTHOR_EMAIL='${authorEmail}' -entrypoint='/bin/sh'") {
        sh 'git config --global --add safe.directory "*"'
        sh "git config --global user.email '${authorName}'"
        sh "git config --global user.name '${authorEmail}'"
        body()
    }
}
```

!!! warning
    Using jenkins pipeline with any git plugin may require many configurations,
    you'll have to tinker with it until your pipelines properly detects git events. Check your
    webhook in your git repository and check the "behaviors" and "build strategies" in
    your pipeline settings.

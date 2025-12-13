
sonar-scanner \
    -Dsonar.projectKey=rococo-service-host \
    -Dsonar.sources=. \
    -Dsonar.host.url=http://localhost:9001 \
    -Dsonar.token=sqa_5e58dfaec5d2ec9c43646e27baf3d40be05195f2 \
    -Dsonar.scm.disabled=true \
    -Dsonar.exclusions="**/venv/**,**/.venv/**,**/.git/**"
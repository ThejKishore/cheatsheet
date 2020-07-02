cf enable-feature-flag diego_docker 

cf push APP-NAME --docker-image REPO/IMAGE:TAG

cf push APP-NAME --docker-image mysql:8.0.20

# Breaking Changes and Migrations Guide


## 1.0.0

Changes required in a service to migrate to the rococo service host v 1.0.0:

1. Change directory structure to make the service installable via poetry
2. Add dependency to the `rococo-svchost` package in the service .toml file, explicitely specify the package name in the code using the package functionality. E.g `from rococo_svchost.logger import Logger`  
3. Construct service Docker image based on the `rococo-service-base-onbuild`, move the environment variables to the .env files or to the docker compose configuration as necessary.  
  
See commits 15136e70af572ad4f and 0f1b0f194331a1f as samples of how the above was done in the service examples from the rococo service host repository.  

To ensure a smooth transition, v 1.0.0 of the rococo service host should NOT be merged into the main branch yet. The changes should be maintained in a separate branch until all or most of the services are migrated.  

Publishing of the `rococo-service-base-onbuild` docker image, as well as publishing of the `rococo-svchost` PyPi package, is yet to be automated (currently done manually).  


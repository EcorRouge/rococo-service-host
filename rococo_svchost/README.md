Runnable service host. Run via `poetry run svchost`  
Polls message queue and logs the received message when run standalone.  
Can be added as a dependency in a service .toml file, in which case locates and uses the processor defined in the service when run.  
See README.md in the repository root for more details.
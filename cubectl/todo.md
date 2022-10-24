# todo

## Common

- [ ] start up processes using executor
- [ ] change state of processes using configurator
- [x] decide who will choose ports for services -> Configurator class

- [ ] add init command
- [ ] add start command
- [ ] add start-all command
- [ ] add nginx config creation

---
## ServiceProcess
- [x] created class
- [x] class can start up and stop process
- [x] class can control state of process using config object
- [x] environment var should override other env vars


## Configurator

Changes `status_file`.

- [x] design `status_file`
  - [x] services state
  - [x] jobs to execute
- [ ] on start up creates `status_file` out of init_file
- [ ] create init_application method
- [ ] design port assigning mechanism

## Executor

Starts up processes and controls theirs state using `status_file`.

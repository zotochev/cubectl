# todo

## Common

- [x] Start up processes using executor.
- [x] Change state of processes using configurator.
- [x] Decide who will choose ports for services -> Configurator class.

- [x] Add init command.
- [x] Add start command.
- [x] Add start-all command.
- [x] Add nginx config creation.

---
## ServiceProcess
- [x] Created class.
- [x] Class can start up and stop process.
- [x] Class can control state of process using config object.
- [x] Environment var should override other env vars.


## Configurator

Changes `status_file`

- [x] Design `status_file`.
  - [x] Services state.
  - [x] Jobs to execute.
- [x] On start up creates `status_file` out of init_file.
- [x] Create init_application method.
- [ ] Design port assigning mechanism.
  - [ ] Decide how port stored in to status file should be propagated to process itself:
    - [ ] Via env variable.
    - [ ] Via argument (--port 9006).

## Executor

Starts up processes and controls theirs state using `status_file`.
- [ ] Processes health check.
  - [x] Restart if failed.
  - [ ] Send message to telegram in some cases.
- [x] Saving report for `status` command.

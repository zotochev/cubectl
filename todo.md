# ToDo

## Common

- [x] Start up processes using executor.
- [x] Change state of processes using configurator.
- [x] Decide who will choose ports for services -> Configurator class.

- [x] Add `init` command.
- [x] Add `start` command.
- [x] Add `nginx` config creation.

- [ ] `clean` command
  - [ ] stops all applications
  - [ ] deletes temp files and directories

- [ ] `fclean`
  - [ ] launch `clean` command 
  - [ ] deletes nginx config

---
## ServiceProcess
Class for launching, monitoring and controlling one process.
- [x] Created class.
- [x] Class can start up and stop process.
- [x] Class can control state of process using config object.
- [x] Environment var should override other env vars.


---
## Configurator

Class for configuring applications `register`, creating and changing `status files`

- [x] Design `status_file`.
  - [x] Services state.
  - [x] Jobs to execute.
- [x] On start up creates `status_file` out of init_file.
- [x] Create init_application method.
- [ ] Design port assigning mechanism.
  - [ ] Decide how port stored in to status file should be propagated to process itself:
    - [ ] Via env variable.
    - [ ] Via argument (--port 9006).

---
## Executor
Class that keeps `ServiceProcess` instances, reads `status file` and impacts on processes accordingly to `status file` (starts, stops, retrieves current status).

- [x] Read `status file` and apply status to processes.
- [ ] Processes health check.
  - [x] Restart process if failed.
  - [ ] Stop restarting process after some number of attempts.
    - [ ] create algorithm using max_attempts, current_attempt, count_attempt
  - [x] Send message to telegram in some cases.
- [x] Saving report for `status` command.

# ToDo

## Common

- [x] Start up processes using executor.
- [x] Change state of processes using configurator.
- [x] Decide who will choose ports for services -> Configurator class.

- [x] Add `init` command.
  - [x] check temp_dir existence
- [x] Add `start` command.
- [x] Add `nginx` config creation.

- [x] `clean` command
  - `clean <app_name>`
    - [x] deletes status file
    - [x] delete report file
    - [x] delete log buffer file
    - [x] deletes app from register
  - `clean all`
    - [x] calls `clean` command for all apps
    - [x] deletes `register`

- [x] `get-apps` command
- [x] redo register from dict to list
- [x] fix tests
- [ ] clean up classes:
  - [ ] move out of classes functions that can be static
    - [ ] Executor
    - [x] Configurator
    - [ ] ServiceProcess


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

- [x] Created class.
- [x] Design `status_file`.
  - [x] Services state.
  - [x] Jobs to execute.
- [x] On start up creates `status_file` out of init_file.
- [x] Create init_application method.
- [ ] Design port assigning mechanism.
  - [ ] Decide how port stored in to status file should be propagated to process itself:
    - [ ] Via env variable.
    - [ ] Via argument (--port 9006).
- [x] `get-logs` command
  - [x] return logs from supplied log file
  - [ ] try to read stdout or stderr from popen object

---
## Executor
Class that keeps `ServiceProcess` instances, reads `status file` and impacts on processes accordingly to `status file` (starts, stops, retrieves current status).

- [x] Created class.
- [x] Read `status file` and apply status to processes.
- [ ] Processes health check.
  - [x] save desired state and compare to it
  - [x] Restart process if failed.
  - [x] Stop restarting process after some number of attempts.
    - [x] create algorithm using max_attempts, current_attempt, count_attempt
  - [x] Send message to telegram in some cases.
  - [ ] In case of error send logs (short version if possible) to telegram.
    - [ ] truncate in case too long.
- [x] Saving report for `status` command.
- [x] `restart` wo arguments does not work

# cubectl
Utility for starting and controlling processes in unix environments.

## Requirements
* setuptools
* build (python module)

## Installation of cubectl
```bash
python -m build && pip3 install .
```

## Usage
1. Init your application using `init.yaml` file
    ```bash
    cubectl init init.yaml
    ```

2. Start up watcher
    ```bash
    cubectl watch [installation_name] [-c <number_of_seconds>]&
    ```
   * `-c` option define how often watcher checks processes status

3. Start up processes (services and workers)
    ```bash
    cubectl start [installation_name] [process_name]
    ```

4. Check if all processes are started
    ```bash
    cubectl status [installation_name]
    ```

## Init file
Init file is file that defines installation and describes which processes to start and how to start them.
You can get example of init file by executing following command:
   ```bash
   cubectl get-init-file-example
   ```

# cubectl
Utility for starting and controlling processes in unix environments.

## Requirements
* python 3.9 or higher
* setuptools
* build (pip install build)

## Installation of cubectl
```bash
python -m build && pip3 install .
```
For specific version of python
```bash
python3.9 -m build && python3.9 -m pip install .
```

## Usage
1. Init your application using `init.yaml` file
    ```bash
    cubectl init init.yaml
    ```

2. Start up watcher
    ```bash
    cubectl watch [installation_name] [-c <number_of_seconds>] &
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

## Setting up nginx configuration
You can get nginx config file by executing:
```bash
cubectl get-nginx-config [installation_name]
```

To apply file to nginx directly you can use:
```bash
sudo bash -c "echo \"$(cubectl get-nginx-config)\" > /etc/nginx/sites-available/cubectl.conf"
sudo ln -s /etc/nginx/sites-available/cubectl.conf /etc/nginx/sites-enabled/cubectl.conf
```

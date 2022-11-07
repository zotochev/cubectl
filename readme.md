# cubectl
Utility for starting and controlling processes in unix environments.

## Requirements
* python 3.9 or higher
* pip
* build (pip install build)
* setuptools

## Installation of cubectl
[OPTIONAL] Update and install requirements if you need:
```bash
sudo apt install python3-pip
python -m pip install --upgrade pip
pip install setuptools --upgrade
python -m pip install build
```
[OPTIONAL] After installation of pip check that pip location added to PATH env variable:
```bash
echo ${PATH} | grep "/home/${USER}/.local/bin" > /dev/null && echo "OK: PIP is set up" || echo "ERROR: Default pip location not found in PATH"
```

Build and install package
```bash
python -m build && pip install .
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

# cubectl

## Requirements
* setuptools

## Installation of module
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
    cubectl watch [installation_name]
    ```

3. Start up processes (services and workers)
    ```bash
    cubectl start [installation_name]
    ```

4. Check if all processes are started
    ```bash
    cubectl status [installation_name]
    ```

## Init file


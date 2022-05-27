# Example Script

This script searches to find Prometheus Rules that do not have any unit tests writen against them.

## Setup
Create, active the python virtual environment and install the dependencies.  
```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Add the correct values to the `settings.toml`.

## Running script
The script needs to be run from the same location as the `settings.toml` file.
```shell
python script.py
```

## Finished
Don't forget to deactivate the virtual environment.
```shell
deactive
```
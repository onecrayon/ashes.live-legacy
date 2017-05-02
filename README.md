# Ashes.live Flask app

The site has the following dependencies:

* Python 3 / pip
* virtualenv

## Setup on macOS

1. Install [Homebrew](https://brew.sh/) then Python 3:

        brew install python3

2. Install pip, if necessary:

        sudo easy_install pip

3. Install virtualenv:

        sudo pip install virtualenv

4. Within the project directory, setup virtualenv:

        virtualenv -p python3 venv

5. Install site requirements:

        . venv/bin/activate
        pip install -r requirements.txt

### Configuration

For development servers:

1. Create `/config/development/config.py` and copy all "Environment-specific" variables from `config/config.py` into it
2. Customize config variables for local development environment
3. Execute the following:

        . venv/bin/activate
        ./cli.py runserver -r
4. Load the specified URL in browser

## SCRATCH

Potentially useful extensions (need to research some of them to make sure):

* Flask-User or Flask-Security

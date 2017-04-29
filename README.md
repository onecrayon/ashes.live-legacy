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

## SCRATCH

Potentially useful extensions (need to research some of them to make sure):

* Flask-SQLAlchemy
* Flask-Migrate
* Flask-Script
* Flask-User and/or Flask-Login

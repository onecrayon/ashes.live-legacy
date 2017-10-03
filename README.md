# Ashes.live Flask app

The project has the following dependencies:

* Python 3 / pip
* virtualenv
* Node.js / npm

## Install project dependencies (macOS)

1. Install [Homebrew](https://brew.sh/) then Python 3:

        brew install python3

2. Install pip, if necessary:

        sudo easy_install pip

3. Install virtualenv:

        sudo pip install virtualenv

## Install site dependencies

1. Within the project directory, setup virtualenv:

        virtualenv -p python3 venv

2. Install site requirements:

        . venv/bin/activate
        pip install -r requirements.txt
        npm install

### Configuration

For development servers:

1. Create `/config/development/config.py` and copy all "Environment-specific" variables from `config/config.py` into it
2. Customize config variables for local development environment
3. Execute the following:

        npm run dev
4. Load the specified URL in browser

## Commands

* `npm run dev`: run development server
* `npm run build`: parse Javascript (via webpack) and LESS files
* `npm run lint`: lint Javascript files

## SCRATCH

TODO:

* Figure out why I can't connect to my database on production (???)
* Finish getting production setup and running
    * Ensure ENVIRONMENT="production" is getting set for all production script runs
    * Configure webapp.plist per http://jelockwood.blogspot.com/2013/06/running-django-webapps-with-os-x.html
    * Write the WSGI file logic and serve the app from the site via Server.app
    * Write logic to populate admin account when building server up?

Optional before release:

* Figure out how to handle Salamander Monk Spirit better (currently only disappears on click)
* Implement responsive behaviors for filters (collapse to icons, flow nicely)
* Implement different listing styles, and refactor into components
* Add animated transitions for things like alerts

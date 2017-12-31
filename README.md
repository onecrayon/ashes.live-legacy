# Ashes.live Flask app

The project has the following dependencies:

* Python 3 / pip
* virtualenv
* Node.js / npm

## Install project dependencies

### macOS

1. Install [Homebrew](https://brew.sh/) then Python 3:

        brew install python3

2. Install pip, if necessary:

        sudo easy_install pip

3. Install virtualenv:

        sudo pip install virtualenv

4. Install [NodeJS](https://nodejs.org/) (and npm)

### Linux subsystem on Windows running Ubuntu

1. Install pip (Python 3 is installed by default as `python3`):
    
        sudo apt-get install python3-pip

2. Install virtualenv:
    
        sudo pip3 install virtualenv

3. Install NodeJS:
    
        sudo apt-get update
        curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
        sudo apt-get install nodejs

## Install site dependencies

1. Within the project directory, setup virtualenv:

        virtualenv -p python3 venv

2. Install site requirements:

        . venv/bin/activate
        pip install -r requirements.txt
        npm install

3. Follow configuration instructions below, then initialize the database:

        . venv/bin/activate
        ./cli.py db upgrade

### Configuration

For development servers:

1. Create `/config/development/config.py` and copy all "Environment-specific" variables from `/config/config.py` into it
2. Customize config variables for local development environment
3. Execute the following:

        npm run dev
4. Load the specified URL in browser

For production servers:

1. Create `/config/production/config.py` and copy all "Environment-specific" variables from `/config/config.py` into it
2. Customize config variables for production environment
3. Enable `mod_wsgi` and point it toward `/app.wsgi`
4. Setup rules to serve all immediate children of `/app/static` and all recursive children of `/app/static/css`, `/app/static/fonts`, `/app/static/images`, and `/app/static/js` statically

## Commands

* `npm run dev`: run development server
* `npm run build`: parse Javascript (via webpack) and LESS files
* `npm run build-production`: build production-ready JS and CSS files (may require `export NODE_ENV='production'` first)
* `npm run lint`: lint Javascript files

## SCRATCH

TODO:

* Figure out how to handle Salamander Monk Spirit better (currently only disappears on click)

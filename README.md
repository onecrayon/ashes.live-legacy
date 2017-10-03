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

* Finish getting production setup and running
    * Write logic to populate admin account when building server up?
* Add "no decks" for when the user has no decks
* Modify the sign-up pages to only show items in the list that I know I'm planning to include
* Serve the bulk of the images through Apache instead of Flask, since that Flask seems pretty slow over the network

Optional before release:

* Figure out how to handle Salamander Monk Spirit better (currently only disappears on click)
* Implement responsive behaviors for filters (collapse to icons, flow nicely)
* Implement different listing styles, and refactor into components
* Add animated transitions for things like alerts

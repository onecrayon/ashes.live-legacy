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

* Implement development vs. production environments in a way that works for both Python and webpack
    * Implement a way to serve up different JS and CSS files for production (`.min` versions)
* Create Divine icons, and add to the PHG font
* Implement site-wide "card detail" hover effect
* Implement deck saving
* Implement "my decks" listing page
* Implement responsive behaviors for filters (collapse to icons, flow nicely)

Optional before release:

* Implement "set height" behavior for card details, with expansion button?
* Implement different listing styles, and refactor into components

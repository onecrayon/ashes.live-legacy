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

        sudo easy_install pip3

3. Install virtualenv:

        sudo pip3 install virtualenv

4. Install [NodeJS](https://nodejs.org/) (and npm)

### Linux subsystem for Windows running Ubuntu

1. Install the Linux subsystem for Windows, and then the Ubuntu distribution ([docs](https://docs.microsoft.com/en-us/windows/wsl/install-win10))
2. Launch the newly-installed `bash.exe` to enter the Linux terminal (all commands will be run here)
3. Install pip (Python 3 is installed by default as `python3`):
    
        sudo apt-get install python3-pip

4. Install virtualenv:
    
        sudo pip3 install virtualenv

5. Install NodeJS:
    
        sudo apt-get update
        curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
        sudo apt-get install nodejs

## Install site dependencies

1. Within the project directory, setup virtualenv:

        virtualenv -p python3 venv

2. Install site requirements:

        . venv/bin/activate
        pip3 install -r requirements.txt
        npm install

3. Follow configuration instructions below, then initialize the database:

        . venv/bin/activate
        ./cli.py db upgrade

### Configuration

For development servers:

1. Create `/config/development/config.py` and copy all "Environment-specific" variables from `/config/config.py` into it
2. Customize config variables for local development environment
3. Execute the following:

        npm start

4. Load the specified URL in browser

For production servers:

1. Create `/config/production/config.py` and copy all "Environment-specific" variables from `/config/config.py` into it
2. Customize config variables for production environment
3. Enable `mod_wsgi` and point it toward `/app.wsgi`
4. Setup rules to serve all immediate children of `/app/static` and all recursive children of `/app/static/css`, `/app/static/fonts`, `/app/static/images`, and `/app/static/js` statically

## Editing the site

Ashes.live is written in Python using the [Flask](http://flask.pocoo.org/docs/) framework, with the deck builder and card browser implemented in [VueJS](https://vuejs.org/v2/guide/). Data is available via [SQL Alchemy](http://www.sqlalchemy.org/docs/latest/) with a mySQL database backend, and database schema is controlled via [Alembic](http://alembic.zzzcomputing.com/en/latest/) migrations.

### Source files

* `/_assets`: card data files and related scripts (these are used to generate the data that populates the site, but are not directly accessed by the site logic)
* `/app`: Flask application folder. You will be working with these files if you modify or add any Python logic.
* `/app/static/src`: VueJS app (and global scripts). Any modifications to the deck builder/card browser must be made here, and then compiled with `npm run build` (compiled Javascript lives in `/app/static/js`).
* `/app/static/less`: LESS stylesheet folder. Any modifications to the styles must be compiled with `npm run build` (compiled CSS lives in `/app/static/css`).
* `/migrations`: Alembic migration logic. Card JSON is stored in `/migrations/data` and migration version files are in `/migrations/versions`

### Vuex

The deck builder uses [Vuex](https://vuex.vuejs.org/) for managing state. Basically, none of the source files for the deck builder access data directly. Instead, they all call through `this.$store` to view or commit changes to the global state. The store object is defined in `/app/static/src/app/store.js`. Actual logic for filtering, sorting, and fetching card data is handled by `/app/static/src/app/card_manager.js`. Currently, all card data is fetched as soon as the deck builder is loaded, and stored client-side. Due to the relatively small number of cards in Ashes, this proved more performant on most devices than loading card data asynchronously.

### Editing views

Whenever you create a new Python view or API file, you will need to import it and register the route blueprint in `/manager.py`.

### Editing models

Editing Python models necessitates an Alembic migration to modify the database. Typically, you will do the following:

1. Modify (or create) the Flask model. If creating a new file, make sure to import it in `/cli.py` (otherwise Alembic will not notice it).
2. After entering the virtual environment, run `./cli.py db migrate -m "Short description"`
3. Locate the resulting file in `/migrations/versions`. You will need to strip out a bunch of the extra indices that Alembic is trying to re-create (I have not had a chance to track down why it is doing this), and double check that your defined model properties are included correctly.
4. Run `./cli.py db upgrade` to apply your migration

If you need to inspect the history, `./cli.py db history -r-10:` will give you the 10 latest migrations, and `./cli.py db current` will output the ID of the current migration.

### Coding style

Use 4 spaces for indenting Python, and tabs for indenting everything else. No semicolons in Javascript, please. Otherwise, try to match the existing style used across the site.

## Adding expansions

1. Create card data files in `_assets/card-data/` following naming pattern `ID-expansion.txt` (e.g. `014-king-of-titans.txt`). Card data formatting is documented in `_assets/generate-card-json.js`.
2. Process card data files on command line:
    
        cd _assets/
        ./generate-card-json.js card-data/FOLDER_NAME
3. Verify card dice requirements for any cards with costs in their effects (these tend to parse poorly).
4. Create a new migration and copy the hash
5. Move exported card JSON into `migrations/data/` named like `HASH_expansion_name.json`
6. Copy and paste migration logic from most recent expansion migration, modifying as necessary
7. Add expansion ID and name to `config/config.py`
8. Add expansion ID to `app/static/src/global.js`
9. Add new Phoenixborn to `app/static/css.esdynamo/styles.less` in two locations (search for `mixin-phoenixborn-slice`)
10. Add card images to `app/static/images/cards/`

## Commands

* `npm start` or `npm run start`: run development server
* `npm run venv`: enter virtual environment
* `npm run upgrade`: upgrade Python and Node dependencies to latest specified versions
* `npm run build`: parse Javascript (via webpack) and LESS files
* `npm run build-production`: build production-ready JS and CSS files (may require `export NODE_ENV='production'` first)
* `npm run lint`: lint Javascript files

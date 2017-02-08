# Housenet
A simple webapp for sorting some of the niggles of living together

Housenet creates profile pages for each housemate which provides two main functions:

## IOU Tracker:

* Clearly displays how much people owe you and vice versa
* Apply the changes to everyone's IOU trackers automatically

## Chore Tracker:

* Displays the name of the chore that you're currently assigned
* Generate an .ics to import into any good calendar app

## Transactions Tracker:

* Records and labels each transaction, never have the problem of "I owe you again?"
* Easy to view and filter in tabular format

## Features

* Simple to configure - complete the config file, copy over your profile pictures, and run one command
* Built in database backup command that can easily be ran via a Cron job
* Open source and (hopefully) easy to extend and change


## Installation/ Configuration

* Clone the repository to wherever you want it with ` git clone https://github.com/0Hughman0/Housenet/`
* Create and activate a virtual enviroment here with `virtualenv --no-site-packages env` and `source env/bin/activate`
* Install dependencies with `python -m pip install -r requirements.txt`
* Navigate to `.../config/` and enter your config.
* Copy in profile pictures for your housemates into the `.../config/profile_pics` dir.
* Set the `FLASK_APP` enviroment variable to the path to the `housenet.py` file e.g. on debian `export FLASK_APP=.../run.py`
* Run the command `flask init` to build the database and initialise the config
* Done!

## Running the server

* Activate the virtual env created earlier
* `FLASK_APP` enviroment variable to the path to the `housenet.py` file e.g. on debian `export FLASK_APP=/home/pi/Housenet/housenet/housenet.py` (this can be added to the activate script of your virtual env for convenience)
* Start the server with `flask run --host="0.0.0.0" --with-threads`
* Go to another computer on your network and head to IP.TO.HOST.DEVICE:5000 and housenet should be up and running!

## Advanced usage

* Backups of the database can be placed into the `.../housenet/backups` folder using the command `flask backupdb`
* All configs can be reloaded by running `flask reloadconfig --name=CONFIG_NAME`

## DISCALAIMER

This app is only recommended for use within an internal network, and is not secure if exposed to the big bad internet.





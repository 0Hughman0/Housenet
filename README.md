# Housenet
A simple webapp for sorting some of the niggles of living together

Housenet essentially generates three web pages:

### User profile pages:

Profiles for each housemate containing their current chore, and IOUs.

#### IOU Tracker:

* Clearly displays how much people owe you and vice versa
* Apply the changes to everyone's IOU trackers automatically, giving a reason

#### Chore Tracker:

* Displays the name of the chore that you're currently assigned
* Generate an .ics to import into any good calendar app


### Transactions Tracker:

* Records and labels each transaction, never have the problem of "Why do I owe you again?"
* Easy to view, sort and filter in tabular format

### Home:

* Home for the website
* Can enter any profile
* Can view everyone's chore for the day

## Features

* Simple to configure - complete the config file, copy over your profile pictures, and run one command
* Built in database backup command that can easily be ran via a Cron job
* Open source and (hopefully) easy to extend and change
* Can import existing IOUs or chores from csv files


## Installation/ Configuration

* Clone the repository to wherever you want it with ` git clone https://github.com/0Hughman0/Housenet/`
* Create and activate a virtual environment here with `virtualenv --no-site-packages env` and `source env/bin/activate`
* Install dependencies with `python -m pip install -r Housenet/requirements.txt`
* Navigate to `.../Housenet/config/config.ini` and modify to your needs.
* Copy in profile pictures for your housemates into the `.../Housenet/config/profile_pics` dir, ensuring each profile pic is named `HOUSEMATE_NAME.jpeg`
* Set the `FLASK_APP` environment variable to the path to the `housenet.py` file e.g. on debian `export FLASK_APP=.../Housenet/run.py`
* Run the command `flask init` to build the database and initialise the config
* Done!

## Running the server

* Activate the virtual env created earlier
* set the `FLASK_APP` environment variable to the path to the `housenet.py` file e.g. on debian `export FLASK_APP=.../Housenet/run.py` (this can be added to the activate script of your virtual env for convenience)
* Start the server with `flask run --host="0.0.0.0" --with-threads`
* Go to another computer on your network and head to IP.TO.HOST.DEVICE:5000 and housenet should be up and running!

## Advanced usage

* Backups of the database can be placed into the `.../Housenet/housenet/backups` folder using the command `flask backupdb`
* All configs can be reloaded by running `flask reloadconfig --name=CONFIG_NAME`
* Database is pre-configured for alembic, for more convenient migrations

## Final Stuff

Please submit reports for any bugs encountered, I'll do my best to squish 'em. I'd love for people to add their own custom pages to this basic app, and share!

### DISCLAIMER

This app is only recommended for use within an internal network, and is not secure if exposed to the big bad internet.

This app is not fully tested (see empty tests.py!), but I have personally been using it in my shared house, on a raspberry pi zero for over 4 months and it's been working very well!






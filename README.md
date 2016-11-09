# Housenet
A simple webapp for sorting some of the niggles of living together

Housenet creates profile pages for each housemate which provides two main functions:

# IOU Tracker:

* Clearly displays how much people owe you and vice versa
* Apply the changes to everyone's IOU trackers automatically

# Chore Tracker:

* Displays the name of the chore that you're currently assigned
* Generate an .ics to import into any good calendar app


# Features

* Simple to configure, simply requiring some csv 'config grids' to be filled out which can be done using excel.
* Built in database backup command that can easily be ran via a Cron job
* Open source and (hopefully) easy to extend and change


# Installation

* Ensure Python 3.4+ is installed
* Clone the repository to wherever you want it with ` git clone https://github.com/0Hughman0/Housenet/`
* Install dependencies with `python -m pip install -r requirements.txt`
* Navigate to .../housenet/configs/ and edit the config files as appropriate
* Set the `FLASK_APP` enviroment variable to the path to the `housenet.py` file e.g. on debian `export FLASK_APP=/home/pi/Housenet/housenet/housenet.py`
* Replace the template profile pictures found in `.../housenet/static` in the form `housematename.jpeg`
* Reinitialise the database with the new config using `flask reloaddb`
* Start the server with `flask run --host="0.0.0.0"`
* Go to another computer on your network and head to IP.TO.HOST.DEVICE:5000 and housenet should be up and running!

# Advanced usage

* Backups of the database can be placed into the `.../housenet/backups` folder using the command `flask savedb`
* The current configuration can be exported to the `.../housenet/exports` folder using `flask exportdb`






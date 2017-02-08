class DefaultConfig:
    ### Database config ###
    # Where to find db file?
    SQLALCHEMY_DATABASE_URI = r"sqlite:///housenet/database/database.db"
    # Produces lots of messages/ slows performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DebugConfig(DefaultConfig):
    # Creates DB in memory
    SQLALCHEMY_DATABASE_URI = r"sqlite:///"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TESTING = True

import configparser

class ConfigData:

    def __init__(self, config_auth, config_rules):
        dataAuth = configparser.ConfigParser()
        dataAuth.read_file(config_auth)
        self.token = dataAuth["github"]["token"]
        
        dataRules = configparser.ConfigParser()
        dataRules.read_file(config_rules)

        self.unknownLabel = dataRules['fallback']['name']
        self.userPatterns = {}

        for user in dataRules['patterns']:
            self.userPatterns[user] = dataRules['patterns'][user].splitlines()

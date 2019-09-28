import configparser

class ConfigData:
    
    def __init__(self, config_auth, config_rules):
        dataAuth = configparser.ConfigParser()
        dataAuth.read_file(config_auth)
        self.token = dataAuth["github"]["token"]
        
        dataRules = configparser.ConfigParser()
        dataRules.read_file(config_rules)

        if 'fallback' in dataRules:
            self.unknownLabel = dataRules['fallback']['name']
        else:
            self.unknownLabel = ""

        self.loadRules(dataRules)
        
    # 
    # Loads userPatterns data: 
    #   { 
    #       location: [ 
    #           (pattern, username),
    #           ...
    #       ] 
    #   }
    def loadRules(self, dataRules):
        self.userPatterns = {}

        for user in dataRules['patterns']:
            # self.userPatterns[user] = dataRules['patterns'][user].splitlines()
            lines = dataRules['patterns'][user].splitlines()
            for line in lines:
                split = line.split(sep=":", maxsplit=1)
                if len(split) < 2:
                    continue
                location, pattern = split
                pair = (pattern, user)

                if location not in self.userPatterns.keys():
                    self.userPatterns[location] = [pair]
                else:
                    self.userPatterns[location].append(pair)

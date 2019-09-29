import configparser

class ConfigData:
    
    def __init__(self, config_auth, config_rules):
        self.token = config_auth["github"]["token"]
        
        self.loadRules(config_rules)
        
    # 
    # Loads fallback label name and userPatterns data: 
    #   { 
    #       location: [ 
    #           (pattern, username),
    #           ...
    #       ] 
    #   }
    def loadRules(self, config_rules):
        self.userPatterns = {}

        if 'fallback' in config_rules:
            self.fallbackLabel = config_rules['fallback']['label']
        else:
            self.fallbackLabel = ""

        for user in config_rules['patterns']:
            lines = config_rules['patterns'][user].splitlines()
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

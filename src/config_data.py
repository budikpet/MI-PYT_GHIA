import configparser

class ConfigData:
    
    def __init__(self, config_auth, config_rules):
        github = config_auth["github"]
        self.token = github["token"]
        self.secret = github["secret"]
        
        self.load_rules(config_rules)
        
    # 
    # Loads fallback label name and user_patterns data: 
    #   { 
    #       location: [ 
    #           (pattern, username),
    #           ...
    #       ] 
    #   }
    def load_rules(self, config_rules):
        self.user_patterns = {}

        if 'fallback' in config_rules:
            self.fallback_label = config_rules['fallback']['label']
        else:
            self.fallback_label = ""

        for user in config_rules['patterns']:
            lines = config_rules['patterns'][user].splitlines()
            for line in lines:
                split = line.split(sep=":", maxsplit=1)
                if len(split) < 2:
                    continue
                location, pattern = split
                pair = (pattern, user)

                if location not in self.user_patterns.keys():
                    self.user_patterns[location] = [pair]
                else:
                    self.user_patterns[location].append(pair)

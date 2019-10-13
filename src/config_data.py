from configparser import ConfigParser

class ConfigData:
    
    def __init__(self, config_auth, config_rules):
        github = config_auth["github"]
        self.token = github["token"]
        
        if github.get("secret") is not None:
            self.secret = github["secret"]
        else:
            self.secret = ""
        
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
        self.user_patterns = dict()
        self.user_patterns_by_user = dict()

        if 'fallback' in config_rules:
            self.fallback_label = config_rules['fallback']['label']
        else:
            self.fallback_label = ""

        users = config_rules["patterns"]
        for user in users:
            lines = users[user].splitlines()
            self.user_patterns_by_user[user] = list()
            for line in lines:
                split = line.split(sep=":", maxsplit=1)
                if len(split) < 2:
                    continue
                location, pattern = split
                self.user_patterns_by_user[user].append((location, pattern))
                pair = (pattern, user)

                if location not in self.user_patterns.keys():
                    self.user_patterns[location] = [pair]
                else:
                    self.user_patterns[location].append(pair)
        print

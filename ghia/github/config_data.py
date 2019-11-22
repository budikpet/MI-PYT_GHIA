from configparser import ConfigParser

class ConfigData:
    """ 
    Loads and parses all configuration files. 

    Args:
        token (str): GITHUB_TOKEN
        secret (str): GITHUB_SECRET
        trigger_actions (List[str]): All issue webhook actions that should trigger the GHIA CLI.
        fallback_label (str): Fallback label title
        user_patterns (Dict): Parsed rules where location is the key
        user_patterns_by_user (Dict): Parsed rules where username is the key
    
    """
    
    def __init__(self, config_auth: ConfigParser, config_rules: ConfigParser = None):
        github = config_auth["github"]
        self.token = github["token"]
    
        # Value or None
        self.secret = github.get("secret")
        
        if config_rules is not None:
            self.load_rules(config_rules)

            if "other" in config_rules:
                self.trigger_actions = config_rules["other"].get("trigger_actions").replace(" ", "").split(",")

    def load_rules(self, config_rules: ConfigParser):
        """ Loads fallback label name and user_patterns dictionary data. """
        
        self.user_patterns = dict()
        self.user_patterns_by_user = dict()

        if 'fallback' in config_rules:
            self.fallback_label = config_rules['fallback']['label']
        else:
            self.fallback_label = None

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

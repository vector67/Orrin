global_settings = {}
with open('.env', 'r') as f:
    for line in f:
        line = line.split("=")
        if not len(line) == 2:
            raise SyntaxError("Wrong format for .env")
        global_settings[line[0]] = line[1].strip()
def settings(setting):
    global global_settings
    if setting in global_settings:
        return global_settings[setting]
    return None

from custom_error import IncorrectConfigurations

def load_level(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.readlines()
        pointer =  ""
        level = {}
        for i in content:
            if i != '\n':
                i = i.rstrip()
                if i[:2] == "==" and i[-2:] == "==":
                    pointer = i
                    level[pointer] = {}
                else:
                    info = {}
                    config = i.split(" : ")
                    if len(config) < 2:
                        raise IncorrectConfigurations("Value seperated wrongly")
                    # info[config[0]] = config[1]
                    level[pointer][config[0]] = config[1]
        if level.get("==World==", None) == None or \
                level.get("==Player==", None) == None:
            raise IncorrectConfigurations("World or Player missing")

        check = level["==World=="]
        if check.get("gravity", None) == None or \
                check.get("start", None) == None:
            raise IncorrectConfigurations("World configured wrongly")

        check = level["==Player=="]
        if check.get("character") == None or \
                check.get("x") == None or \
                check.get("y") == None or \
                check.get("mass") == None or \
                check.get("health") == None or \
                check.get("max_velocity") == None:
            raise IncorrectConfigurations("Player configured wrongly")

        for key, value in level.items():
            if key not in ["==World==", "==Player=="]:
                if level[key].get("goal", None) == None:
                    raise IncorrectConfigurations("One of the levels configured wrongly")
        return level
    except FileNotFoundError:
        print("Not such file exists")
        return None
    except IncorrectConfigurations as e:
        print(e)
        return None

if __name__ == "__main__":
    load_level("config.txt")
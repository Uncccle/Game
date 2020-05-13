
try:
    filename = "config.txt"
    with open(filename, "r") as f:
        lines = f.readlines()
    
    config = {}
    current_header = None
    for i in lines:
        if i != '\n':
            i = i.rstrip()
            if i[:2] == "==" and i[-2:] == "==":
                config[i] = {}
                current_header = i
            else:
                i = i.split(" : ")
                if len(i) == 2:
                    config[current_header][i[0]] = i[1] 
    if config.get("==World==", None) == None:
        print("there is no world, error!!!")
except FileNotFoundError:
    print("File does not exist"
)

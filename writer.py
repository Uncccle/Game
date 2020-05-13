

try:
    with open("test.txt", "a") as f:
        f.write("Jason : 10\n")
except Exception as e:
    print(e)

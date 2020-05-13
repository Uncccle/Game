from custom_error import IncorrectConfigurations

class HighScores(object):
    def __init__(self):
        self._entries = []

    def add_score(self, name, score):
        self._entries.append((name, score))

    def get_all(self):
        return self._entries

    def get_top_10(self):
        self._entries.sort(key = lambda x : x[1])
        return self._entries[-10:][::-1]

    def save_scores(self, filename):
        try:
            with open(filename, 'w') as f:
                for i in self.get_all():
                    f.write(str(i[0]) + " : " + str(i[1]) + '\n')
        except:
            print("Error writing file")

    def load_scores(self, filename):
        try:
            with open(filename, 'r') as f:
                content = f.readlines()
            scores = []
            for i in content:
                if i != '\n':
                    i = i.rstrip()
                    config = i.split(" : ")
                    if len(config) < 2:
                        raise IncorrectConfigurations("Value seperated wrongly")
                    scores.append((config[0],int(config[1])))
            self._entries = scores

        except FileNotFoundError:
            print("Not such file exists")
            return None
        except IncorrectConfigurations as e:
            print(e)
            return None
        except Exception:
            print("something went wrong")
            return None
        return 1


if __name__ == "__main__":
    s = HighScores()
    s.add_score("Jason", 50)
    s.add_score("Jack", 40)
    s.add_score("Emma", 60)
    print(s.get_all())
    print(s.get_top_10())
    s.save_scores("level1")
    s.load_scores("level1")
    print(s.get_top_10())



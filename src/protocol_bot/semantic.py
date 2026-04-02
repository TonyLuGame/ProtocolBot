import difflib

class similarityFunction:
    def __init__(self):
        self.name_list = []

    def generateNameList(self, recipe, dictionary):
        # Create the name list that contains all pre-made stock solutions and bulk solution in well plate
        original_name_list = []
        for stock in dictionary:
            original_name_list.append(stock)
        for item in recipe:
            original_name_list.append(item.SProtocol.Name)
        self.name_list = [n for n in original_name_list if isinstance(n, str)]

    def similarityCheck(self, name):
        # Find the best-match word given the name in recipe or stock solution list
        matches = difflib.get_close_matches(name, self.name_list, n=1, cutoff=0.0)
        return matches[0]
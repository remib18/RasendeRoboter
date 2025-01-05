import random

class Map:
    def __init__(self):
        self.map_import = self.load_maps("maps.txt")
        self.map_input = self.generate_gameboard(self.map_import)

    # Function to rotate a map by 90 degrees clockwise
    def rotate_map_90_right(self, map_data):
        transposed_map = [list(row) for row in zip(*map_data)]
        rotated_map = [row[::-1] for row in transposed_map]
        return rotated_map

    def rotate_map_180_right(self, map_data):
        return self.rotate_map_90_right(self.rotate_map_90_right(map_data))

    def rotate_map_270_right(self, map_data):
        return self.rotate_map_90_right(self.rotate_map_180_right(map_data))

    # Function to load maps from the file
    def load_maps(self, file_name):
        try:
            with open(file_name, 'r') as f:
                maps = {}
                current_map = None
                current_map_data = []
                
                for line in f:
                    line = line.strip()
                    if line.startswith('<'):
                        if current_map:
                            maps[current_map] = current_map_data
                        current_map = line.strip('<>')
                        current_map_data = []
                    elif line:
                        current_map_data.append([int(x) if x.isdigit() else x for x in line.split()])
                
                if current_map:
                    maps[current_map] = current_map_data
                    
            return maps
        except FileNotFoundError:
            print(f"Error: File '{file_name}' not found.")
            return {}

    # Function to create the 16x16 gameboard by combining rotated maps
    def generate_gameboard(self, maps):
        if not maps:
            print("No maps loaded. Cannot generate gameboard.")
            return []

        chosen_order = list(range(4))
        random.shuffle(chosen_order)
        map_index = [0] * 4
        for i in range(4):
            map_index[i] = chosen_order[i] * 2 + random.choice([1, 2])

        chosen_map_data = []
        for i in map_index:
            map_key = f"map{i}"
            if map_key in maps:
                chosen_map_data.append(maps[map_key])
            else:
                print(f"Invalid map key: {map_key}")
                return []

        map1, map2, map3, map4 = chosen_map_data
        map2 = self.rotate_map_90_right(map2)
        map3 = self.rotate_map_180_right(map3)
        map4 = self.rotate_map_270_right(map4)

        gameboard = [[9 for _ in range(34)] for _ in range(34)]
        for i in range(17):
            for j in range(17):
                gameboard[i][j] = map1[i][j]
        for i in range(17):
            for j in range(17, 34):
                gameboard[i][j] = map2[i][j-17]
        for i in range(17, 34):
            for j in range(17, 34):
                gameboard[i][j] = map3[i-17][j-17]
        for i in range(17, 34):
            for j in range(17):
                gameboard[i][j] = map4[i-17][j]

        for row in range(17):
            if gameboard[row][16] == 1 and gameboard[row][17] == 1:
                gameboard[row][16] = 1
            elif gameboard[row][16] == 2 or gameboard[row][17] == 2:
                gameboard[row][16] = 2

        for row in range(34):
            del gameboard[row][17]

        for col in range(17):
            if gameboard[16][col] == 1 and gameboard[17][col] == 1:
                gameboard[16][col] = 1
            elif gameboard[16][col] == 2 or gameboard[17][col] == 2:
                gameboard[16][col] = 2

        del gameboard[17]

        # gameboard = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 'BC', 1, 0, 1, 0, 1, 'YS', 2, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 'GC', 2, 0, 1, 0, 1, 0, 1, 0, 1], [1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 'YT', 2, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 'GS', 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 0, 1, 'RH', 2, 0, 1, 0, 1, 0, 1, 0, 1, 'Rain', 2, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 'BH', 1, 0, 1, 0, 1], [1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], [1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 2, 2, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 'X', 1, 'X', 2, 0, 2, 'RT', 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 'X', 1, 'X', 2, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1], [1, 0, 1, 0, 1, 0, 1, 0, 2, 'YC', 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 'BS', 2, 0, 1, 0, 1, 0, 1], [1, 1, 1, 2, 2, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1], [1, 0, 1, 'GH', 2, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], [1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 'YH', 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 'BT', 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 'GT', 1, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1], [1, 0, 1, 0, 1, 'RS', 2, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 'RC', 2, 0, 1, 0, 1, 0, 1, 0, 1], [1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

        # print(gameboard)
        return gameboard

'''
if __name__ == "__main__":
    maps = Map()

    if maps.map_input:
        for row in maps.map_input:
            print(" ".join(map(str, row)))
'''
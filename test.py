relation_matrix = [[0, 1, 1, 1, 1, 1, 0, 0],
                   [1, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 1, 0, 0],
                   [0, 0, 0, 0, 0, 0, 1, 0],
                   [1, 0, 0, 0, 0, 1, 1, 0],
                   [0, 1, 0, 0, 0, 0, 0, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 1, 0, 0, 0, 0, 0]]

tact = int(input("Введите такт: "))

variables = {
    "v1": {0: []},
    "v2": {},
    "v3": {},
    "v4": {},
    "v5": {},
    "v6": {},
    "v7": {},
    "v8": {}
}

for i in range(1, tact+1):
    for v in range(len(relation_matrix)):
        if i-1 in variables[f"v{v+1}"].keys():
            for w in range(len(relation_matrix)):
                if relation_matrix[v][w] == 1:
                    print(i, v, w)
                    variables[f"v{w+1}"][i] = variables[f"v{v+1}"][i-1].copy()
                    variables[f"v{w+1}"][i].append(f"v{v+1}[{i-1}]")

print(variables)



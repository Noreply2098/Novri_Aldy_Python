matrix = [
    [0, 1, 1, 0],
    [1, 1, 1, 1],
    [1, 0, 0, 1],
    [0, 0, 1, 1],
]

for row in matrix:
    for cell in row:
        print(cell, end=" ")
    print()
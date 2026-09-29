mtx = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
]

trans = []
for i in range(4):
    tr = []
    for row in mtx:
        tr.append(row[i])
    trans.append(tr)

print(trans)
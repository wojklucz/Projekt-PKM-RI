import numpy as np

class Strefa():
    def __init__(self, nr, przejscia, zajetosci):
        self.przejscia = przejscia
        self.nr = nr
        self.zajetosci = zajetosci

strefy = []
strefy.append(Strefa(1,[],[]))
strefy.append(Strefa(2,[[3, [27, False], [25, False]]],[]))
strefy.append(Strefa(3,[[4, [1, False]]],[]))
strefy.append(Strefa(4,[[5, [1, True]]],[]))
strefy.append(Strefa(5,[[1, [28, False], [27, True]]],[]))
strefy.append(Strefa(6,[],[]))
strefy.append(Strefa(7,[[8, [5, True], [4, False]]],[8,20]))
strefy.append(Strefa(8,[[9,[4, False],[5, True]],[10,[4, True]]],[[9,12]]))
strefy.append(Strefa(9,[],[12]))
strefy.append(Strefa(10,[[11,[313, True]]],[8]))
strefy.append(Strefa(11,[],[]))
strefy.append(Strefa(12,[],[]))
strefy.append(Strefa(13,[],[]))
strefy.append(Strefa(14,[],[[15,16]]))
strefy.append(Strefa(15,[[16,[7,False], [9, False]]],[16]))
strefy.append(Strefa(16,[[16,[9,True], [8,True]]],[]))
strefy.append(Strefa(17,[],[]))
strefy.append(Strefa(18,[],[[29,19]]))
strefy.append(Strefa(19,[],[]))
strefy.append(Strefa(20,[],[8]))
strefy.append(Strefa(21,[[26,[12,True]]],[26,24]))
strefy.append(Strefa(22,[],[21]))
strefy.append(Strefa(23,[],[30,24]))
strefy.append(Strefa(24,[[26,[21,True]]],[26,21]))
strefy.append(Strefa(25,[[30,[20,True]]],[30,23]))
strefy.append(Strefa(26,[[20,[12, False],[15,False],[14,False],[13,True]],[25,[13,False]],[27,[13,True],[14,False],[15,True],[17,True],[16,False]]],[]))
strefy.append(Strefa(27,[[28,[22,True],[23,True],[24,True],[29,True]]],[]))
strefy.append(Strefa(28,[[7,[29,True],[24,False],[18,False]]],[]))
strefy.append(Strefa(29,[],[19]))
strefy.append(Strefa(30,[[23,[33,False]],[24,[33,True],[32,False]]],[]))

# for strefa in strefy:
#     for przejscie in strefa.przejscia:
#         print strefa.nr, przejscie

mozliwe_przejscia = {}

for strefa in strefy:
    mozliwe_przejscia[strefa.nr] = []
    if strefa.przejscia:
        for przejscie in strefa.przejscia:
            mozliwe_przejscia[strefa.nr].append(przejscie[0])


przejscia = np.zeros((30,30))
for key in mozliwe_przejscia:
    if mozliwe_przejscia[key]:
        for przejscie in mozliwe_przejscia[key]:
            przejscia[key-1][przejscie-1] = 1


G = np.logical_or(np.transpose(przejscia),przejscia)

#implementacja Breadth First Search
def bfs(s,c):
    s = s - 1
    c = c - 1
    colors = {}
    distance = {}
    parent = {}
    Q = []
    for u in range(len(G)):
        colors[u] = "WHITE"
        distance[u] = float('inf')
        parent[u] = None
    colors[s] = "GREY"
    distance[s] = 0
    parent[s] = None
    Q.append(s)
    while Q:
        u = Q.pop()
        for V in np.where(G[u]):
            for v in V:
                if colors[v] == "WHITE":
                    colors[v] = "GREY"
                    distance[v] = distance[u] + 1
                    parent[v] = u
                    Q.append(v)
        colors[u] = "BLACK"

    for k in colors:
        if colors[k] == "BLACK":
            print k+1, colors[k]
    # for k in distance:
    #     print k+1, distance[k]
    # for k in parent:
    #     print k+1, parent[k]
    if colors[c] == "BLACK":
        temp = []
        while parent[c]:
            temp.append(c+1) #numeracja wezlow od 1
            c = parent[c]
        return temp[::-1]
    else:
        raise Exception("Graf niespojny, przejscia nie ma")
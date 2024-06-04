import copy
import itertools
import networkx as nx
from database.DAO import DAO


class Model:
    def __init__(self):
        self._betObjVal = None
        self._bestPath = None
        self._allTeams = []
        self._grafo = nx.Graph()
        self._idMapTeams = {}

    def buildGraph(self, year):
        self._grafo.clear()
        if len(self._allTeams) == 0:
            print("ERRORE, seleziona bene le squadre!")
            return
        else:
            self._grafo.add_nodes_from(self._allTeams)

            # Aggiungere nodi 1
            """
            for t1 in self._grafo.nodes:
                for t2 in self._grafo.nodes:
                    if t1 != t2:
                        self._grafo.add_edge(t1, t2) """

            # Aggiungere nodi 2
            myedges = list(itertools.combinations(self._allTeams, 2))  # Libreria che combina 2 a 2 tutti i nodi,
            # restituisce lista di tuple!
            self._grafo.add_edges_from(myedges)
            salariesOfTeams = DAO.getSalaryOfTeams(year, self._idMapTeams)
            for e in self._grafo.edges:
                self._grafo[e[0]][e[1]]["weight"] = salariesOfTeams[e[0]] + salariesOfTeams[e[1]]

    def getPercorso(self, v0):
        self._bestPath = []
        self._betObjVal = 0
        parziale = [v0]
        self._ricorsione(parziale)
        return self._bestPath

    def _ricorsione(self, parziale):

        # Verifico se soluzione è migliore del best
        if self._getScore(parziale) > self._betObjVal:
            self._bestPath = copy.deepcopy(parziale)
            self._betObjVal = self._getScore(parziale)

        # Verifico se posso aggiungere elemento e in caso aggiungo e faccio ricorsione
        listaVicini = []
        for v in self._grafo.neighbors(parziale[-1]):
            edgeV = self._grafo[parziale[-1]][v]["weight"]
            listaVicini.append((v, edgeV))
            listaVicini.sort(key=lambda x: x[1], reverse=True)
        for v1 in listaVicini:
            if v1[0] not in parziale and self._grafo[parziale[-2]][parziale[-1]]["weight"] > v1[1]:
                parziale.append(v1)
                self._ricorsione(parziale)
                parziale.pop()
                return

    def _getScore(self, listOfNodes):
        if len(listOfNodes) == 1:
            return 0
        score = 0
        for i in range(0, len(listOfNodes)-1):
            score += self._grafo[listOfNodes[i]][listOfNodes[i+1]]["weight"]
        return score

    def getSortedNeighbors(self, v0):
        vicini = self._grafo.neighbors(v0)
        viciniTuple = []
        for v in vicini:
            viciniTuple.append((v, self._grafo[v0][v]["weight"]))
        viciniTuple.sort(key=lambda x: x[1], reverse=True)
        return viciniTuple

    @staticmethod
    def getYears():
        return DAO.getAllYears()

    def getTeamsOfYear(self, year):
        self._allTeams = DAO.getTeamsOfYear(year)
        self._idMapTeams = {t.ID: t for t in self._allTeams}
        return self._allTeams

    def printGraphDetails(self):
        print(f"grafo crato con {len(self._grafo.nodes)} nodi e {len(self._grafo.edges)} archi")

    def getGraphDetails(self):
        return len(self._grafo.nodes), len(self._grafo.edges)

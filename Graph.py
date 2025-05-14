"""Graph class to handle roatrip routing using a weighted graph"""

from heapq import heappush, heappop
from typing import Any

type Vertex = Any


class Graph:
    """
    A class that uses an adjacency list to keep track of edges
    """

    def __init__(self):
        # Dictionary to store adjacency list with weights
        self.adj_list: dict["Vertex", list[list["Vertex",float]]] = {}  # nodes = landmarks
        self.edges:list[tuple[float, "Vertex", "Vertex"]] = []  # edges = roads in between the landmarks

    def __str__(self) -> str:
        result = ""
        for vertex in self.adj_list:
            result += f"Vertex ({vertex}): {self.adj_list[vertex]}\n"
        return result

    def __getattribute__(self, vertex: Vertex) -> list[list]:
        return self.adj_list[vertex]
    
    def __iter__(self) -> Vertex:
        for v in self.adj_list:
            yield v

    def addVertex(self, vertex):
        """
        Adds a vertex to graph
        """
        # Add a vertex if it does not already exist
        if vertex not in self.adj_list:
            self.adj_list[vertex] = []

    # Ensure that your graph can handle String identifiers for vertices.

    def addEdge(self, vertex1, vertex2, weight=1.0):
        """
        Adds edge
        """
        # Add weighted edge between V1 and V2 for (Undirected Graph); Directed graph need 1 edge
        if vertex1 in self.adj_list and vertex2 in self.adj_list:
            self.adj_list[vertex1].append([vertex2, weight])
            self.adj_list[vertex2].append([vertex1, weight])
            self.edges.append((weight, vertex1, vertex2))
        else:
            raise ValueError("Both vertices must exist in the graph.")
        
    def removeEdge(self, vertex1, vertex2):
        """ Remove the first edge found that contains the two vertices. """
        raise NotImplementedError("TODO")
        if vertex1 in self.adj_list and vertex2 in self.adj_list:
            edge = None
            self.adj_list.popitem((vertex1, [edge]))

    def display(self):
        # Display adjacency list
        for vertex, edges in self.adj_list.items():
            print(f"{vertex}: {edges}")

    def bfs(self, startVert):
        """
        This method for BFS prints out the order of landmarks visited
        """
        visited = set()
        # our queue for vertices to visit
        notVisited: list = [startVert]

        while len(notVisited) > 0:
            vert = notVisited.pop()
            visited.add(vert)
            print(vert)
            for adjVert, _ in self.adj_list[vert]:
                if adjVert not in visited:
                    notVisited.insert(0, adjVert)
                    visited.add(adjVert)

    def dfs(self, startVert):
        """
        This method for DFS is using a stack to print out the order of landmarks visited
        """
        visited = set()
        # our stack for vertices to visit
        notVisited: list = [startVert]

        while len(notVisited) > 0:
            vert = notVisited.pop()
            visited.add(vert)
            print(vert)
            for adjVert, _ in self.adj_list[vert]:
                if adjVert not in visited:
                    notVisited.append(adjVert)
                    visited.add(adjVert)

    def dijkstra(self, startVert) -> dict:
        """
        Dijkstra used to find the shortest distance to vertices from the start vertex.
        """
        # TODO make sure there are valid edges to traverse through
        if startVert not in self.adj_list:
            raise ValueError("Both vertices must exist in the graph.")

        # track w/ heap the next closest to visit
        pq = []
        heappush(pq, (0, startVert))
        dists = {vertex: float("inf") for vertex in self.adj_list}
        # ordered keys for which vertex to pass through
        dists[startVert] = 0
        visited = set()
        while pq:
            currentDistance, vertex = heappop(pq)

            if vertex in visited:
                continue
            visited.add(vertex)

            for adjacentVertex, dist in self.adj_list[vertex]:
                if adjacentVertex not in visited:
                    # neighbor distance through current vertex
                    newDistance = currentDistance + dist
                    if newDistance < dists[adjacentVertex]:
                        # if smaller distance than previous, add it to path
                        dists[adjacentVertex] = newDistance
                        heappush(pq, (newDistance, adjacentVertex))

        return dists

    def route(self, startVert, endVert) -> list:
        """
        This method uses Dijkstra's algoroithm to find the shortest path between two vertices.
        """
        # Implement a function that uses BFS to find the shortest path (in terms of the number of edges) from one landmark to another if one exists.
        if endVert not in self.adj_list:
            raise ValueError("Both vertices must exist in the graph.")
        dists = self.dijkstra(startVert)
        shortestDistance = dists[endVert]
        predecessors = {vertex: None for vertex in self.adj_list}

        for vertex, distance in dists.items():
            for adjacentVertex, dist in self.adj_list[vertex]:
                # check if the shortest distance to the neighbor from start is equal to shortest distance to current vertex + distance from current vertex to neighbor
                if dists[adjacentVertex] == distance + dist:
                    # if shortest distance to neighbor is sum, then this vertex is the predecessor to the neighbor
                    predecessors[adjacentVertex] = vertex
                    # should be no predecessor to start

        # backtrace steps from end
        path = []
        currentVertex = endVert
        while currentVertex:
            path.insert(0, currentVertex)
            currentVertex = predecessors[currentVertex]

        return path
    
    def kruskal(self) -> "Graph":
        """
        Kruskal's algorithm to find the minimum spanning tree of the graph.
        """
        # Sort edges by weight
        self.edges.sort(key= lambda e: e[0])
        mst = Graph()
        # disjoint set of vertices to detect cycles. contains connections between vertices if they exist
        disjointSet = []
        for vert in self.adj_list:
            mst.addVertex(vert)
            disjointSet.append({vert})

        for weight, vertex1, vertex2 in self.edges:
            # if any set contains the vertex in disjointSet store in these
            vert1Set = set()
            vert2Set = set()
            for mySet in disjointSet:
                if vertex1 in mySet:
                    vert1Set = mySet
                if vertex2 in mySet:
                    vert2Set = mySet
            
            # if there is not already an edge between these two
            if vert1Set is not vert2Set:
                mst.addEdge(vertex1, vertex2, weight)
                tempSet = vert1Set.union(vert2Set)
                disjointSet.remove(vert1Set)
                disjointSet.remove(vert2Set)
                disjointSet.append(tempSet)

        return mst
    

if __name__ == "__main__":
    # Sample graph with 5 vertices all interconnected.
    pinGraph = Graph()
    # vertices (5)
    pinGraph.addVertex("Grand Library of All Books")
    pinGraph.addVertex("Harvard University")
    pinGraph.addVertex("Charles River")
    pinGraph.addVertex("Harvard Square")
    pinGraph.addVertex("Harvard Museum of Natural History & Arts")
    # edges
    pinGraph.addEdge("Grand Library of All Books", "Harvard University",1)
    pinGraph.addEdge("Grand Library of All Books", "Charles River",2)
    pinGraph.addEdge("Grand Library of All Books", "Harvard Square",3)
    pinGraph.addEdge(
        "Grand Library of All Books", "Harvard Museum of Natural History & Arts",2
    )

    pinGraph.addEdge("Harvard University", "Charles River",2)
    pinGraph.addEdge("Harvard University", "Harvard Square",3)
    pinGraph.addEdge(
        "Harvard University", "Harvard Museum of Natural History & Arts",2
    )

    pinGraph.addEdge("Charles River", "Harvard Square",3)
    pinGraph.addEdge("Charles River", "Harvard Museum of Natural History & Arts",1)
    
    pinGraph.addEdge("Harvard Square", "Harvard Museum of Natural History & Arts",4)

    print(pinGraph.kruskal())

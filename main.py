from tkinter import Event
from PIL import Image, ImageTk
import customtkinter as ctk
from pywinstyles import set_opacity

from Graph import Graph
import random
from math import sqrt
from itertools import permutations

from typing import Sequence
from time import time


type Vertex = int


class DisplayGraph(Graph):
    def __init__(self, canvas: "PinCanvas"):
        super().__init__()
        self.canvas: PinCanvas = canvas
        self.mst: Graph | None = None

    def getMST(self) -> Graph:
        if not self.mst:
            return self.setMST()
        return self.mst

    def setMST(self, mst: Graph | None = None) -> Graph:
        if not mst:
            self.mst = self.kruskal()
            return self.mst
        elif type(mst) is Graph:
            self.mst = mst
            return mst
        else:
            raise TypeError(f"{type(mst)} is not None or Graph")

    def drawEdges(
        self,
        edges: None | list[tuple[float, int, int]] = None,
        clear: bool = True,
        fill: str = "#faf7f2",
    ):
        xOffset = self.canvas.pinImg.pinSize[0] // 2
        yOffset = self.canvas.pinImg.pinSize[1] // 2
        if clear:
            for line in self.canvas.lines:
                self.canvas.delete(line)

        if not edges:
            edges = self.edges

        for edge in edges:
            loc1 = self.canvas.locations[edge[1]]
            loc2 = self.canvas.locations[edge[2]]
            self.canvas.lines.append(
                self.canvas.create_line(
                    loc1[0] + xOffset,
                    loc1[1] + yOffset,
                    loc2[0] + xOffset,
                    loc2[1] + yOffset,
                    width=2,
                    fill=fill,
                )
            )

    def getRouteCost(self, vertices: Sequence["Vertex"] | None = None) -> float:
        """Sum total cost for all existing edges (the total distance travelled w/ current route)"""
        cost = 0
        if not vertices:
            for edge in self.edges:
                cost += edge[0]
            return cost

        # keys = set(self.adj_list)
        # if vertices[0] not in keys:
        #     raise Exception("Invalid vertex in provided route.")

        for i in range(1, len(vertices)):
            # if vertices[i] not in keys:
            #     raise Exception("Invalid vertex in provided route.")
            for adjVert, weight in self.adj_list[vertices[i]]:
                if adjVert == vertices[i - 1]:
                    cost += weight
                    break
        return cost

    def nearestNeighborRoute(
        self, startVertex: int | None = None
    ) -> tuple[list["Vertex"], float]:
        """
        Get a guess at the optimal route by going to the least costly connected vector.
        Time complexity: O(n+n(nlogn)+n^2+n) -> O(n^2(logn+1))
        - n to put each vertex in set
        - n(nlogn) to merge sort list of edges to all other vertices for all n vertices
        - n^2 to loop through every vertex and check if not already visited
        - n to get the distance from last in route to start vertex
        """
        if not startVertex:
            startVertex = self.canvas.getStartPin()

        unvisited = set(vert for vert in list(self.adj_list))
        unvisited.remove(startVertex)
        route = [startVertex]
        distance = 0

        for vert in list(self.adj_list):
            self.adj_list[vert].sort(key=lambda edge: edge[1])

        # i think i can make this more efficient... how? use sets to see if existing visit?
        while unvisited:
            lastVert = route[-1]
            nextVert = None
            weight = 0
            for adjVert, dist in self.adj_list[lastVert]:
                if adjVert in unvisited:
                    nextVert, weight = adjVert, dist
                    break
            route.append(nextVert)
            distance += weight
            unvisited.remove(nextVert)
        route.append(startVertex)
        for edge in self.adj_list[startVertex]:
            v2, w = edge
            if v2 == route[-2]:
                distance += w
                break
        return route, distance

    def bruteForceRoute(
        self, startVertex: int | None = None
    ) -> tuple[list["Vertex"], float]:
        """
        Get the shortest cycle by checking all permutations of paths to compare performance vs efficiency.
        Time complexity: O((n-1)!/2)
        - n for each vertex
        - n-1 due to excluding the start vertex when creating the permutation
        - (n-1)! for all permutations
        - dvided by 2 by skipping all reverse permutations
        """
        distance = float("inf")
        route = []
        if not startVertex:
            startVertex = self.canvas.getStartPin()

        if len(self.adj_list) <= 0:
            raise Exception("Missing vertices to construct path")

        # check all permutations of routes
        intermediaryVertices = set(self.adj_list)
        intermediaryVertices.remove(startVertex)
        for r in permutations(intermediaryVertices):
            # skip reverse routes
            # from https://stackoverflow.com/questions/960557/how-to-generate-permutations-of-a-list-without-reverse-duplicates-in-python-us
            # this extended slice reverses the permutation and uses comparison to make sure it is less, so it gets rid of half of perms
            if r <= r[::-1]:
                continue
            # construct cycle from intermediary route and loop back to start
            newRoute = [startVertex]
            for v in r:
                newRoute.append(v)
            newRoute.append(startVertex)

            newDistance = self.getRouteCost(newRoute)
            if newDistance < distance:
                route = newRoute
                distance = newDistance

        return route, distance

    def drawLowerBoundRoute(
        self,
        clear: bool = True,
        fill: str = "#faf7f2",
        offset: int | tuple[int, int] | None = None,
    ) -> tuple[list["Vertex"], float]:
        """
        Finds the lower bound of the optimal solutions using a MST in order to save time attempting to calculate it through brute force and draws it.

        MST is lower bound because if you delete an edge in the cycle, now have a spanning tree which must be at least the cost of the MST.
        """
        # TODO figure out how to actually get sequential route to make methods more uniform
        mst = self.getMST()
        route = []

        if type(offset) is int:
            xOffset = offset
            yOffset = offset
        elif type(offset) is tuple:
            xOffset = offset[0]
            yOffset = offset[1]
        else:
            # catch in case of invalid argument for offset
            xOffset = self.canvas.pinImg.pinSize[0] // 2
            yOffset = self.canvas.pinImg.pinSize[1] // 2

        for edge in mst.edges:
            _, v1, v2 = edge
            loc1 = self.canvas.locations[v1]
            loc2 = self.canvas.locations[v2]
            self.canvas.lines.append(
                self.canvas.create_line(
                    loc1[0] + xOffset,
                    loc1[1] + yOffset,
                    loc2[0] + xOffset,
                    loc2[1] + yOffset,
                    width=2,
                    fill=fill,
                )
            )
            self.canvas.tag_lower(self.canvas.lines[-1])

        distance = 0.0
        for edge in mst.edges:
            distance += edge[0]

        return route, distance

    def christofidesRoute(self):
        """
        Modifying of MST to become 1 cycle to approach optimal solution.
        Written based off of explanation from here: https://youtu.be/GiDsjIBOVoA?t=726
        O(n^4) time, but improved by the perfect matching algorithm. Blossom V would improve speed but ran out of time
        """
        mst = self.getMST()
        # get odd degree vertices in MST
        oddVertices = []
        for vertex in mst:
            if len(mst[vertex]) % 2:
                oddVertices.append(vertex)
        # pair up odd degree vertices w/ min weight to even out degrees
        # current implementation is brute force, TODO: blossom 5 implementation
        # https://pub.ista.ac.at/~vnk/papers/blossom5.pdf
        minDistance = float("inf")
        minMatchEdges = []
        # track permutations to verify skipping repeats
        # ps1 = []
        # ps2 = []
        for p in permutations(oddVertices):
            # skipping should improve by factor of 4?
            # skip reverse
            if p <= p[::-1]:
                continue
            # ps1.append(p)
            # skip subsets of 2 being reversed
            if p[1::2] < p[::2]:
                continue
            # ps2.append(p)
            edges = []
            dist = 0
            for i in range(1, len(p), 2):
                v1 = p[i - 1]
                v2 = p[i]
                w = 0
                for adjVertex, distance in self[v1]:
                    if adjVertex == v2:
                        w = distance
                        dist += w
                        break

                edges.append([w, v1, v2])

            if dist < minDistance:
                minMatchEdges = edges
                minDistance = dist

        # add min cost perfect match to MST for Eulerian tour
        for edge in minMatchEdges:
            mst.addEdge(edge[1], edge[2], edge[0])

        # create new graph by skipping repeated vertices
        # christofideGraph = DisplayGraph(self.canvas)
        startVertex = self.canvas.getStartPin()
        # christofideGraph.addVertex(startVertex)
        unvisited = {vert for vert in mst}
        unvisited.remove(startVertex)
        route = [startVertex]
        distance = 0
        while unvisited:
            lastVert = route[-1]
            nextVert = None
            w = None
            for adjVert, weight in mst[lastVert]:
                if adjVert not in route:
                    nextVert = adjVert
                    w = weight
                    break
            # if the mst does not have path to unvisited node, back track until next valid
            if not nextVert:
                result = None
                i = -2
                while not result:
                    # then vert before last has another direction it can go
                    lastVert = route[i]
                    for adjVert, weight in mst[lastVert]:
                        if adjVert not in route:
                            nextVert = adjVert
                            break
                    # now find distance from last step to next
                    result = self.findEdge(route[-1], nextVert)
                    if result:
                        w = result[0]
                    else:
                        # back trace if needed
                        i -= 1

            unvisited.remove(nextVert)
            # christofideGraph.addVertex(nextVert)
            # christofideGraph.addEdge(route[-1],nextVert,w)
            distance += w
            route.append(nextVert)

        distance += self.findEdge(startVertex, route[-1])[0]
        route.append(startVertex)
        return route, distance


class PinImage(ImageTk.PhotoImage):
    def __init__(self):
        pinPath = "./pin.png"
        self.pinSize = (20, 35)
        super().__init__(
            Image.open(pinPath).resize(self.pinSize, Image.Resampling.NEAREST)
        )

    def bluePin(self):
        path = "./pinBlue.png"
        return ImageTk.PhotoImage(
            Image.open(path).resize(self.pinSize, Image.Resampling.NEAREST)
        )


class PinCanvas(ctk.CTkCanvas):
    def __init__(self, master, font, size, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            bg="#000001",
            bd=0,
            highlightthickness=0,
            relief="ridge",
            height=size[0],
            width=size[1],
        )
        self.grid(row=0, column=3, padx=0, pady=0, rowspan=3, sticky="nsew")
        set_opacity(self, color="#000001")
        # Pin Stuff
        self.pinImg = PinImage()
        self.bluePinImg = self.pinImg.bluePin()
        self.locations = {}
        self.lines = []
        self.startPin: int | None = None

        self.pinCoords = ctk.CTkLabel(
            self,
            text="X: None Y: None",
            font=font,
            # text_color="#f4eadf",
            text_color="gray60",
            fg_color="#000001",
        )
        self.pinCoords.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        def __createPinHelper(event):
            return self.createPin(
                (
                    self.canvasx(event.x - (self.pinImg.pinSize[0] // 2)),
                    self.canvasy(event.y - (self.pinImg.pinSize[1] // 2)),
                )
            )

        self.bind("<Double-Button-1>", __createPinHelper, add="+")

    def __checkBounds(self, newLoc) -> tuple[int, int]:
        seCorner = (
            self.winfo_width() - self.pinImg.pinSize[0] - 1,
            self.winfo_height() - self.pinImg.pinSize[1],
        )
        corners = [(0, 0), seCorner]
        result = newLoc
        if corners[0][0] > newLoc[0]:
            result = (corners[0][0], result[1])
        elif newLoc[0] > corners[1][0]:
            result = (corners[1][0], result[1])
        if corners[0][1] > newLoc[1]:
            result = (result[0], corners[0][1])
        elif newLoc[1] > corners[1][1]:
            result = (result[0], corners[1][1])

        return result

    def __movePin(self, event: Event, pin) -> None:
        newLoc = (
            self.canvasx(event.x - self.__dragOffset[0]),
            self.canvasy(event.y - self.__dragOffset[1]),
        )
        newLoc = self.__checkBounds(newLoc)

        # prevent overlap on drag by shifting from cursor
        while True:
            changed = False
            for pin2, loc2 in self.locations.items():
                if loc2 == newLoc and pin != pin2:
                    offset = 5
                    newLoc = (newLoc[0] + offset, newLoc[1] + offset)
                    self.__dragOffset = (
                        self.__dragOffset[0] + offset,
                        self.__dragOffset[1] + offset,
                    )
                    # self.locations[pin] = newLoc
                    changed = True
                    print("Cannot overlap pins!")
            if not changed:
                break

        self.moveto(pin, newLoc[0], newLoc[1])
        self.locations[pin] = newLoc

    def __setDragOffset(self, event: Event, pin) -> None:
        """Get mouse location offset from top left corner when they start dragging"""
        loc = self.locations[pin]
        self.__dragOffset = (
            self.canvasx(event.x) - loc[0],
            self.canvasy(event.y) - loc[1],
        )

    def __removePin(self, event: Event|None, pin) -> None:
        self.delete(pin)
        self.locations.pop(pin, None)
        if self.startPin == pin:
            self.startPin = None

    def __updateCoordText(self, event: Event|None, pin) -> None:
        self.pinCoords.configure(
            text=f"X: {int(self.locations[pin][0])} Y:{int(self.locations[pin][1])}"
        )
        # self.itemconfigure(self.test,text=f"X: {int(self.locations[pin][0])} Y:{int(self.locations[pin][1])}")canvas

    def setStartPin(self, pin) -> None:
        if pin == self.startPin:
            return
        if self.startPin:
            self.itemconfigure(self.startPin, image=self.pinImg)
        self.startPin = pin
        self.itemconfigure(pin, image=self.bluePinImg)

    def createPin(self, loc) -> None:
        """
        Create pin image on canvas at given location, update location in dictionary, and bind the needed functions to the pin.
        """
        # maybe add label under pin that denotes tag id? pair in tuple and move together?
        for pin, loc2 in self.locations.items():
            if loc2 == loc:
                print("Cannot overlap pins!")
                return
        pin = self.create_image(loc[0], loc[1], image=self.pinImg, anchor="nw")
        self.locations[pin] = loc

        # use default arguments in order to know which pin called this function since bind only does event
        def moveHandler(event, self=self, pin=pin):
            return self.__movePin(event, pin)

        def offsetHandler(event, self=self, pin=pin):
            return self.__setDragOffset(event, pin)

        def removeHandler(event, self=self, pin=pin):
            return self.__removePin(event, pin)

        def coordHandler(event, self=self, pin=pin):
            return self.__updateCoordText(event, pin)

        def startHandler(event, self=self, pin=pin):
            self.setStartPin(pin)

        self.tag_bind(pin, "<Button-1>", offsetHandler, add="+")
        self.tag_bind(pin, "<Button1-Motion>", coordHandler, add="+")
        self.tag_bind(pin, "<Button1-Motion>", moveHandler, add="+")
        self.tag_bind(pin, "<Button-3>", removeHandler, add="+")
        self.tag_bind(pin, "<Button-2>", startHandler, add="+")
        
        self.__updateCoordText(None, pin)

    def raisePins(self) -> None:
        for pin in list(self.locations):
            self.tkraise(pin)

    def drawAllLines(self):
        xOffset = self.pinImg.pinSize[0] // 2
        yOffset = self.pinImg.pinSize[1] // 2
        for line in self.lines:
            self.delete(line)
        for pin1, loc1 in self.locations.items():
            for pin2, loc2 in self.locations.items():
                if pin1 != pin2:
                    self.lines.append(
                        self.create_line(
                            loc1[0] + xOffset,
                            loc1[1] + yOffset,
                            loc2[0] + xOffset,
                            loc2[1] + yOffset,
                            width=2,
                            fill="#faf7f2",
                        )
                    )
        self.raisePins()

    def drawRoute(
        self,
        pins: list["Vertex"],
        clear: bool = True,
        fill: str = "#faf7f2",
        offset: int | tuple[int, int] | None = None,
    ) -> None:
        """
        Draw lines between vertices given a list of ordered vertices to traverse through.
        clear: delete all existing lines before drawing new ones.
        fill: line color to use when drawing lines.
        offset: Default (None) used to offset from top left corner to center of pinImg.
            - single int for same offset in x and y
            - tuple for different offset in x and y
        """
        if type(offset) is int:
            xOffset = offset
            yOffset = offset
        elif type(offset) is tuple:
            xOffset = offset[0]
            yOffset = offset[1]
        else:
            # catch in case of invalid argument for offset
            xOffset = self.pinImg.pinSize[0] // 2
            yOffset = self.pinImg.pinSize[1] // 2

        if clear:
            for line in self.lines:
                self.delete(line)

        for i in range(1, len(pins)):
            loc1 = self.locations[pins[i - 1]]
            loc2 = self.locations[pins[i]]
            self.lines.append(
                self.create_line(
                    loc1[0] + xOffset,
                    loc1[1] + yOffset,
                    loc2[0] + xOffset,
                    loc2[1] + yOffset,
                    width=2,
                    fill=fill,
                )
            )
            self.tag_lower(self.lines[-1])
        # self.raisePins()

    def getStartPin(self) -> int | None:
        if len(self.locations) <= 0:
            raise Exception("Cannot create cycle from 0 pins placed.")
            return
        if not self.startPin:
            self.setStartPin(random.choice(list(self.locations)))
        return self.startPin

    def createCurrentGraph(self) -> None:
        self.graph = DisplayGraph(self)

        def distance(loc1: tuple[int, int], loc2: tuple[int, int]) -> float:
            return sqrt((loc2[0] - loc1[0]) ** 2 + (loc2[1] - loc1[1]) ** 2)

        pins = list(self.locations)
        for pin in pins:
            self.graph.addVertex(pin)
        for i in range(len(pins)):
            for j in range(i + 1, len(pins)):
                self.graph.addEdge(
                    pins[i],
                    pins[j],
                    distance(self.locations[pins[i]], self.locations[pins[j]]),
                )

        # self.graph.drawEdges()

    def resetPins(self) -> None:
        """Delete all pins from canvas and clean up any lines."""
        for pin in list(self.locations):
            self.__removePin(None, pin)
        for line in self.lines:
            self.delete(line)


class PinFrame(ctk.CTkFrame):
    def __init__(self, master, size, **kwargs):
        """Frame just to color back area of container and round the corners"""
        super().__init__(master, **kwargs)
        self.configure(
            fg_color="#a8c7a1",
            bg_color="transparent",
            height=size[0],
            width=size[1],
        )
        self.grid(row=0, column=3, padx=0, pady=0, rowspan=3, sticky="nsew")

        # create another helper in case the frame is above canvas and takes the events instead of the canvas
        def __createPinHelper(event):
            return self.master.pinCanvas.createPin(
                (
                    self.master.pinCanvas.canvasx(
                        event.x - (self.master.pinCanvas.pinImg.pinSize[0] // 2)
                    ),
                    self.master.pinCanvas.canvasy(
                        (event.y - (self.master.pinCanvas.pinImg.pinSize[1] // 2))
                    ),
                )
            )

        self.bind("<Double-Button-1>", __createPinHelper, add="+")


class ContainerFrame(ctk.CTkFrame):
    def __init__(self, master, font: tuple, **kwargs):
        super().__init__(master, **kwargs)
        self.font = font
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=7)
        self.grid_rowconfigure(0, weight=5)
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=1)

        pinAreaSize = (825, 500)
        self.pinFrame = PinFrame(self, pinAreaSize)
        self.pinCanvas = PinCanvas(self, font, pinAreaSize)

        # create header
        headerFontSize = font[1] * 2.5 // 1
        self.title = ctk.CTkLabel(
            self,
            text="Road Trip Plotter",
            font=(font[0], headerFontSize),
            justify="left",
            anchor="sw",
            corner_radius=3,
        )
        self.title.grid(
            row=0, column=0, padx=10, pady=(10, 0), columnspan=3, sticky="sew"
        )
        # create body
        bodyText = "Double left click to place a pin.\nLeft click drag and drop.\nRight click pin to delete.\nMiddle click to select the start.\nSubmit when ready!"
        self.body = ctk.CTkLabel(
            self,
            text=bodyText,
            justify="left",
            anchor="sw",
            corner_radius=3,
            font=font,
        )
        self.body.grid(
            row=1, column=0, padx=10, pady=(0, 10), columnspan=3, sticky="new"
        )

        buttonFont = (font[0], font[1] // 1.5)
        # create submit and reset button
        self.submitButton = ctk.CTkButton(
            self,
            text="Submit",
            command=self.submitLocations,
            font=buttonFont,
        )
        self.submitButton.grid(row=2, column=0, padx=(5, 2), pady=5, sticky="sew")

        self.SOLUTIONS = [
            "Nearest Neigbor",
            "Brute Force",
            "Christofide's Approximation",
            "Minimum Spanning Tree",
            "Compare to MST Lower Bound",
            "Compare to Brute Force",
        ]
        self.solutionComboBox = ctk.CTkComboBox(
            self,
            values=self.SOLUTIONS,
            font=buttonFont,
            command=self.solutionChoice,
            button_hover_color=("#36719F", "#144870"),
            button_color=("#3B8ED0", "#1F6AA5"),
            state="readonly",
        )
        self.solutionComboBox.grid(row=2, column=1, padx=2, pady=5, sticky="sew")
        self.solutionComboBox.set(self.SOLUTIONS[0])
        self.choice = self.solutionComboBox.get()

        self.resetButton = ctk.CTkButton(
            self,
            text="Reset",
            command=self.resetPins,
            font=buttonFont,
        )
        self.resetButton.grid(row=2, column=2, padx=(2, 5), pady=5, sticky="sew")

    def solutionChoice(self, choice):
        self.choice = choice

    def submitLocations(self):
        self.pinCanvas.createCurrentGraph()
        startTime = time()
        if self.choice == self.SOLUTIONS[0]:
            # Nearest Neighbor
            route, distance = self.pinCanvas.graph.nearestNeighborRoute()
            dur = time() - startTime
            print(
                f"Nearest neighbor distance: {distance} u\nDuration: {dur:9.9f} s\nRoute: {route}"
            )
            print("-" * 15 + "\n")
        elif self.choice == self.SOLUTIONS[1]:
            # Brute force
            route, distance = self.pinCanvas.graph.bruteForceRoute()
            dur = time() - startTime
            print(
                f"Brute force distance: {distance} u\nDuration: {dur:9.9f} s\nRoute: {route}"
            )
            print("-" * 15 + "\n")
        elif self.choice == self.SOLUTIONS[3]:
            # MST
            route, distance = self.pinCanvas.graph.drawLowerBoundRoute()
            dur = time() - startTime
            print(f"MST distance: {distance} u\nDuration: {dur:9.9f} s\nRoute: {route}")
            print("-" * 15 + "\n")
            return
        elif self.choice == self.SOLUTIONS[2]:
            # Christofide algorithm approximation using MST
            route, distance = self.pinCanvas.graph.christofidesRoute()
            dur = time() - startTime
            print(
                f"Christofide's approximation distance: {distance} u\nDuration: {dur:9.9f} s\nRoute: {route}"
            )
            print("-" * 15 + "\n")
        elif self.choice == self.SOLUTIONS[4]:
            # Compare NN and MST
            route1, distance1 = self.pinCanvas.graph.nearestNeighborRoute()
            dur1 = time() - startTime
            print(
                f"Nearest neighbor distance: {distance1} u\nDuration: {dur1:9.9f} s\nRoute: {route1}"
            )
            print("-" * 15 + "\n")
            self.pinCanvas.drawRoute(route1)

            startTime = time()
            route2, distance2 = self.pinCanvas.graph.drawLowerBoundRoute(
                clear=False, fill="gray30", offset=(12, 19)
            )
            dur2 = time() - startTime
            print(
                f"Lower bound MST distance: {distance2} u\nDuration: {dur2:9.9f} s\nRoute: {route2}"
            )
            print("-" * 15 + "\n")

            startTime = time()
            route3, distance3 = self.pinCanvas.graph.christofidesRoute()
            dur3 = time() - startTime
            print(
                f"Christofide's approximation distance: {distance3} u\nDuration: {dur3:9.9f} s\nRoute: {route3}"
            )
            print("-" * 15 + "\n")
            self.pinCanvas.drawRoute(route3, clear=False, fill="black", offset=(14, 21))

            print(
                f"Time taken by NN solution: {(dur1 * 100 / dur2):9.3f}% of lower bound MST"
            )
            print(
                f"Cost of route by NN solution: {(distance1 * 100 / distance2) - 100:9.3f}% more than lower bound MST"
            )
            print(
                f"Time taken by Christofide's solution: {(dur3 * 100 / dur2):9.3f}% of lower bound MST"
            )
            print(
                f"Cost of route by Christofide's solution: {(distance3 * 100 / distance2) - 100:9.3f}% more than lower bound MST"
            )
            print("-" * 15 + "\n")
            return
        elif True:
            # Compare NN and brute force
            route1, distance1 = self.pinCanvas.graph.nearestNeighborRoute()
            dur1 = time() - startTime
            print(
                f"Nearest neighbor distance: {distance1} u\nDuration: {dur1:9.9f} s\nRoute: {route1}"
            )
            print("-" * 15 + "\n")
            self.pinCanvas.drawRoute(route1)

            startTime = time()
            route3, distance3 = self.pinCanvas.graph.christofidesRoute()
            dur3 = time() - startTime
            print(
                f"Christofide's approximation distance: {distance3} u\nDuration: {dur3:9.9f} s\nRoute: {route3}"
            )
            print("-" * 15 + "\n")
            self.pinCanvas.drawRoute(route3, clear=False, fill="black", offset=(12, 19))

            startTime = time()
            route2, distance2 = self.pinCanvas.graph.bruteForceRoute()
            dur2 = time() - startTime
            print(
                f"Brute force distance: {distance2} u\nDuration: {dur2:9.9f} s\nRoute: {route2}"
            )
            print("-" * 15 + "\n")
            self.pinCanvas.drawRoute(
                route2, clear=False, fill="gray30", offset=(14, 21)
            )

            print(
                f"Time taken by NN solution: {(dur1 * 100 / dur2):9.3f}% of brute force"
            )
            print(
                f"Cost of route by NN solution: {(distance1 * 100 / distance2) - 100:9.3f}% more than brute force"
            )
            print(
                f"Time taken by Christofide's solution: {(dur3 * 100 / dur2):9.3f}% of brute force"
            )
            print(
                f"Cost of route by Christofide's solution: {(distance3 * 100 / distance2) - 100:9.3f}% more than brute force"
            )
            print("-" * 15 + "\n")
            return
        self.pinCanvas.drawRoute(route)

    def resetPins(self):
        """Remove all pins from canvas"""
        self.pinCanvas.resetPins()


class RoadTripApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")
        font = ("Calibri", 18)

        self.title("Road Trip Route")
        self.geometry("1200x600")
        self.configure(
            bg="#faf7f2",
        )
        self.resizable(False, False)
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)
        self.container = ContainerFrame(self, font)


def main():
    window = RoadTripApp()
    window.mainloop()


if __name__ == "__main__":
    main()

"""
References:
https://www.pythontutorial.net/tkinter/
https://docs.python.org/3/library/tkinter.html#bindings-and-events
https://customtkinter.tomschimansky.com/tutorial/grid-system/
https://stackoverflow.com/questions/4299145/getting-the-widget-that-triggered-an-event

"""

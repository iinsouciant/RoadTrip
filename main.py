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

# TODO output cost and route together when returning output

class DisplayGraph(Graph):
    def __init__(self, canvas: "PinCanvas"):
        super().__init__()
        self.canvas: PinCanvas = canvas

    def drawEdges(self, edges: None | list[tuple[float, int, int]] = None, clear: bool = True, fill:str = "#faf7f2"):
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

    def getRouteCost(self, vertices: Sequence["Vertex"]|None = None) -> float:
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
                if adjVert == vertices[i-1]:
                    cost += weight
                    break
        return cost
    
    def nearestNeighborRoute(self, startVertex: int|None = None) -> list["Vertex"]:
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
        
        startTime = time()
        unvisited = set(vert for vert in list(self.adj_list))
        unvisited.remove(startVertex)
        route = [startVertex]
        distance = 0

        for vert in list(self.adj_list):
            self.adj_list[vert].sort(key= lambda edge: edge[1])

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
            # minDist = float("inf")
            # for adjVert in unvisited:
            #     minDist = min(self.adj_list[])
        route.append(startVertex)
        for edge in self.edges:
            w, v1, v2 = edge
            if (v1 == route[-2] or v2 == route[-2]) and (v1 == route[-1] or v2 == route[-1]):
                distance += w
                break
        dur = time() - startTime
        print(f"Nearest neighbor distance: {distance} u\nDuration: {dur:9.9f} s")
        print("-"*15+'\n')
        return route
    
    # def nearestNeighborGraph(self) -> None:
    #     """ Removes extra edges of the current graph to create one cycle using nearest neighbors."""

    def bruteForceRoute(self, startVertex: int|None = None) -> Sequence["Vertex"]:
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
        
        startTime = time()
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

        dur = time() - startTime
        print(f"Brute force distance: {distance} u\nDuration: {dur:9.9f} s")
        print("-"*15+'\n')
        return route


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

        # less options to make text pretty do not use
        # self.test = self.create_text(100,10,anchor="nw",font=font,text="X: None Y: None",)

        self.pinCoords = ctk.CTkLabel(
            self,
            text="X: None Y: None",
            font=font,
            text_color="#f4eadf",
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

    def __removePin(self, event: Event, pin) -> None:
        self.delete(pin)
        self.locations.pop(pin, None)
        if self.startPin == pin:
            self.startPin = None

    def __updateCoordText(self, event: Event, pin) -> None:
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

    def drawRoute(self, pins:list["Vertex"]) -> None:
        xOffset = self.pinImg.pinSize[0] // 2
        yOffset = self.pinImg.pinSize[1] // 2
        for line in self.lines:
            self.delete(line)
        for i in range(1,len(pins)):
            loc1 = self.locations[pins[i-1]]
            loc2 = self.locations[pins[i]]
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
        # self.title.configure(fg_color="gray30", height=headerFontSize+10)
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

        buttonFont = (font[0], font[1]//1.5)
        # create submit and reset button
        self.submitButton = ctk.CTkButton(
            self, text="Submit", command=self.submitLocations, font=buttonFont,
        )
        self.submitButton.grid(row=2, column=0, padx=(5, 2), pady=5, sticky="sew")

        self.SOLUTIONS = ["Nearest Neigbor", "Brute Force", "Compare"]
        self.solutionComboBox = ctk.CTkComboBox(
            self,
            values=self.SOLUTIONS,
            font=buttonFont,
            command=self.solutionChoice,
            button_hover_color=('#36719F', '#144870'),
            button_color=('#3B8ED0', '#1F6AA5'),
            state="readonly",
        )
        self.solutionComboBox.grid(row=2, column=1, padx=2, pady=5, sticky="sew")
        self.solutionComboBox.set(self.SOLUTIONS[0])
        self.choice = self.solutionComboBox.get()

        self.resetButton = ctk.CTkButton(self, text="Reset", command=self.resetPins, font=buttonFont,)
        self.resetButton.grid(row=2, column=2, padx=(2, 5), pady=5, sticky="sew")

    def solutionChoice(self, choice):
        self.choice = choice

    def submitLocations(self):
        self.pinCanvas.createCurrentGraph()
        if self.choice == self.SOLUTIONS[0]:
            route = self.pinCanvas.graph.nearestNeighborRoute()
        elif self.choice == self.SOLUTIONS[1]:
            route = self.pinCanvas.graph.bruteForceRoute()
        elif True:
            route1 = self.pinCanvas.graph.bruteForceRoute()
            route2 = self.pinCanvas.graph.nearestNeighborRoute()
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

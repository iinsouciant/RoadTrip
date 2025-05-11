from tkinter import PhotoImage, Tk, Label, Event
from PIL import Image, ImageTk
import customtkinter as ctk
import pywinstyles


class PinImage(ImageTk.PhotoImage):
    def __init__(self):
        pinPath = "./pin.png"
        self.pinSize = (20, 35)
        super().__init__(Image.open(pinPath).resize(self.pinSize,Image.Resampling.NEAREST))


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
        self.grid(row=0, column=2, padx=0, pady=0, rowspan=3, sticky="nsew")
        pywinstyles.set_opacity(self, color="#000001")
        # Pin Stuff
        self.pinImg = PinImage()
        self.locations = {}

        self.pinCoords = ctk.CTkLabel(
            self, text="X: None Y: None", font=font, text_color="black"
        )
        self.pinCoords.pack(padx="10px", pady="10px", anchor="se")

        def __createPinHelper(event):
            return self.createPin((self.canvasx(event.x-(self.pinImg.pinSize[0]//2)),self.canvasy(event.y-(self.pinImg.pinSize[1]//2))))
        self.bind("<Double-Button-1>", __createPinHelper, add='+')
        

    def __movePin(self, event: Event, pin):
        newLoc = (
            self.canvasx(event.x - self.__dragOffset[0]),
            self.canvasy(event.y - self.__dragOffset[1]),
        )
        # how do i prevent these from overlapping on drag?
        # while True:
        #     changed = False
        #     for pin, loc in self.locations.items():
        #         if loc == newLoc:
        #             offset = 5
        #             newLoc = (newLoc[0]+offset, newLoc[1]+offset)
        #             self.__dragOffset = (self.canvasx(event.x) - loc[0] + offset, self.canvasy(event.y) - loc[1] + offset)
        #             # self.locations[pin] = newLoc
        #             changed = True
        #             print("Cannot overlap pins!")
        #     if not changed:
        #         break

        # if i try  this way, when i attempt to drag another pin, it drags the old one. how do fix
        for pin, loc in self.locations.items():
            if loc == newLoc:
                print("Cannot overlap pins!")
                return
        self.moveto(pin, newLoc[0], newLoc[1])
        self.locations[pin] = newLoc

    def __setDragOffset(self, event: Event, pin):
        """Get mouse location offset from top left corner when they start dragging"""
        loc = self.locations[pin]
        self.__dragOffset = (self.canvasx(event.x) - loc[0], self.canvasy(event.y) - loc[1])

    def __removePin(self, event: Event, pin):
        print("remove this pin!")

    def updateCoordText(self, event: Event):
        self.pinCoords.configure(
            text=f"X: {int(event.x - self.__dragOffset[0])} Y:{int(event.y - self.__dragOffset[1])}"
        )

    def createPin(self, loc):
        """
        Create pin image on canvas at given location, update location in dictionary, and bind the needed functions to the pin.
        """
        for pin, oldLoc in self.locations.items():
            if oldLoc == loc:
                print("Cannot overlap pins!")
                return
        pin = self.create_image(loc[0], loc[1], image=self.pinImg, anchor='nw')
        self.locations[pin] = loc
        # use default arguments in order to know which pin called this function since bind only does event
        def moveHandler(event, self=self, pin=pin):
            return self.__movePin(event, pin)

        def offsetHandler(event, self=self, pin=pin):
            return self.__setDragOffset(event, pin)
        
        def removeHandler(event, self=self, pin=pin):
            return self.__removePin(event, pin)

        self.tag_bind(pin, "<Button-1>", offsetHandler, add="+")
        self.tag_bind(pin, "<Button1-Motion>", self.updateCoordText, add="+")
        self.tag_bind(pin, "<Button1-Motion>", moveHandler, add="+")
        self.tag_bind(pin, "<Button-3>", removeHandler, add="+")


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
        self.grid(row=0, column=2, padx=0, pady=0, rowspan=3, sticky="nsew")
        
        # create another helper in case the frame is above canvas and takes the events instead of the canvas
        def __createPinHelper(event):
            return self.master.pinCanvas.createPin(
                (
                    self.master.pinCanvas.canvasx(event.x-(self.master.pinCanvas.pinImg.pinSize[0]//2)),
                    self.master.pinCanvas.canvasy((event.y-(self.master.pinCanvas.pinImg.pinSize[1]//2)))
            ))
        self.bind("<Double-Button-1>", __createPinHelper, add='+')
        

class ContainerFrame(ctk.CTkFrame):
    def __init__(self, master, font: tuple, **kwargs):
        super().__init__(master, **kwargs)
        self.font = font
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=6)
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
            row=0, column=0, padx=10, pady=(10, 0), columnspan=2, sticky="sew"
        )
        # create body
        bodyText = "Double left click to place a pin.\nLeft click drag and drop.\nRight click pin to delete.\nSubmit when ready!"
        self.body = ctk.CTkLabel(
            self,
            text=bodyText,
            justify="left",
            anchor="sw",
            corner_radius=3,
            font=font,
        )
        self.body.grid(
            row=1, column=0, padx=10, pady=(0, 10), columnspan=2, sticky="new"
        )
        # create submit and reset button
        self.submitButton = ctk.CTkButton(
            self, text="Submit", command=self.submit_callback
        )
        self.submitButton.grid(row=2, column=0, padx=(5, 2), pady=5, sticky="sew")
        self.resetButton = ctk.CTkButton(
            self, text="Reset", command=self.reset_callback
        )
        self.resetButton.grid(row=2, column=1, padx=(2, 5), pady=5, sticky="sew")

    def submit_callback(self):
        print("submitted")

    def reset_callback(self):
        print("reset")


class RoadTripApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")
        font = ("Calibri", 18)

        self.title("Road Trip Route")
        self.geometry("1200x600")
        self.configure(bg="#faf7f2",)
        self.resizable(False, False)
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)
        self.container = ContainerFrame(self, font)



def main():
    print("Hello from roadtrip!")
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

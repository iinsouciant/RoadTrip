from tkinter import PhotoImage, Tk, Label, Event
from PIL import Image, ImageTk
import customtkinter as ctk
import pywinstyles

class PinImage(ImageTk.PhotoImage):
    def __init__(self):
        pinPath = './pin.png'
        self.pinSize = (20, 35)
        super().__init__(Image.open(pinPath).resize(self.pinSize))

class PinCanvas(ctk.CTkCanvas):
    def __init__(self, master, font, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg="#000001", bd=0, highlightthickness=0, relief='ridge', )
        self.grid(row=0, column=2, padx=0, pady=0, rowspan=3, sticky="nsew")
        pywinstyles.set_opacity(self, color="#000001")
        # // maybe move this out of frame and make transparent so then the corners are rounded again
        # Pin Stuff
        self.pinImg = PinImage()
        self.locations = {}
        self.locations[self.create_image(30,30,image=self.pinImg)] = (30,30)
        self.locations[self.create_image(30,35,image=self.pinImg)] = (30,35)

        self.pinCoords = ctk.CTkLabel(self, text="X: None Y: None", font=font, text_color="black")
        self.pinCoords.pack(padx="10px", pady="10px", anchor="se")

        # left click and move show coordinates
        #since it is bound to selected pin, it only happens if click on pin
        for pin in list(self.locations):
            # use default arguments in order to know which pin called this function since bind only does event
            def moveHandler(event, self=self, pin=pin):
                return self.__movePin(event, pin)
            def offsetHandler(event, self=self, pin=pin):
                return self.__setDragOffset(event, pin)
            self.tag_bind(pin, "<Button1-Motion>", self.updateCoordText, add="+")
            self.tag_bind(pin, "<Button1-Motion>", moveHandler, add="+")
            self.tag_bind(pin, "<Button-1>", offsetHandler, add="+")

        self.printWidgetType = True

    def __movePin(self, event:Event, pin):
        """ 
        can use lambda or local function handler to take arguments
        https://stackoverflow.com/questions/4299145/getting-the-widget-that-triggered-an-event
        https://stackoverflow.com/questions/7299955/tkinter-binding-a-function-with-arguments-to-a-widget
        """
        if self.printWidgetType:
            print(f"event widget type: {type(event.widget)}")
            self.printWidgetType = False
        newLoc = (self.canvasx(event.x-self.__dragOffset[0]),self.canvasy(event.y-self.__dragOffset[1]))

        self.moveto(pin,newLoc[0], newLoc[1])
        # update self.locations to new
        self.locations[pin] = newLoc

    def updateCoordText(self, event:Event):
        self.pinCoords.configure(text=f"X: {event.x-self.__dragOffset[0]} Y:{event.y-self.__dragOffset[1]}")

    def __setDragOffset(self, event:Event, pin):
        """ Get mouse location offset from top left corner when they start dragging"""
        loc = self.locations[pin]
        self.__dragOffset = (event.x-loc[0],event.y-loc[1])


class PinFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        """Frame just to color back area of container and round the corners"""
        super().__init__(master, **kwargs)
        self.configure(fg_color="#a8c7a1", bg_color="transparent")
        self.grid(row=0, column=2, padx=0, pady=0, rowspan=3, sticky="nsew")

class ContainerFrame(ctk.CTkFrame):
    def __init__(self, master, font: tuple, **kwargs):
        super().__init__(master, **kwargs)
        self.font = font
        # self.configure(bg_color='#f0dbdb')
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        # only need two columns with padding
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=5)
        self.grid_rowconfigure(0, weight=5)
        self.grid_rowconfigure(1,weight=2)
        self.grid_rowconfigure(2,weight=1)

        self.pinFrame = PinFrame(self)
        self.pinCanvas = PinCanvas(self, font)
        # create header
        headerFontSize = font[1] * 2.5 // 1
        self.title = ctk.CTkLabel(self, text="Road Trip Plotter", font=(font[0], headerFontSize), justify="left", anchor="sw", corner_radius=3,)
        # self.title.configure(fg_color="gray30", height=headerFontSize+10)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), columnspan=2, sticky="sew")
        # create body
        bodyText = "Left click to place pin or drag and drop.\nDouble left click pin to designate as the start.\nRight click pin to delete.\nSubmit when ready!"
        self.body = ctk.CTkLabel(self, text=bodyText, justify='left', anchor="sw", corner_radius=3, font=font,)
        self.body.grid(row=1, column=0, padx=10, pady=(0, 10), columnspan=2, sticky="new")
        # create submit and reset button
        self.submitButton = ctk.CTkButton(self,text="Submit", command=self.submit_callback)
        self.submitButton.grid(row=2, column=0, padx=(5, 2), pady=5,  sticky="sew")
        self.resetButton = ctk.CTkButton(self,text="Reset", command=self.reset_callback)
        self.resetButton.grid(row=2, column=1, padx=(2, 5), pady=5,  sticky="sew")

    def submit_callback(self):
        print("submitted")

    def reset_callback(self):
        print("reset")

class RoadTripApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")
        font = ('Calibri', 18)

        self.title("Road Trip Route")
        self.geometry("1200x600")
        self.configure(bg="#faf7f2")
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)
        self.container = ContainerFrame(self, font)




# def imageResize(path: str, newSize: tuple[int, int]) -> PhotoImage:
#     return ImageTk.PhotoImage(Image.open(path).resize(newSize))

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
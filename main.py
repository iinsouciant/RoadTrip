from tkinter import PhotoImage, Tk, Label
# from PIL import Image, ImageTk
import customtkinter as ctk

class PinCanvas(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg="#a8c7a1", bd=0, highlightthickness=0, relief='ridge', )
        self.grid(row=0, column=1, padx=0, pady=0, rowspan=3, sticky="nsew")

class TextFrame(ctk.CTkFrame):
    def __init__(self, master, font: tuple, **kwargs):
        super().__init__(master, **kwargs)
        self.font = font
        self.configure(fg_color="transparent",bg_color="transparent")
        self.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.grid_rowconfigure(0,weight=1)
        # create submit button

class ContainerFrame(ctk.CTkFrame):
    def __init__(self, master, font: tuple, **kwargs):
        super().__init__(master, **kwargs)
        self.font = font
        # self.configure(bg_color='#f0dbdb')
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        # only need two columns with padding
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1,weight=3)
        self.grid_rowconfigure(2,weight=1)

        self.pinCanvas = PinCanvas(self)
        # create header
        self.title = ctk.CTkLabel(self, text="Road Trip Plotter", fg_color="gray30", font=(font[0], font[1]*1.5//1), corner_radius=3,)
        # self.title.configure(height=font[1]*1.5//1+10)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="new")
        # create body
        bodyText = "Left click to place pin or drag and drop.\nDouble left click pin to designate as the start\nRight click pin to delete.\nSubmit when ready!"
        self.body = ctk.CTkLabel(self, text=bodyText, justify='left', corner_radius=3, font=font)
        self.body.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="ew")


class RoadTripApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")
        pinPath = './pin.png'
        pinSize = (20, 35)
        self.locations = {}
        font = ('Calibri', 18)

        # custom window for grids and weights
        # 5 rows, 4 columns
        # drag and drop area has weight_x=8, weight_y=6
        # border has weight=1
        # body has weight_x=2, weight_y=4
        # header/title has weight_x=2, weight_y=2, centered
        # same for button at bottom
        # custom ctklabel for Title and body w/ instructions
        # custom button for rounded button
        # normal label for pins

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
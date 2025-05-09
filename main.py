from tkinter import PhotoImage, Tk, Label
# from PIL import Image, ImageTk
import customtkinter as ctk
import pywinstyles

class PinCanvas(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg="#000001", bd=0, highlightthickness=0, relief='ridge', )
        self.grid(row=0, column=2, padx=0, pady=0, rowspan=3, sticky="nsew")
        pywinstyles.set_opacity(self, color="#000001")
        # // maybe move this out of frame and make transparent so then the corners are rounded again
        # Pin Stuff
        pinPath = './pin.png'
        pinSize = (20, 35)
        self.locations = {}

class PinFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
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
        self.pinCanvas = PinCanvas(self)
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
        self.submitButton.grid(row=2, column=0, padx=2, pady=5,  sticky="sew")
        self.resetButton = ctk.CTkButton(self,text="Reset", command=self.reset_callback)
        self.resetButton.grid(row=2, column=1, padx=2, pady=5,  sticky="sew")

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
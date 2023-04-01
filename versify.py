"""
File containing the user interface for Versify
"""
from discography import *
from main import *
import tkinter as tk
from tkinter import messagebox
import customtkinter
import threading
from random import choice

# setting default asthetics of the GUI
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("green")


class VersifyGUI:
    """Class containing the functionality of the Versify GUI.
    """
    def __init__(self):
        # list containing the progress bar messages
        self.progress_text = ["Don't worry - a few words tried to escape, but we caught them",
                              "Generating witty dialog...",
                              "99 bottles of beer on the wall...",
                              "Dividing by zero...",
                              "Feel free to spin in your chair",
                              "Why is a piano so hard to open? Because the keys are on the inside.",
                              "What type of music are balloons afraid of? Pop music.",
                              "Counting backwards from infinity...",
                              "Initializing the initializer...",
                              "Grabbing extra minions...",
                              "Are we there yet?",
                              "(Insert quarter)"]

        # creating the window
        self.root = customtkinter.CTk()
        self.root.geometry('800x370')
        self.root.title('Versify')

        # creating the main screen title and description text
        self.title = customtkinter.CTkLabel(self.root, text='Welcome to VERSIFY: The Future of Songwriting',
                                            font=customtkinter.CTkFont(family="Futura", size=20, weight="bold"))
        self.desc = customtkinter.CTkLabel(self.root,
                                           text='VERSIFY aims to generate song lyrics in the style of an artist you '
                                                'want!\nTell us the name of an artist!',
                                           font=customtkinter.CTkFont(family="Futura", size=16))
        self.title.pack(padx=20, pady=35)
        self.desc.pack()

        # entry box for artist name input
        self.entry = customtkinter.CTkEntry(self.root, font=customtkinter.CTkFont(family="Futura", size=16), width=300)
        self.entry.pack(pady=25)

        # creating a progress bar with randomly selected text underneath
        self.progress_bar = customtkinter.CTkProgressBar(
            self.root, orientation='horizontal', mode='indeterminate', width=500, indeterminate_speed=0.5)
        self.progress_text = customtkinter.CTkLabel(self.root, text=choice(self.progress_text),
                                                    font=customtkinter.CTkFont(family="Futura", size=14))
        # generate button, once clicked will call self.generate()
        self.button = customtkinter.CTkButton(
            self.root, text='Generate', font=customtkinter.CTkFont(family="Futura", size=16))
        self.button.pack(pady=10)
        self.button.configure(command=self.start_progress_bar)

        self.root.mainloop()

    def start_progress_bar(self) -> None:
        """Starts the generation progress with the progress bar and loading message
        """
        # shows the progress bar and text
        self.progress_bar.pack(pady=20)
        self.progress_bar.start()
        self.progress_text.pack()
        # disabling the generate button so it cannot be pressed again
        self.button.configure(state=tk.DISABLED)

        # threading is used to call self.generate() seperately since otherwise, the method call within,
        # generate_discography(), will freeze the program due to the time it takes to complete
        threading.Thread(target=self.generate).start()

    def generate(self) -> None:
        """Creates a pop-up window with the generated song, or an error pop-up window if the artist cannot be found.
        """
        # generating the discography
        discography = generate_discography(self.entry.get().strip())

        # creates an error box if the discography is None, otherwise proceeds with song generation
        if discography is None:
            messagebox.showinfo(title='Generation Error', message='Artist cannot be found')
        else:
            # generating the characteristics of the song and placing them on a new window
            song_title = generate_song_title(discography)
            generated_song = generate_song(discography)

            # creates a "top level" window (a seperate window from the main one)
            song_win = customtkinter.CTkToplevel(self.root)
            song_win.geometry('700x1000')
            song_win.title(song_title)

            song_text = customtkinter.CTkLabel(song_win, text=generated_song, font=customtkinter.CTkFont(
                family="Futura", size=15))
            song_text.pack(padx=10, pady=20)

        # stops the progress bar and enables the button for more generation
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_text.pack_forget()
        self.button.configure(state=tk.NORMAL)


if __name__ == "__main__":
    # starts Versify
    VersifyGUI()

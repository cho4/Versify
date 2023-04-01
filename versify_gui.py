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


class VersifyGUI:
    """Class containing the functionality of the Versify GUI.
    """
    def __init__(self):
        # setting default asthetics of the GUI
        customtkinter.set_appearance_mode("Dark")
        customtkinter.set_default_color_theme("green")

        # list containing the progress bar messages
        # some messages are drawn from https://gist.github.com/meain/6440b706a97d2dd71574769517e7ed32
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
                              "(Insert quarter)",
                              "Would you like fries with that?",
                              "Checking the gravitational constant in your locale...",
                              "Go ahead -- hold your breath!",
                              "You're not in Kansas any more",
                              "We're testing your patience",
                              "While the satellite moves into position...",
                              "We need a new fuse...",
                              "The server is powered by a lemon and two electrodes.",
                              "Counting the sheep in the sky...",
                              "Time flies when you’re having fun.",
                              "A commit a day keeps the mobs away",
                              "Well, this is embarrassing.",
                              "Kindly hold on as we convert this bug to a feature...",
                              "Distracted by cat gifs.",
                              "Please wait... Consulting the manual...",
                              "Everything in this universe is either a potato or not a potato.",
                              "Sorry we are busy catching em' all, we're done soon.",
                              "You are number 2843684714 in the queue."]

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
        self.progress_message = customtkinter.CTkLabel(self.root,
                                                       text=choice(self.progress_text),
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
        self.progress_message.configure(text=choice(self.progress_text))
        self.progress_message.pack()

        # disabling the generate button and entry box, so they cannot be used again during this process
        self.button.configure(state=tk.DISABLED)
        self.entry.configure(state=tk.DISABLED)

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
            generated_song = generate_song(discography)
            song_title = generate_song_title(generated_song)

            # creates a "top level" window (a seperate window from the main one)
            song_win = customtkinter.CTkToplevel(self.root)
            song_win.grid_rowconfigure(0, weight=1)
            song_win.grid_columnconfigure(0, weight=1)
            song_win.geometry('700x1000')
            song_win.title(song_title)

            # creates the textbox
            song_lyrics = customtkinter.CTkTextbox(master=song_win, width=650, height=900,
                                                   font=customtkinter.CTkFont(family="Futura", size=17))
            # inserts the song lyrics into the textbox
            song_lyrics.insert("0.0", generated_song)
            # disables the textbox so the user cannot interact with the lyrics
            song_lyrics.configure(state="disabled")
            song_lyrics.grid(row=0, column=0, sticky="nsew")

            # creates the scrollbar
            scrollbar = customtkinter.CTkScrollbar(song_win, command=song_lyrics.yview)
            scrollbar.grid(row=0, column=1, sticky="ns")

            song_lyrics.configure(yscrollcommand=scrollbar.set)

        # removes the progress bar and enables the button and entry box for more generation
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_message.pack_forget()
        self.button.configure(state=tk.NORMAL)
        self.entry.configure(state=tk.NORMAL)


if __name__ == "__main__":
    # starts Versify
    VersifyGUI()

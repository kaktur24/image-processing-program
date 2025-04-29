from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import colorchooser
from tkinter import messagebox
from math import ceil
from collections import namedtuple
from apomenu import *
from apoimage import getimage
from apoprofile import plot_profile, close_profiles


class AppGui:
    # Frame with topbar and scrollabel canvas
    ImageFrame = namedtuple("ImageFrame", ["mainframe", "topbar", "canvas"])
    # Combined scale and entry
    ScaleEntry = namedtuple("ScaleEntry", ["frame", "scale", "entry"])
    # Settings window with 3 buttons: Apply, Check, Cancel
    ApplyCheckWindow = namedtuple("ApplyCheckWindow", ["window", "canvas", "frames", "applybut", "checkbut", "cancelbut"])
    # Settings window with 2 buttons: Apply, Cancel
    ApplyWindow = namedtuple("ApplyWindow", ["window", "canvas", "frames", "applybut", "cancelbut"])
    # Settings window for math operations with lists of images and entry fields for numbers
    MathOpWindow = namedtuple("MathOpWindow", ["window", "images", "numbers", "resultname", "checkboxvar", "applybut", "cancelbut"])
    # Settings window for neighbourhood operations
    NeighbourhoodOpWindow = namedtuple("NeighbourhoodOpWindow", ["window", "maskrbuts", "maskcode", "bordertypecode", "bordertypeparam"])
    # Prefix for non-disk paths
    internal_path_prefix = "<APO>" 


    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Initialization
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def __init__(self):
        self.root = Tk()
        self.menubar = prep_menu(self)
        self.tabmanager = ttk.Notebook(self.root)
        self.tabs = []

        self.root.geometry(self.__init_geometry())
        self.root.config(menu=self.menubar)
        self.tabmanager.pack(expand=True, fill=BOTH)

        self.tabmanager.bind("<<NotebookTabChanged>>", self.__adjust_menubaropts)

        logo = PhotoImage(file="logo.png")
        self.root.iconphoto(True, logo)
        self.root.title("APO program")
        self.root.bind_all("<Button-1>", lambda event: event.widget.focus_set())

        def close():
            close_profiles()
            self.root.quit()
            self.root.destroy()
        self.root.protocol("WM_DELETE_WINDOW", close)

        self.root.mainloop()

    # Geometry initialization for application main window.
    def __init_geometry(self):
        self.root.state("zoomed")

        display_width = self.root.winfo_screenwidth()
        display_height = self.root.winfo_screenheight()

        width = int(display_width / 1.5)
        height = int(display_height / 1.5)

        posx = (display_width - width) // 2
        posy = (display_height - height) // 2
        return f"{width}x{height}+{posx}+{posy}"

    # Menu adjust event.
    def __adjust_menubaropts(self, event):
        tab = self.__get_selected_tab()
        if tab is None:
            adjust_menu(self.menubar, "init")
        else:
            adjust_menu(self.menubar, tab.image.mode)


    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Tab Management
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    # Opens a tab and adds it to the end or to the specific position in the list of tabs. 
    def __open_tab(self, image, index=None):
        tab = self.__create_tab(image)
        if index is None or index >= self.tabmanager.index(END):
            self.tabmanager.add(tab.frame, text=tab.label)
            self.tabmanager.select(len(self.tabs)-1)
        else:
            self.tabmanager.insert(index, tab.frame, text=tab.label)
            self.tabmanager.select(index)
        tab.setname(self.tabmanager.select())

    # Creates a tab with the specified image. 
    def __create_tab(self, image):
        image_path = image.filename
        image_label = self.__get_imagelabel(image_path)
        imgframe = self.__create_image_frame(self.tabmanager)

        topbar_pathlabel = Label(imgframe.topbar, text=image_path)
        topbar_pathlabel.grid(row=0, column=0)

        topbar_scalelabel = Label(imgframe.topbar, text="100%", padx=20)
        topbar_scalelabel.grid(row=0, column=2)

        topbar_windowbutton = Button(imgframe.topbar, text="🗗", takefocus=False)
        topbar_windowbutton.config(bg="#dddddd", fg="black", font=("", 8), padx=10, pady=0)
        topbar_windowbutton.config(command=lambda:self.__show_window(topbar_windowbutton))
        topbar_windowbutton.grid(row=0, column=3)

        topbar_resizebutton = Button(imgframe.topbar, text="\u2b0c", takefocus=False)
        topbar_resizebutton.config(bg="#dddddd", fg="black", font=("", 8), padx=10, pady=0)
        topbar_resizebutton.config(command=lambda:self.zoom_inout((self.root.winfo_width()-30) / image.size[0]))
        topbar_resizebutton.grid(row=0, column=4)

        topbar_closebutton = Button(imgframe.topbar, text="\u274c", takefocus=False)
        topbar_closebutton.config(bg="#dd0000", fg="white", font=("", 8, "bold"), padx=10, pady=0)
        topbar_closebutton.config(command=self.__close_tab)
        topbar_closebutton.grid(row=0, column=5)

        rettab = Tab(self, imgframe.mainframe, imgframe.canvas, image_path, image_label, image, topbar_scalelabel)
        self.tabs.append(rettab)
        return rettab

    # Closes a tab and releases its resources.
    def __close_tab(self, tab=None):
        if tab == None:
            tab = self.__get_selected_tab()
        if tab.window is not None:
            tab.window.close()
        tab.image.close()
        tab.displayed_image.close()
        self.tabs.remove(tab)
        self.tabmanager.forget(tab.name)

    # Returns a currently selected tab.
    def __get_selected_tab(self):
        tabname = self.tabmanager.select()
        tab = None
        for tab in self.tabs:
            if tab.name == tabname:
                break
        return tab

    # Returns a unique label for the image with the given path.
    def __get_imagelabel(self, path):
        opened_files = [tb.label for tb in self.tabs]
        counter = 1
        imagename = path.split("/")[-1]
        imagelabel = imagename
        namebase, extension = imagename.split(".")
        while True:
            if imagelabel not in opened_files: break
            imagelabel = f"{namebase}({counter}).{extension}"
            counter += 1
        return imagelabel

    # Returns a unique internal non-disk path for the give infix and filename.
    def __get_internal_path(self, filename, infix):
        opened_paths = [tb.path for tb in self.tabs if tb.path.endswith("/"+filename)]
        counter = 1
        ispathtaken = True
        while ispathtaken:
            path = f"{self.internal_path_prefix}{infix}/{counter}/{filename}"
            ispathtaken = path in opened_paths
            counter += 1
        return path


    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Image Window 
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    # Creates and shows a window with an image.
    def __show_window(self, button):
        tab  = self.__get_selected_tab()
        if tab.window: return

        image_window = Toplevel(self.root)
        image_window.title(tab.path)
        image_window.wimage = tab.image.resize(1)
        image_window.assoc_but = button
        image_window.close = lambda: self.__close_window(tab)
        image_window.protocol("WM_DELETE_WINDOW", image_window.close)

        tab.window = image_window
        button.config(state=DISABLED)

        imgframe = self.__create_image_frame(image_window)
        imgframe.mainframe.pack(expand=1, fill=BOTH)
        image_window.canvas = imgframe.canvas

        scale_frame = Frame(imgframe.topbar, pady=10)
        scale_frame.grid(row=0, column=1)
        scale_label = Label(scale_frame, text="100%", padx= 10)
        scale_label.grid(row=0, column=1)

        scale_values = [0.1, 0.2 , 0.25, 0.50, 1, 1.5, 2]
        index = 4
        def zoom_in():
            nonlocal index
            if index + 1 < len(scale_values):
                index += 1
                scale_label.config(text=f"{int(scale_values[index]*100)}%")
                self.zoom_inout(scale_values[index], image_window)
        def zoom_out():
            nonlocal index
            if index - 1 >= 0:
                index -= 1
                scale_label.config(text=f"{int(scale_values[index]*100)}%")
                self.zoom_inout(scale_values[index], image_window)

        plus_button = Button(scale_frame, text="\u002b", takefocus=False)
        plus_button.config(bg="#444444", fg="white", font=("", 10, "bold"), padx=7)
        plus_button.config(command=zoom_in)
        plus_button.grid(row=0, column=2)

        minus_button = Button(scale_frame, text="\u2212", takefocus=False)
        minus_button.config(bg="#444444", fg="white", font=("", 10, "bold"), padx=7)
        minus_button.config(command=zoom_out)
        minus_button.grid(row=0, column=0)

        self.__draw_image_on_canvas(image_window.canvas, image_window.wimage)

    # Closes the window with the image and releases its resources.
    def __close_window(self, tab):
        tab.window.assoc_but.config(state=ACTIVE)
        tab.window.wimage.close()
        tab.window.destroy()
        tab.window = None

    # Draws the image on given canvas.
    def __draw_image_on_canvas(self, canvas, image):
        width, height = image.size
        img_converted = image.getphotoimage()
        canvas.delete("all")
        canvas.config(height=height, width=width)
        canvas.create_image((0,0), image=img_converted, anchor=NW)
        canvas.photo_copy = img_converted
        canvas.event_generate("<Configure>")
    

    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Other GUI Components
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def __create_image_frame(self, parentwidget):
        '''
        Creates an ImageFrame (frame with topbar and scrollabel canvas).

        Args:
            parentwidget (Tk, Toplevel, Notebook, Frame): Parent container widget.

        Returns:
            ImageFrame: Frame with topbar and canvas. It is namedtuple with components such as mainframe, topbar and canvas. 
        '''
        main_frame = Frame(parentwidget)

        topbar_frame = Frame(main_frame)
        topbar_frame.grid_columnconfigure(1, weight=1)
        topbar_frame.pack(side=TOP, fill=X)

        content_frame = Frame(main_frame)
        content_frame.pack(expand=True, fill=BOTH)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        canvas = Canvas(content_frame, highlightthickness=0)
        canvas.grid(row=0,column=0)

        y_scrollbar = ttk.Scrollbar(content_frame, orient=VERTICAL, command=canvas.yview)
        y_scrollbar.grid(row=0,column=1, sticky=NS)

        x_scrollbar = ttk.Scrollbar(content_frame, orient=HORIZONTAL, command=canvas.xview)
        x_scrollbar.grid(row=1,column=0, sticky=EW)

        canvas.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        return AppGui.ImageFrame(main_frame, topbar_frame, canvas)
    

    def __create_scale_entry(self, parentwidget, width, minval, maxval, resolution=1, labinterval=50, initval="0", label=""):
        '''
        Creates a ScaleEntry (combined scale and entry).

        Scale and Entry are connected so changing value in one of them causes change of value in the other. ScaleEntry.frame component has 
        a chgval_decor attribute. If chgval_decor is not None, it is called as a function at the end of the value change event execution.

        Args:
            parentwidget (Tk, Toplevel, Notebook, Frame): Parent container widget.
            width (int): Scale length in pixels.
            minval (float): Lower range value.
            maxval (float): Upper range value.
            resolution (float): Difference between successive values (step value).
            labinterval (float): Space between consecutive labels.
            initval (str): Initial value for Scale and Entry. The string should contain a number from the range 
            specified by minval and maxval.
            label (str): Label (title) for scale.

        Returns:
            ScaleEntry: Frame with combined scale and entry. It is namedtuple with components such as frame, scale and entry. 
        '''
        frame = Frame(parentwidget)
        frame.chgval_decor = None
        scale = Scale(frame, from_=minval, to=maxval, resolution=resolution, orient=HORIZONTAL)
        scale.config(length=width, tickinterval=labinterval, highlightthickness=0)
        scale.grid(row=1, column=0)
        entry = Entry(frame, width=5)
        entry.grid(row=1, column=1, padx=5)
        label = Label(frame, text=label)
        label.grid(row=0, column=0, sticky=W)

        entry.insert(0, initval)
        try: val = float(initval)
        except: return

        if minval <= val <= maxval:
            scale.set(val)

        def change_value(value):
            entry.delete(0, END)
            entry.insert(0, value)
            if frame.chgval_decor is not None: frame.chgval_decor()

        def check_value(event):
            try:
                val = float(entry.get())
                val = round(val / resolution) * resolution
            except:
                val = minval
            if val < minval:
                val = minval
            elif val > maxval:
                val = maxval
            scale.set(val)
            change_value(val)  

        scale.config(command=lambda val:change_value(str(val)))
        entry.bind("<FocusOut>", check_value)
        return AppGui.ScaleEntry(frame, scale, entry)


    def __create_apply_check_img_window(self, wtitle, addcanvas=False, numberofframes=1):
        '''
        Creates an ApplyCheckWindow (settings window with 3 buttons: Apply, Check, Cancel).

        Result is shown as a Toplevel object window which blocks others components of application. The window contains canvas 
        if the addcanvas flag is set to True. The window can contain any number of empty frames. 

        Args:
            wtitle (str): Window title.
            addcanvas (bool): A flag that determines whether the canvas will be added.
            numberofframes (int): Number of empty frames.

        Returns:
            ApplyCheckWindow: Toplevel window with 3 buttons: Apply, Check, Cancel. It is namedtuple with components such as window, 
            canvas, frames, applybut, checkbut, cancelbut. 
        '''
        window = Toplevel(self.root)
        window.title(wtitle)
        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)
        window.grab_set()

        def cancel_window():
            window.grab_release()
            window.destroy()
        window.protocol("WM_DELETE_WINDOW", cancel_window)
        window.close = cancel_window

        window_frame = Frame(window, padx=30, pady=10)
        window_frame.grid(row=0, column=0)

        canvas = None
        if addcanvas:
            canvas = Canvas(window_frame)
            canvas.grid(row=0, column=0)

        frames = []
        for frcounter in range(numberofframes):
            frame = Frame(window_frame, pady=10)
            frame.grid(row=frcounter+1, column=0, sticky=NSEW)
            frames.append(frame)

        buttons_frame = Frame(window_frame, pady=20)
        buttons_frame.grid(row=numberofframes+1, column=0, sticky=EW)
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons = []
        for index, butname in enumerate(["Apply", "Check", "Cancel"]):
            button = Button(buttons_frame, text=butname, padx=7, font=("", 10))
            button.grid(row=0, column=index+1, padx=5)
            buttons.append(button)
        buttons[2].config(command=cancel_window)
        return AppGui.ApplyCheckWindow(window, canvas, frames, *buttons)


    def __create_apply_img_window(self, wtitle, addcanvas=False, numberofframes=1):
        '''
        Creates an ApplyWindow (settings window with 2 buttons: Apply, Cancel).

        Result is shown as a Toplevel object window which blocks others components of application. The window contains canvas 
        if the addcanvas flag is set to True. The window can contain any number of empty frames. 

        Args:
            wtitle (str): Window title.
            addcanvas (bool): A flag that determines whether the canvas will be added.
            numberofframes (int): Number of empty frames.

        Returns:
            ApplyWindow: Toplevel window with 2 buttons: Apply, Cancel. It is namedtuple with components such as window, canvas, frames, 
            applybut, cancelbut. 
        '''
        win = self.__create_apply_check_img_window(wtitle, addcanvas, numberofframes)
        win.checkbut.destroy()
        return AppGui.ApplyWindow(win.window, win.canvas, win.frames, win.applybut, win.cancelbut)
        

    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Base Menu Functions
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def open_file(self):
        '''
        Displays the open file dialog and opens a file.
        '''
        file_types = (("All files", "*.*"), 
                    ("All images", "*.jpg;*.jpeg;*.jpe;*.png;*.tif;*.tiff;*.bmp;"), 
                    ("JPEG Images", "*.jpg;*.jpeg;*.jpe"),
                    ("PNG Images", "*.png"),
                    ("TIFF Images", "*.tif;*.tiff"),
                    ("BMP Images", "*.bmp"))
        filepath = filedialog.askopenfilename(filetypes=file_types)
        if filepath == "":
            return

        image = getimage(filepath)
        if image == None:
            messagebox.showwarning(title="Cannot open image", message="File does not exist or has unsupported format")
        elif(filepath in [tab.path for tab in self.tabs]):
            messagebox.showwarning(title="Cannot open image", message="File has already been opened")
        else:
            self.__open_tab(image)


    def save_file(self):
        '''
        Saves the selected file on disk.
        '''
        tab = self.__get_selected_tab()
        if tab.is_file_saved_on_disk:
            if messagebox.askyesno(title="Save file", message="Are you sure you want to save a file?"):
                tab.image.save(tab.image.filename)
        else:
            self.saveas_file()


    def saveas_file(self):
        '''
        Displays the 'save as' file dialog and saves the file on disk.
        '''
        tab = self.__get_selected_tab()
        filename = filedialog.asksaveasfilename(defaultextension=".png", 
                        filetypes= (("PNG Image", ".png"), ("JPEG Image", ".jpg"), 
                                    ("TIFF Image", ".tiff"), ("BMP Image", ".bmp")))
        if not filename:
            return
        tab.image.save(filename)
        if not tab.is_file_saved_on_disk:
            tab_index = self.tabmanager.index(tab.name)
            self.__close_tab(tab)
            image = getimage(filename)
            self.__open_tab(image, index=tab_index)
        

    def duplicate_img(self):
        '''
        Duplicates the selected image and opens the duplicate in new tab.
        '''
        tab = self.__get_selected_tab()
        filename = tab.path.split("/")[-1]
        duplicatepath = self.__get_internal_path(filename, "[duplicate]")
        image = tab.image.duplicate(duplicatepath)
        self.__open_tab(image)

    
    def convert_to(self, targetmode):
        '''
        Converts the selected image to given type.

        Args:
            targetmode (str): The string which represents image type.
        '''
        tab = self.__get_selected_tab()
        ret_image = tab.image.convert(targetmode)
        tab.redraw_image(ret_image)

    
    def invert_img(self):
        '''
        Inverts the selected image.
        '''
        tab = self.__get_selected_tab()
        ret_image = tab.image.negate()
        tab.redraw_image(ret_image)


    def zoom_inout(self, factor, window=None):
        '''
        Zooms in/out the selected image according to given factor.

        Args:
            factor (float): Resize factor.
            window (bool): A flag that determines whether the resizing will be applied to the image in the window (if the flag is True) 
            or to the image in the tab (if the flag is False).
        '''
        if not window:
            tab = self.__get_selected_tab()
            tab.displayed_image = tab.image.resize(factor)
            tab.image_scalefactor = factor
            tab.draw_image()
            tab.scalelabel.config(text=f"{int(factor*100)}%")
        else:
            resized_image = window.wimage.resize(factor)
            self.__draw_image_on_canvas(window.canvas, resized_image)


    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Thresholding
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def threshold_binary(self):
        '''
        Displays the binary thresholding window for the selected image.
        '''
        tab = self.__get_selected_tab()
        def draw_func(canvas, content_space, threshold):
            st_x, ed_y, ed_x, st_y = content_space
            return self.draw_function(canvas, (st_x, st_y), (threshold, st_y), (threshold, ed_y), (ed_x, ed_y))
        self.__thresholding(tab, "Binary thresholding", ["Threshold"], draw_func, tab.image.treshold_binary)


    def threshold_grayscale(self):
        '''
        Displays the window for thresholding with maintaining gray levels for the selected image.
        '''
        tab = self.__get_selected_tab()
        def draw_func(canvas, content_space, threshold):
            st_x, ed_y, ed_x, st_y = content_space
            return self.draw_function(canvas, (st_x, st_y), (threshold, st_y), (threshold, st_y-threshold+st_x), (ed_x, ed_y))
        self.__thresholding(tab, "Thresholding with grayscale", ["Threshold"], draw_func, tab.image.treshold_grayscale)


    def threshold_two(self):
        '''
        Displays the window for thresholding with two thresholds for the selected image.
        '''
        tab = self.__get_selected_tab()
        def check_thresholds(tshd1, tshd2):
            if tshd1 >= tshd2:
                messagebox.showinfo(title="Invalid values", message="First threshold must be less than second threshold")
                return False
            return True
        def draw_func(canvas, content_space, tshd1, tshd2):
            if check_thresholds(tshd1, tshd2):
                st_x, ed_y, ed_x, st_y = content_space
                return self.draw_function(canvas, (st_x, st_y), (tshd1, st_y), (tshd1, ed_y), (tshd2, ed_y), (tshd2, st_y), (ed_x, st_y))
        def threshold_func(tshd1, tshd2):
            if check_thresholds(tshd1, tshd2):
                return tab.image.treshold_two(tshd1, tshd2)
        self.__thresholding(tab, "Thresholding with two thresholds", ["First Threshold", "Second Threshold"], draw_func, threshold_func)


    def __thresholding(self, tab, title_pref, scales, draw_func, threshold_func):
        '''
        Displays a thresholding window for the given tab. 

        Args:
            tab (Tab): The tab with the image which will be processed.
            title_pref (str): Prefix for the title. The entire title consists of the prefix and the tab label.
            scales (list[str]): A list of strings representing threshold titles. The list is used to generate scales.
            draw_func (function(canv, contpoints, *args)): Function to draw the graph of the function. Function returns list of the lines 
            from which the graph of the function consists of.
                It should take 3 parameters:
                canv: a canvas on which the function will be drawn
                contpoins: a tuple with the points of rectangle that defines the drawing area. 
                It should be in the form (str_x, end_y, end_x, str_y)
                *args: any number of threshold y values.
            threshold_func (function(*args)) : Threshold function that takes threshold values as parameters
        '''
        title = f"{title_pref} - {tab.label}"
        sett_window = self.__create_apply_check_img_window(title, addcanvas=True, numberofframes=len(scales))

        img_M = tab.image.M
        hist = tab.image.histogram()
        cnv_width, cnv_height, xpad, ypad = img_M, img_M, 5, 5
        sett_window.canvas.config(height=cnv_height+ypad*2, width=cnv_width+xpad*2, highlightthickness=0)
        self.__draw_histogram_borders(sett_window.canvas, (xpad, ypad), (cnv_width+xpad, cnv_height+ypad))
        self.__draw_histogram(hist, sett_window.canvas, (xpad, cnv_height+ypad), cnv_height / max(hist), color="#aaaaaa")

        scale_objs = []
        for index, scalelabel in enumerate(scales):
            init_val = (index+1) * (tab.image.Lmax // (len(scales)+1))
            scale_fr = self.__create_scale_entry(sett_window.frames[index], 200, tab.image.Lmin, tab.image.Lmax, 
                                                initval=str(init_val), label=scalelabel)
            scale_fr.frame.grid(row=0, column=0)
            scale_objs.append(scale_fr.scale)

        treshold_func_lines = []
        def check_func():
            nonlocal treshold_func_lines
            for line in treshold_func_lines:
                sett_window.canvas.delete(line)
            dr_f_ret = draw_func(sett_window.canvas, (xpad, ypad, cnv_width+xpad, cnv_height+ypad), *[sc.get()+xpad for sc in scale_objs])
            if dr_f_ret:
                treshold_func_lines = dr_f_ret

        def apply_func():
            ret_image = threshold_func(*[sc.get() for sc in scale_objs])
            if ret_image:
                tab.redraw_image(ret_image)
                sett_window.window.close()

        check_func()
        sett_window.applybut.config(command=apply_func)
        sett_window.checkbut.config(command=check_func)


    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Segmentation
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def segmentation_thresholding(self):
        '''
        Displays the window for segmentation by thresholding for the selected image.
        '''
        tab = self.__get_selected_tab()
        # Segmentation graphical interface configuration
        sett_window = self.__create_apply_img_window(f"Segmentation by thresholding - {tab.label}", numberofframes=1)
        mainframe = sett_window.frames[0]
        mainframe.config(padx=15)
        visualization_frame = self.__create_image_frame(sett_window.window)
        visualization_frame.mainframe.grid(row=0, column=1)
        visualization_frame.mainframe.config(padx=10)

        global_label = Label(mainframe, text="Global", font=("", 12))
        global_label.grid(row=0, column=0, sticky=W)

        gl_manual_frame = Frame(mainframe, padx=10)
        gl_manual_frame.grid(row=1, column=0, sticky=W)

        gl_auto_frame = Frame(mainframe, padx=10)
        gl_auto_frame.grid(row=2, column=0, sticky=W)

        local_label = Label(mainframe, text="Local", font=("", 12))
        local_label.grid(row=3, column=0, sticky=W)

        lc_adapt_frame = Frame(mainframe, padx=10)
        lc_adapt_frame.grid(row=4, column=0, sticky=W)

        rb_gen = zip([0,1,2], ["Manual", "Automatic by the Otsu method", "Adaptive"], [gl_manual_frame, gl_auto_frame, lc_adapt_frame])
        threshold_code = IntVar()
        rbuts_threshold_opt = []
        for code, label, frame in rb_gen:
            rbutton = Radiobutton(frame, text=label, font=("", 11), variable=threshold_code, value=code)
            rbutton.grid(row=0, column=0, sticky=W, pady=3)
            rbuts_threshold_opt.append(rbutton)
        threshold_code.set(0)

        gl_manual_rbuts_frame = Frame(gl_manual_frame, padx=15)
        gl_manual_rbuts_frame.grid(row=1, column=0, sticky=W)
        threshold_manual_code = IntVar()
        rbuts_threshold_manual_opt = []
        for code, label in enumerate(["Binary", "With Grayscale", "With Two Thresholds"]):
            rbutton = Radiobutton(gl_manual_rbuts_frame, text=label, variable=threshold_manual_code, value=code)
            rbutton.grid(row=0, column=code)
            rbuts_threshold_manual_opt.append(rbutton)
        threshold_manual_code.set(0)

        glman_thsh_main = self.__create_scale_entry(gl_manual_frame, 200, tab.image.Lmin, tab.image.Lmax, initval=127, label="Threshold 1")
        glman_thsh_main.frame.grid(row=2, column=0)
        glman_thsh_main.frame.config(pady=5)
        glman_thsh_snd = self.__create_scale_entry(gl_manual_frame, 200, tab.image.Lmin, tab.image.Lmax, initval=127, label="Threshold 2")
        glman_thsh_snd.frame.grid(row=3, column=0)
        glman_thsh_snd.frame.config(pady=5)

        glauto_thsh_label = Label(gl_auto_frame, padx=5)
        glauto_thsh_label.grid(row=1, column=0)

        lc_adapt_rbuts_frame = Frame(lc_adapt_frame, padx=15)
        lc_adapt_rbuts_frame.grid(row=1, column=0, sticky=W)
        threshold_adapt_code = IntVar()
        rbuts_threshold_adapt_opt = []
        for code, label in enumerate(["Mean", "Gaussian"]):
            rbutton = Radiobutton(lc_adapt_rbuts_frame, text=label, variable=threshold_adapt_code, value=code)
            rbutton.grid(row=code+1, column=0, sticky=W)
            rbuts_threshold_adapt_opt.append(rbutton)
        threshold_adapt_code.set(0)

        # Mechanism for enabling and disabling segmentation radio buttons
        def applyState(state, *args):
            for widget in args:
                widget.config(state=state)

        def applyStates(states, *args):
            for state, widgets in zip(states, args):
                applyState(state, *widgets)

        def setWidgetsStates(states, wdgt_groups, extnd_funcs):
            applyStates(states, *wdgt_groups)
            for extnd_func in extnd_funcs:
                extnd_func() 

        def setManThshdState():
            state = DISABLED
            if  threshold_manual_code.get() == 2:
                state = NORMAL
            glman_thsh_snd.scale.config(state=state)
            glman_thsh_snd.entry.config(state=state)

        td_opt_elems = [rbuts_threshold_manual_opt + [glman_thsh_main.scale, glman_thsh_snd.scale, 
                        glman_thsh_main.entry, glman_thsh_snd.entry], 
                        [], 
                        rbuts_threshold_adapt_opt]
        td_opt_elems_disabled = []
        td_opt_elems_extd_func = [[setManThshdState], [], []]

        for rbut_index, rbut in enumerate(rbuts_threshold_opt):
            wdgt_disabled = []
            for opt_index, threshold_opt_elem in enumerate(td_opt_elems):  
                if rbut_index != opt_index:
                    wdgt_disabled += threshold_opt_elem
            td_opt_elems_disabled.append(wdgt_disabled)
            rbut.config(command=lambda:setWidgetsStates((NORMAL, DISABLED), 
                                                        (td_opt_elems[threshold_code.get()], 
                                                        td_opt_elems_disabled[threshold_code.get()]), 
                                                        td_opt_elems_extd_func[threshold_code.get()]))

        setWidgetsStates((NORMAL, DISABLED), (td_opt_elems[0], td_opt_elems_disabled[0]), td_opt_elems_extd_func[0])
        sett_window.window.thcodes = [threshold_code, threshold_manual_code, threshold_adapt_code]

        def setSubOptsFuncs(funcs_list):
            for fun in funcs_list: fun()
                
        threshold_manual_opt_funcs = [setManThshdState] 
        for rbut in rbuts_threshold_manual_opt:
            rbut.config(command=lambda: setSubOptsFuncs(threshold_manual_opt_funcs))

        threshold_adapt_opt_funcs = []
        for rbut in rbuts_threshold_adapt_opt:
            rbut.config(command=lambda: setSubOptsFuncs(threshold_adapt_opt_funcs))

        # Image computing and redrawing visualization image
        ret_image = None
        resize_factor = 1
        max_vwidth, max_vheight = 700, 600

        img_width, img_height = tab.image.size
        img_width_factor = max_vwidth / img_width
        img_height_factor = max_vheight / img_height
        if img_width_factor < 1 or img_height_factor < 1:
            resize_factor = min(img_width_factor, img_height_factor)
            
        
        otsu_thsh, otsu_image = tab.image.segmentation_threshold("otsu")
        glauto_thsh_label.config(text=f"Threshold: {str(otsu_thsh)}")

        def get_segmented_img():
            nonlocal ret_image, otsu_image
            opt_code = threshold_code.get()
            if opt_code == 0:
                subopt_code = threshold_manual_code.get()
                if subopt_code == 0:
                    ret_image = tab.image.segmentation_threshold("bin", glman_thsh_main.scale.get())[1]
                elif subopt_code == 1:
                    ret_image = tab.image.segmentation_threshold("gray", glman_thsh_main.scale.get())[1]
                elif subopt_code == 2:
                    ret_image = tab.image.segmentation_threshold("2th", glman_thsh_main.scale.get(), glman_thsh_snd.scale.get())[1]
            elif opt_code == 1:
                ret_image = otsu_image
            elif opt_code == 2:
                ret_image = tab.image.segmentation_threshold("adapt", adaptivemode=threshold_adapt_code.get())[1]
            return ret_image

        def redraw_image(event=None):
            visul_image = get_segmented_img()
            if resize_factor != 1:
                visul_image = visul_image.resize(resize_factor)
            self.__draw_image_on_canvas(visualization_frame.canvas, visul_image)

        redraw_image()

        for extd_func_list in td_opt_elems_extd_func:
            extd_func_list.append(redraw_image)

        threshold_manual_opt_funcs.append(redraw_image)
        threshold_adapt_opt_funcs.append(redraw_image)

        glman_thsh_main.scale.bind("<ButtonRelease-1>", redraw_image)
        glman_thsh_main.scale.bind("<Left>", redraw_image)
        glman_thsh_main.scale.bind("<Right>", redraw_image)
        glman_thsh_snd.scale.bind("<ButtonRelease-1>", redraw_image)
        glman_thsh_snd.scale.bind("<Left>", redraw_image)
        glman_thsh_snd.scale.bind("<Right>", redraw_image)
        glman_thsh_main.entry.bind("<FocusOut>", redraw_image, add="+")
        glman_thsh_snd.entry.bind("<FocusOut>", redraw_image, add="+")

        def apply_func():
            get_segmented_img()
            tab.redraw_image(ret_image)
            sett_window.window.close()
        sett_window.applybut.config(command=apply_func)
        

    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Arithmetic and logic operations
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def add_const(self):
        '''
        Displays the window for adding a constant to the selected image.
        '''
        window = self.__math_operation("Add integer", img_operands=1, number_operands=1)
        def apply_func():
            validation_ret = self.__validate_math_int(window, "add int")
            if validation_ret is None: return
            tab, number = validation_ret
            ret_image = tab.image.add_int(number, window.checkboxvar.get())
            tab.redraw_image(ret_image)
            window.window.close()
        window.applybut.config(command=apply_func)


    def multiply_by_const(self):
        '''
        Displays the window for multiplying the selected image by constant.
        '''
        window = self.__math_operation("Multiply by integer", img_operands=1, number_operands=1)
        def apply_func():
            validation_ret = self.__validate_math_int(window, "multiply int")
            if validation_ret is None: return
            tab, number = validation_ret
            ret_image = tab.image.multiply_int(number, window.checkboxvar.get())
            tab.redraw_image(ret_image)
            window.window.close()
        window.applybut.config(command=apply_func)


    def divide_by_const(self):
        '''
        Displays the window for dividing the selected image by constant.
        '''
        window = self.__math_operation("Divide by integer", img_operands=1, number_operands=1)
        def apply_func():
            validation_ret = self.__validate_math_int(window, "divide int")
            if validation_ret is None: return
            tab, number = validation_ret
            if number == 0:
                messagebox.showinfo(title="Invalid number", message="Number cannot be zero!")
                return
            ret_image = tab.image.divide_int(number, window.checkboxvar.get())
            tab.redraw_image(ret_image)
            window.window.close()
        window.applybut.config(command=apply_func)


    def add_images(self):
        '''
        Displays the images adding window.
        '''
        window = self.__math_operation("Add images", img_operands=2, number_operands=0, isresultname=True)
        def apply_func():
            tabs = self.__validate_math_images(window, "add images")
            if tabs is None: return
            filepath = self.__validate_math_resultname(window.resultname.get())
            if filepath is None: return
            tab1, tab2 = tabs
            ret_image = tab1.image.add_images(tab2.image, window.checkboxvar.get())
            ret_image.filename = filepath
            self.__open_tab(ret_image)
            window.window.close()
        window.applybut.config(command=apply_func)


    def subtract_images(self):
        '''
        Displays the images absolute subtraction window.
        '''
        window = self.__math_operation("Subtract images", img_operands=2, number_operands=0, isresultname=True, ischeckbox=False)
        def apply_func():
            tabs = self.__validate_math_images(window, "subtract images")
            if tabs is None: return
            filepath = self.__validate_math_resultname(window.resultname.get())
            if filepath is None: return
            tab1, tab2 = tabs
            ret_image = tab1.image.subtract_images(tab2.image)
            ret_image.filename = filepath
            self.__open_tab(ret_image)
            window.window.close()
        window.applybut.config(command=apply_func)


    def logic_not(self):
        '''
        Displays the window for logical NOT operation for the selected image.
        '''
        window = self.__math_operation("NOT", img_operands=1, number_operands=0, ischeckbox=False)
        def apply_func():
            validation_ret = self.__validate_math_operation(window.images[0].get(), "logic not")
            if validation_ret is None: return
            tab = validation_ret
            ret_image = tab.image.logic_not()
            tab.redraw_image(ret_image)
            window.window.close()
        window.applybut.config(command=apply_func)


    def logic_and(self):
        '''
        Displays the window for logical AND operation for two images.
        '''
        window = self.__math_operation("AND", img_operands=2, number_operands=0, isresultname=True, ischeckbox=False)
        def apply_func():
            tabs = self.__validate_math_images(window, "logic and")
            if tabs is None: return
            filepath = self.__validate_math_resultname(window.resultname.get())
            if filepath is None: return
            tab1, tab2 = tabs
            ret_image = tab1.image.logic_and(tab2.image)
            ret_image.filename = filepath
            self.__open_tab(ret_image)
            window.window.close()
        window.applybut.config(command=apply_func)


    def logic_or(self):
        '''
        Displays the window for logical OR operation for two images.
        '''
        window = self.__math_operation("OR", img_operands=2, number_operands=0, isresultname=True, ischeckbox=False)
        def apply_func():
            tabs = self.__validate_math_images(window, "logic or")
            if tabs is None: return
            filepath = self.__validate_math_resultname(window.resultname.get())
            if filepath is None: return
            tab1, tab2 = tabs
            ret_image = tab1.image.logic_or(tab2.image)
            ret_image.filename = filepath
            self.__open_tab(ret_image)
            window.window.close()
        window.applybut.config(command=apply_func)


    def logic_xor(self):
        '''
        Displays the window for logical XOR operation for two images.
        '''
        window = self.__math_operation("XOR", img_operands=2, number_operands=0, isresultname=True, ischeckbox=False)
        def apply_func():
            tabs = self.__validate_math_images(window, "logic xor")
            if tabs is None: return
            filepath = self.__validate_math_resultname(window.resultname.get())
            if filepath is None: return
            tab1, tab2 = tabs
            ret_image = tab1.image.logic_xor(tab2.image)
            ret_image.filename = filepath
            self.__open_tab(ret_image)
            window.window.close()
        window.applybut.config(command=apply_func)
    
    # Validates the chosen file name for result image
    def __validate_math_resultname(self, filename):
        if filename == "":
            messagebox.showinfo(title="No result file name", message="Enter the name for result file!")
            return
        elif filename.split(".")[-1].lower() not in ["jpg", "jpeg", "jpe", "png", "tif", "tiff", "bmp"]:
            filename += ".png"
        filepath = self.__get_internal_path(filename, "[math]")
        return filepath

    # Validates the operands for math operation performed on an image and an integer
    def __validate_math_int(self, window, operation):
        imagetab = self.__validate_math_operation(window.images[0].get(), operation)
        if imagetab is None: return
        for num in window.numbers:
            try:
                number = float(num.get())
            except:
                messagebox.showinfo(title="Invalid number", message="Input is not a number!")
                return
            intnumber = int(number)
            if intnumber != number:
                messagebox.showinfo(title="Invalid number", message="Number must be an integer!")
                return
        return (imagetab, intnumber)

    # Validates the operands for math operation performed on images
    def __validate_math_images(self, window, operation):
        tabs = []
        for image in window.images:
            validate_ret = self.__validate_math_operation(image.get(), operation)
            if validate_ret is None: return
            tabs.append(validate_ret)
        if len(tabs) == 0: return
        imagesize = tabs[0].image.size
        imagemode = tabs[0].image.mode
        for tab in tabs:
            if imagesize != tab.image.size:
                messagebox.showinfo(title="Invalid images", message="Images must have the same size!")
                return
            if imagemode != tab.image.mode:
                messagebox.showinfo(title="Invalid images", message="Images must be the same type!")
                return
        return tabs

    # Validates the image as the operand for math operation and returns the tab with the image
    def __validate_math_operation(self, image, operation):
        if image == "":
            messagebox.showinfo(title="No file selected", message="Select file!")
            return
        for tab in self.tabs:
            if tab.label == image:
                break
        imagemode_options = supported_menu_options(tab.image.mode)
        if operation not in imagemode_options:
            messagebox.showinfo(title="Unsupported operation", message="File does not support this operation!")
            return
        return tab


    def __math_operation(self, title, img_operands, number_operands, isresultname=False, ischeckbox=True):
        '''
        Displays the window for math operation. The window should be supplemented with buttons handling.

        Args:
            title (str): Window title.
            img_operands (int): Number of selection lists for selecting images.
            number_operands (int): Number of entry fields for entering integers.
            isresultname (bool): A flag that determines whether the entry field for result file name will be added.
            ischeckbox (bool): A flag that determines whether the checkbox for oversaturation will be added.
        
        Returns:
            MathOpWindow: Toplevel window for math operations with lists of images and entry fields for numbers. It is namedtuple with 
            components such as window, images, numbers, resultname, checkboxvar, applybut, cancelbut.
        '''
        framenum = img_operands + number_operands + isresultname + ischeckbox
        sett_window = self.__create_apply_img_window(title, numberofframes=framenum)

        images = []
        number_entries = []
        resultname_entry = None
        checkboxvar = None
        files = [tab.label for tab in self.tabs]
        frame_index = 0

        img_opd_label_text = "Image" if img_operands == 1 else "Image 1"
        for index in range(img_operands):
            img_opd_label = Label(sett_window.frames[frame_index], text=img_opd_label_text)
            img_opd_label_text = f"Image {index+1}"
            images.append(StringVar())
            img_opd = OptionMenu(sett_window.frames[frame_index], images[index], *files)
            img_opd.config(width=30, highlightthickness=0)
            img_opd_label.grid(row=0, column=0, sticky=W)
            img_opd.grid(row=1, column=0, sticky=W)
            frame_index += 1
        number_opd_label_text = "Number" if img_operands == 1 else "Number 1"
        for index in range(number_operands):
            number_opd_label = Label(sett_window.frames[frame_index], text=number_opd_label_text)
            number_opd_label_text = f"Number {index+1}"
            number_opd = Entry(sett_window.frames[frame_index], width=15)
            number_entries.append(number_opd)
            number_opd_label.grid(row=0, column=0, sticky=W)
            number_opd.grid(row=1, column=0, sticky=W)
            frame_index += 1
        if isresultname:
            resultname_entry_label = Label(sett_window.frames[frame_index], text="Result name")
            resultname_entry = Entry(sett_window.frames[frame_index], width=30)
            resultname_entry_label.grid(row=0, column=0, sticky=W)
            resultname_entry.grid(row=1, column=0, sticky=W)
            frame_index += 1
        if ischeckbox:
            checkboxvar = BooleanVar()
            checkbox = Checkbutton(sett_window.frames[frame_index], variable=checkboxvar, text="oversaturation")
            checkbox.select()
            checkbox.grid(row=0, column=0, sticky=W)
        return AppGui.MathOpWindow(sett_window.window, images, number_entries, resultname_entry, 
                                    checkboxvar, sett_window.applybut, sett_window.cancelbut)

    
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Convolution operations
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def smooth_img(self):
        '''
        Displays the image smoothing window for the selected image.
        '''
        tab = self.__get_selected_tab()
        masks = ["\u23a11 1 1\u23a4\n\u23a21 1 1\u23a5\n\u23a31 1 1\u23a6", 
                "\u23a11 1 1\u23a4\n\u23a21 k 1\u23a5\n\u23a31 1 1\u23a6", 
                "\u23a11 2 1\u23a4\n\u23a22 4 2\u23a5\n\u23a31 2 1\u23a6"]
        ngbd_window = self.__neighborhood_opeartion(tab, "Smooth", masks_labels=masks)
        entry_scale = self.__create_scale_entry(ngbd_window.window.frames[0], 200, 0, 100, resolution=1, labinterval=20, initval="2", 
                                                label="Parameter k")
        entry_scale.frame.grid(row=2, column=0)

        def apply_func():
            mask_index = ngbd_window.maskcode.get()
            bordertype = ngbd_window.bordertypecode.get()
            bordertype_pvalue = ngbd_window.bordertypeparam.scale.get()
            if mask_index == 0:
                ret_image = tab.image.smooth_avarage(bordertype, bordertype_pvalue)
            elif mask_index == 1:
                param_k = entry_scale.scale.get()
                ret_image = tab.image.smooth_weighted_avarage(param_k, bordertype, bordertype_pvalue)
            elif mask_index == 2:
                ret_image = tab.image.smooth_gaussian(bordertype, bordertype_pvalue)
            tab.redraw_image(ret_image)
            ngbd_window.window.window.close()
        ngbd_window.window.applybut.config(command=apply_func)


    def sharpen_img(self):
        '''
        Displays the image sharpening window for the selected image.
        '''
        tab = self.__get_selected_tab()
        masks = ["\u23a1 0 -1  0\u23a4\n\u23a2-1  4 -1\u23a5\n\u23a3 0 -1  0\u23a6", 
                "\u23a1-1 -1 -1\u23a4\n\u23a2-1  8 -1\u23a5\n\u23a3-1 -1 -1\u23a6", 
                "\u23a1 1 -2  1\u23a4\n\u23a2-2  4 -2\u23a5\n\u23a3 1 -2  1\u23a6"]
        ngbd_window = self.__neighborhood_opeartion(tab, "Sharpen", masks_labels=masks)

        def apply_func():
            mask_index = ngbd_window.maskcode.get()
            bordertype = ngbd_window.bordertypecode.get()
            bordertype_pvalue = ngbd_window.bordertypeparam.scale.get()
            ret_image = tab.image.sharpen_laplacian(mask_index, bordertype, bordertype_pvalue)
            tab.redraw_image(ret_image)
            ngbd_window.window.window.close()
        ngbd_window.window.applybut.config(command=apply_func)  

    
    def medianblur_img(self):
        '''
        Displays the window for median blurring for the selected image.
        '''
        tab = self.__get_selected_tab()
        masks = ["3x3", "5x5", "7x7", "9x9"]
        ngbd_window = self.__neighborhood_opeartion(tab, "Median blur", masks_labels=masks)
        entry_scale = self.__create_scale_entry(ngbd_window.window.frames[0], 150, 3, 9, resolution=2, labinterval=2, initval="3", 
                                                label="Mask size")
        entry_scale.frame.grid(row=2, column=0) 

        def change_rbut_select():
            mask_size = entry_scale.scale.get()
            ngbd_window.maskcode.set((mask_size - 3) // 2)
        entry_scale.frame.chgval_decor = change_rbut_select

        def change_scale():
            mask_size = (ngbd_window.maskcode.get() * 2) + 3
            entry_scale.scale.set(mask_size)
        for rbut in ngbd_window.maskrbuts:
            rbut.config(command=change_scale)

        def apply_func():
            mask_size = (ngbd_window.maskcode.get() * 2) + 3
            bordertype = ngbd_window.bordertypecode.get()
            bordertype_pvalue = ngbd_window.bordertypeparam.scale.get()
            ret_image = tab.image.median_blur(mask_size, bordertype, bordertype_pvalue)
            tab.redraw_image(ret_image)
            ngbd_window.window.window.close()
        ngbd_window.window.applybut.config(command=apply_func) 


    def edgedetection_sobel_mask(self):
        '''
        Displays the window for edge detection using Sobel masks for the selected image.
        '''
        tab = self.__get_selected_tab()
        masks = ["W  ", "NW", "N  ", "NE", "E  ", "ES", "S  ", "WS"]
        ngbd_window = self.__neighborhood_opeartion(tab, "Edge detection with Sobel mask", masks_title="Directions", masks_labels=masks)

        def apply_func():
            mask_code = masks[ngbd_window.maskcode.get()].strip()
            bordertype = ngbd_window.bordertypecode.get()
            bordertype_pvalue = ngbd_window.bordertypeparam.scale.get()
            ret_image = tab.image.edgedetection_Sobel_mask(mask_code, bordertype, bordertype_pvalue)
            tab.redraw_image(ret_image)
            ngbd_window.window.window.close()
        ngbd_window.window.applybut.config(command=apply_func)


    def edgedetection_operators(self):
        '''
        Displays the window for edge detection using operators for the selected image. 
        There are 3 operators for choose from: Sobel, Prewitt, Canny.
        '''
        tab = self.__get_selected_tab()
        operators = ["Sobel", "Prewitt", "Canny"]
        ngbd_window = self.__neighborhood_opeartion(tab, "Edge detection with operator", masks_title="Operators", masks_labels=operators)

        Lmin, Lmax = tab.image.Lmin, tab.image.Lmax
        treshold1_scale = self.__create_scale_entry(ngbd_window.window.frames[0], 200, Lmin, Lmax, resolution=1, labinterval=50, 
                                                    initval="50", label="Threshold 1")
        treshold2_scale = self.__create_scale_entry(ngbd_window.window.frames[0], 200, Lmin, Lmax, resolution=1, labinterval=50, 
                                                    initval="150", label="Threshold 2")
        treshold1_scale.frame.grid(row=2, column=0)
        treshold2_scale.frame.grid(row=3, column=0)

        def change_scale_state():
            if ngbd_window.maskcode.get() == 2:
                treshold1_scale.scale.config(state=ACTIVE)
                treshold2_scale.scale.config(state=ACTIVE)
                treshold1_scale.entry.config(state=NORMAL)
                treshold2_scale.entry.config(state=NORMAL)
            else:
                treshold1_scale.scale.config(state=DISABLED)
                treshold2_scale.scale.config(state=DISABLED)
                treshold1_scale.entry.config(state=DISABLED)
                treshold2_scale.entry.config(state=DISABLED)
        for rbut in ngbd_window.maskrbuts:
            rbut.config(command=change_scale_state)
        change_scale_state()

        def apply_func():
            operator_index = ngbd_window.maskcode.get()
            bordertype = ngbd_window.bordertypecode.get()
            bordertype_pvalue = ngbd_window.bordertypeparam.scale.get()
            if operator_index == 0:
                ret_image = tab.image.edgedetection_Sobel_operator(bordertype, bordertype_pvalue)
            elif operator_index == 1:
                ret_image = tab.image.edgedetection_Prewitt_operator(bordertype, bordertype_pvalue)
            elif operator_index == 2:
                tshd1, tshd2 = treshold1_scale.scale.get(), treshold2_scale.scale.get()
                if tshd1 < tshd2:
                    ret_image = tab.image.edgedetection_Canny_operator(tshd1, tshd2, bordertype, bordertype_pvalue)
                else:
                    messagebox.showinfo(title="Invalid values", message="Fisrt threshold must be less than second threshold")
                    return
            tab.redraw_image(ret_image)
            ngbd_window.window.window.close()
        ngbd_window.window.applybut.config(command=apply_func)


    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Morphology
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def morphology_erode(self):
        '''
        Displays the window for erosion morphology operation for the selected image.
        '''
        tab = self.__get_selected_tab()
        self.__morpholofy_operation(tab, "Erosion", tab.image.morph_erode)


    def morphology_dilate(self):
        '''
        Displays the window for dilation morphology operation for the selected image.
        '''
        tab = self.__get_selected_tab()
        self.__morpholofy_operation(tab, "Dilation", tab.image.morph_dilate)


    def morphology_open(self):
        '''
        Displays the window for opening morphology operation for the selected image.
        '''
        tab = self.__get_selected_tab()
        self.__morpholofy_operation(tab, "Opening", tab.image.morph_open)


    def morphology_close(self):
        '''
        Displays the window for closing morphology operation for the selected image.
        '''
        tab = self.__get_selected_tab()
        self.__morpholofy_operation(tab, "Closing", tab.image.morph_close)


    def __morpholofy_operation(self, tab, title_pref, morph_function):
        '''
        Displays the morphology operation window for the selected image.

        Args:
            tab (Tab): The tab with the image which will be processed.
            title_pref (str): Prefix for the title. The entire title consists of the prefix and the tab label.
            morph_function (str): The morphology operation function that will be executed.
        '''
        morph_window = self.__neighborhood_opeartion(tab, title_pref, masks_title="Structuring element shape", 
                                                    masks_labels=["Cross", "Square"])
        def apply_func():
            mask_code = morph_window.maskcode.get()
            bordertype = morph_window.bordertypecode.get()
            bordertype_pvalue = morph_window.bordertypeparam.scale.get()
            ret_image = morph_function(mask_code, bordertype, bordertype_pvalue)
            tab.redraw_image(ret_image)
            morph_window.window.window.close()
        morph_window.window.applybut.config(command=apply_func)


    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Neighborhood operations
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def __neighborhood_opeartion(self, tab, title_pref, masks_title="Masks", masks_labels=None, disabled_bordertypes=None):
        '''
        Displays the window for neighborhood operation. The window should be supplemented with apply button handling.

        Args:
            tab (Tab): The tab with the image which will be processed.
            title_pref (str): Prefix for the title. The entire title consists of the prefix and the tab label.
            masks_title (str): The label that will be displayed as the title of the masks section.
            masks_labels (list[str]): List of mask labels. It determines the number of mask radio buttons.
            disabled_bordertypes (list[bool]): List specifying which radio buttons will be either active and disabled. If the value in 
            some index is False the radio button in the same index is active.

        Returns:
            NeighbourhoodOpWindow: Toplevel window for neighbourhood operations. It is namedtuple with components such as window, 
            maskrbuts, maskcode, bordertypecode, bordertypeparam.
        '''
        title = f"{title_pref} - {tab.label}"
        sett_window = self.__create_apply_img_window(title, addcanvas=False, numberofframes=2)
        sett_window.window.mask_code = IntVar()
        sett_window.window.bordertype_code = StringVar()

        mask_rbuts = []
        mask_code = sett_window.window.mask_code
        bordertype_code = sett_window.window.bordertype_code

        if masks_labels is not None:
            label = Label(sett_window.frames[0], text=masks_title)
            label.grid(row=0, column=0, sticky=W)
            mask_frame = Frame(sett_window.frames[0], pady=5)
            mask_frame.grid(row=1, column=0)

            column_index = 0
            row_index = 0
            for index, mask_label in enumerate(masks_labels):
                rbut = Radiobutton(mask_frame, variable=mask_code, value=index, text=mask_label, padx=10, font=("Helvetica", 12))
                rbut.grid(row=row_index, column=column_index)
                mask_rbuts.append(rbut)
                column_index += 1
                if column_index >= 3:
                    column_index = 0
                    row_index += 1
            mask_code.set(0)

        minval, maxval = tab.image.Lmin, tab.image.Lmax
        bordertype_param = self.__get_bordertypes_list(sett_window.frames[1], bordertype_code, (minval, maxval), disabled_bordertypes)
        return AppGui.NeighbourhoodOpWindow(sett_window, mask_rbuts, mask_code, bordertype_code, bordertype_param)
    
    
    def __get_bordertypes_list(self, parentframe, bordertype_code, border_param_range, disabled=None):
        '''
        Generates radio buttons list for choosing border type for neighbourhood operations.

        Args:
            parentframe (Frame): Parent container Frame.
            bordertype_code (StringVar): Variable to hold the value of the selected radio button.
            border_param_range (tuple): A tuple (lower_r, upper_r) specifying the range of parameter values.
            disabled (list[bool]): List specifying which radio buttons will be either active and disabled. If the value in 
            some index is False the radio button in the same index is active.

        Returns:
            EntryScale: Scale and entry field for the value of the parameter.
        '''
        bordertypes = {"const": "Fill margins with value", 
                        "wrap": "Wrap margins",
                        "reflect": "Reflect margins",
                        "const_result": "Don't count margins and fill result with value"}

        label = Label(parentframe, text="Margin type", pady=5)
        label.grid(row=0, column=0, sticky=W)

        if disabled is None:
            disabled = [False] * len(bordertypes)
        elif len(disabled) < len(bordertypes):
            disabled = disabled + [False]*(len(bordertypes)-len(disabled))

        select_rbut = True
        for index, bordertype in enumerate(bordertypes.keys()):
            rbut = Radiobutton(parentframe, variable=bordertype_code, value=bordertype, text=bordertypes[bordertype], pady=5)
            rbut.grid(row=index+1, column=0, sticky=W)
            if disabled[index]:
                rbut.config(state=DISABLED)
            elif select_rbut:
                bordertype_code.set(bordertype)
                select_rbut = False

        minval, maxval = border_param_range
        entry_scale = self.__create_scale_entry(parentframe, 200, minval, maxval , resolution=1, labinterval=50, initval=str(minval), label="Margin type parameter")
        entry_scale.frame.grid(row=index+2, column=0)
        entry_scale.frame.config(pady=5)
        return entry_scale

    
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Image analysis
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def analyze_img(self):
        '''
        Displays the window for analyzing the selected image.
        '''
        tab = self.__get_selected_tab()
        sett_window = self.__create_apply_check_img_window("Image analysis", addcanvas=False, numberofframes=2)

        features_names = ["Area", "Circuit", "Shape factor W1", "Shape factor W2", "Shape factor W3", "Shape factor W9", 
                                "Solidity (W10)", "Equivalent Diameter (W11)", "Moment M1", "Moment M2", "Moment M3"]
        features_variables = [BooleanVar() for x in range(len(features_names))]

        features_label = Label(sett_window.frames[0], text="Features")
        features_label.grid(row=0, column=0, sticky=W)
        for index in range(0, len(features_names)):
            checkbut = Checkbutton(sett_window.frames[0], text=features_names[index], variable=features_variables[index])
            checkbut.grid(row=index+1, column=0, sticky=W)

        def checkall():
            for var in features_variables:
                var.set(True)

        def getfilename():
            nonlocal filename
            filename_ret = filedialog.asksaveasfilename()
            if filename_ret:
                if len(filename_ret) < 5 or filename_ret[-4:] != ".csv":
                    filename_ret += ".csv"
                filename_label.config(text=filename_ret.split("/")[-1])
                filename = filename_ret

        filename = ""
        filename_desc_label = Label(sett_window.frames[1], text="Save result as:", width=20, anchor=W)
        filename_label = Label(sett_window.frames[1], width=30, anchor=W)
        filename_desc_label.grid(row=0, column=0, sticky=W)
        filename_label.grid(row=1, column=0, sticky=W)
        filename_button = Button(sett_window.frames[1], text="...", padx=5, command=getfilename)
        filename_button.grid(row=0, column=0, sticky=E)

        def apply_func():
            features_selected = [feature_var.get() for feature_var in features_variables]
            if not filename:
                messagebox.showinfo(title="No result file name", message="Enter the name for result file!")
                return
            analysis_data_lines = tab.image.analyze(*features_selected)
            headers_line_list = [f_name for i, f_name in enumerate(features_names) if features_selected[i]]
            headers_line = ",".join(headers_line_list) + "\n"
            resultfile = open(filename, "w")
            resultfile.writelines([headers_line] + analysis_data_lines)
            resultfile.close()
            sett_window.window.close()
            messagebox.showinfo(title="Analysis has been done", message="Analysis file has been created!")

        checkall()
        sett_window.checkbut.config(text="Check All")
        sett_window.checkbut.config(command=checkall)
        sett_window.applybut.config(text="Compute")
        sett_window.applybut.config(command=apply_func)

        
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Histogram stretching
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def hist_linear_stretch(self):
        '''
        Displays the histogram stretching window for the selected image.
        '''
        tab = self.__get_selected_tab()
        histogram = tab.image.histogram()
        Lmax = tab.image.Lmax
        ret_image = None

        title = f"Linear stretching - {tab.label}"
        sett_window = self.__create_apply_check_img_window(title, addcanvas=True, numberofframes=2)

        cnv_width, cnv_height, xpad, ypad = len(histogram), 200, 5, 5
        sett_window.canvas.config(height=cnv_height+ypad*2, width=cnv_width+xpad*2, highlightthickness=0)
        self.draw_histogram_changes_sketch([0]*tab.image.M, histogram, sett_window.canvas, (xpad, ypad, cnv_width+xpad, cnv_height+ypad))

        lowrng_scale = self.__create_scale_entry(sett_window.frames[1], 200, 0, Lmax, initval=str(0), label="Lower range")
        uprng_scale = self.__create_scale_entry(sett_window.frames[1], 200, 0, Lmax, initval=str(Lmax), label="Upper range")

        stretchoption = BooleanVar()
        checkbtnvalue = BooleanVar()
        def choose_stretch_option():
            if stretchoption.get():
                cut_values_checkbox.config(state=ACTIVE)
                for elem in [lowrng_scale.scale, lowrng_scale.entry, uprng_scale.scale, uprng_scale.entry]:
                    elem.config(state=DISABLED)
            else:
                cut_values_checkbox.config(state=DISABLED)
                cut_values_checkbox.deselect()
                lowrng_scale.scale.config(state=ACTIVE)
                uprng_scale.scale.config(state=ACTIVE)
                lowrng_scale.entry.config(state=NORMAL)
                uprng_scale.entry.config(state=NORMAL)

        minmax_stretch_rbutton = Radiobutton(sett_window.frames[0], text="Stretching from min to max", pady=10)
        minmax_stretch_rbutton.config(variable=stretchoption, value=True, command=choose_stretch_option)
        minmax_stretch_rbutton.select()
        cut_values_checkbox = Checkbutton(sett_window.frames[0], text="Cut off 5% values from both sides", variable=checkbtnvalue)
        sett_window.frames[0].grid_columnconfigure(0, weight=1)
        minmax_stretch_rbutton.grid(row=0, column=0, sticky=W)
        cut_values_checkbox .grid(row=1, column=0, sticky=EW)

        custom_stretch_rbutton = Radiobutton(sett_window.frames[1], text="Stretching with custom values [a, b]", pady=10)
        custom_stretch_rbutton.config(variable=stretchoption, value=False, command=choose_stretch_option)
        for elem in [lowrng_scale.scale, lowrng_scale.entry, uprng_scale.scale, uprng_scale.entry]:
            elem.config(state=DISABLED)
        custom_stretch_rbutton.grid(row=0, column=0, sticky=W)
        lowrng_scale.frame.grid(row=1, column=0, sticky=W, pady=5)
        uprng_scale.frame.grid(row=2, column=0, sticky=W, pady=5)

        def stretch_func():
            nonlocal ret_image
            if stretchoption.get():
                ret_image = tab.image.hist_linear_stretch(cutoff=checkbtnvalue.get())
            else:
                lowrange = lowrng_scale.scale.get()
                uprange = uprng_scale.scale.get()
                if lowrange >= uprange:
                    messagebox.showinfo(title="Invalid values", message="Lower range must be less than upper range")
                    return
                ret_image = tab.image.hist_linear_stretch(rangevalues=(lowrange, uprange))
        
        def check_func():
            stretch_func()
            ret_histogram = ret_image.histogram()
            self.draw_histogram_changes_sketch(histogram, ret_histogram, sett_window.canvas, (xpad, ypad, cnv_width+xpad, cnv_height+ypad))

        def apply_func():
            if ret_image is None:
                stretch_func()
            tab.redraw_image(ret_image)
            sett_window.window.close()

        sett_window.applybut.config(command=apply_func)
        sett_window.checkbut.config(command=check_func)


    def hist_gamma_stretch(self):
        '''
        Displays the window for gamma stretching for the selected image.
        '''
        tab = self.__get_selected_tab()
        histogram = tab.image.histogram()
        ret_image = None

        title = f"Gamma stretching - {tab.label}"
        sett_window = self.__create_apply_check_img_window(title, addcanvas=True, numberofframes=1)

        cnv_width, cnv_height, xpad, ypad = len(histogram), 200, 5, 5
        sett_window.canvas.config(height=cnv_height+ypad*2, width=cnv_width+xpad*2, highlightthickness=0)
        self.draw_histogram_changes_sketch([0]*tab.image.M, histogram, sett_window.canvas, (xpad, ypad, cnv_width+xpad, cnv_height+ypad))

        gamma_scale = self.__create_scale_entry(sett_window.frames[0], 200, 0, 5, resolution=0.01, labinterval=1, initval=str(1), label="Gamma")
        def blockbutts_func():
            if gamma_scale.scale.get() == 0:
                sett_window.applybut.config(state=DISABLED)
                sett_window.checkbut.config(state=DISABLED)
            else:
                sett_window.applybut.config(state=ACTIVE)
                sett_window.checkbut.config(state=ACTIVE)
        gamma_scale.frame.chgval_decor = blockbutts_func
        gamma_scale.frame.grid(row=0, column=0, sticky=W)

        def stretch_func():
            nonlocal ret_image
            ret_image = tab.image.hist_gamma_stretch(gamma_scale.scale.get())
        
        def check_func():
            stretch_func()
            ret_histogram = ret_image.histogram()
            self.draw_histogram_changes_sketch(histogram, ret_histogram, sett_window.canvas, (xpad, ypad, cnv_width+xpad, cnv_height+ypad))

        def apply_func():
            if ret_image is None:
                stretch_func()
            tab.redraw_image(ret_image)
            sett_window.window.close()

        sett_window.applybut.config(command=apply_func)
        sett_window.checkbut.config(command=check_func)
        

    def hist_equalization(self):
        '''
        Displays the window for histogram equalization for the selected image.
        '''
        tab = self.__get_selected_tab()
        ret_image = tab.image.hist_equalization()
        histogram = tab.image.histogram()
        ret_img_histogram = ret_image.histogram()

        title = f"Equalization - {tab.label}"
        sett_window = self.__create_apply_img_window(title, addcanvas=True, numberofframes=0)

        cnv_width, cnv_height, xpad, ypad = len(histogram), 200, 5, 5
        sett_window.canvas.config(height=cnv_height+ypad*2, width=cnv_width+xpad*2, highlightthickness=0)
        self.draw_histogram_changes_sketch(histogram, ret_img_histogram, sett_window.canvas, (xpad, ypad, cnv_width+xpad, cnv_height+ypad))

        def apply_func():
            tab.redraw_image(ret_image)
            sett_window.window.close()
        sett_window.applybut.config(command=apply_func)


    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Visualization drawing
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def draw_function(self, canvas, *args):
        '''
        Draws the function based on the specified points on the given canvas.

        Args:
            canvas (Canvas): Canvas on which the function will be drawn.
            *args: Points (x,y) of the function.

        Returns:
            list: List of lines that the function consist of.
        '''
        func_lines = []
        st_x, st_y = args[0]
        for idx in range(1, len(args)):
            ed_x, ed_y = args[idx]
            if st_x == ed_x:
                func_lines.append(canvas.create_line(st_x, st_y, ed_x, ed_y, fill="black", width=1, dash=(5,1)))
            else:
                func_lines.append(canvas.create_line(st_x, st_y, ed_x, ed_y, fill="black", width=1))
            st_x, st_y = ed_x, ed_y
        return func_lines


    def draw_histogram_changes_sketch(self, old_hist, new_hist, canvas, content_space):
        '''
        Draws an image with the old and new histograms superimposed.

        Args:
            old_hist (list): The histogram that will be drawn with a lighter color underneath.
            new_hist (list): The histogram that will be drawn with a darker color on top.
            canvas (Canvas): The canvas on which the function will be drawn.
            content_space (tuple): The tuple with the points of rectangle that defines the drawing area. 
            It should be in the form (left_x, top_y, right_x, bottom_y).
        '''
        lf_x, tp_y, rg_x, bt_y = content_space
        hists_max = max(max(old_hist), max(new_hist))
        canvas.delete("all")
        self.__draw_histogram_borders(canvas, (lf_x, tp_y), (rg_x, bt_y))
        self.__draw_histogram(old_hist, canvas, (lf_x, bt_y), (bt_y - tp_y) / hists_max, color="#aaaaaa")
        self.__draw_histogram(new_hist, canvas, (lf_x, bt_y), (bt_y - tp_y) / hists_max)


    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Profile
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def show_profile(self):
        '''
        Displays the window for profile plotting for the selected image.
        '''
        #Obtains the tab with the image and prepares the skeleton of the settings window
        tab = self.__get_selected_tab()
        window_title = f"Profile - {tab.label}"
        sett_window = self.__create_apply_img_window(window_title, numberofframes=3)

        #Width and height of the image
        image_width, image_height = tab.image.size 
        #Color value for the drawn profile lines
        line_color = "#edd51c"
        #Size of the points 
        pt_size = 3
        #Size of the lines 
        ln_size = 3 
        #List of the drawn objects. The first element is a tuple (point) and the next ones are (line, point)
        drawed_points = []
        #List of profile breakpoints
        profile_points = []
        
        #Creates and adjusts the GUI elements for the image size information section
        img_size_str = f"Image size:  {image_width} x {image_height}"
        img_size_label = Label(sett_window.frames[0], text=img_size_str)
        img_size_label.grid(row=0, column=0)
        #Creates and adjusts the GUI elements for the color pick section for profile lines
        line_color_label = Label(sett_window.frames[1], text=f"Line color: {line_color}")
        line_color_label.grid(row=0, column=0, sticky=W)
        line_color_but = Button(sett_window.frames[1], text="Change color")
        line_color_but.grid(row=1, column=0, pady=5, sticky=W)
        #Creates and adjusts the GUI elements for coordinates entries section
        point_section_label = Label(sett_window.frames[2], text="Point")
        point_section_label.grid(row=0, column=0, columnspan=4, sticky=W)
        x_coord_label = Label(sett_window.frames[2], text="x")
        x_coord_label.grid(row=1, column=0, pady=10)
        x_coord_entry = Entry(sett_window.frames[2], width=5)
        x_coord_entry.grid(row=1, column=1, pady=10)
        y_coord_label = Label(sett_window.frames[2], text="y")
        y_coord_label.grid(row=1, column=2, pady=10)
        y_coord_entry = Entry(sett_window.frames[2], width=5)
        y_coord_entry.grid(row=1, column=3, pady=10)
        #Creates and adjusts the buttons for adding and deleting lines functionality
        addpt_but = Button(sett_window.frames[2], text="Add", width=10)
        addpt_but.grid(row=2, column=0, columnspan=2, padx=10)
        delpt_but = Button(sett_window.frames[2], text="Delete", width=10, state=DISABLED)
        delpt_but.grid(row=2, column=2, columnspan=2, padx=10)

        #Creates and prepares the skeleton of the image window
        image_window = Toplevel(sett_window.window)
        image_window.title(window_title)
        img_frame = self.__create_image_frame(image_window)
        img_frame.mainframe.pack(expand=1, fill=BOTH)
        #Draws the image
        self.__draw_image_on_canvas(img_frame.canvas, tab.image)
        #Sets the top bar
        imgwin_coord_label = Label(img_frame.topbar, text=" x: -  y: -")
        imgwin_coord_label.grid(row=0, column=0)

        #The settings window size
        sett_width, sett_height = 270, 320
        #The image window size
        imgfr_width, imgfr_height = 500, 500
        #Sets the position of the settings window and the image window on the screen
        win_x = (self.root.winfo_screenwidth() - (sett_width + imgfr_width)) // 2
        win_y = (self.root.winfo_screenheight() - sett_height) // 4
        sett_window.window.geometry(f"{sett_width}x{sett_height}+{win_x}+{win_y}")
        image_window.geometry(f"{imgfr_width}x{imgfr_height}+{win_x+sett_width+2}+{win_y}")

        #Function that disables the delete button when there is no point of profile and enables it otherwise
        set_delbut_state = lambda: delpt_but.config(state=NORMAL) if len(profile_points) else delpt_but.config(state=DISABLED)

        #Function that draws the point (and the line) on the image. Created objects are added to the list
        def draw_point(x, y):
            point = img_frame.canvas.create_oval(x-pt_size, y-pt_size, x+pt_size, y+pt_size, fill=line_color)
            if len(drawed_points) == 0:
                drawed_points.append((point,))
            else:
                prev_x, prev_y = img_frame.canvas.coords(drawed_points[-1][-1])[:2]
                line = img_frame.canvas.create_line(prev_x+pt_size, prev_y+pt_size, x, y, fill=line_color, width=ln_size)
                drawed_points.append((line, point))

        #Function that changes the color of the profile lines
        def change_color():
            nonlocal line_color
            #Shows window for choosing color
            color = colorchooser.askcolor(color="#edd51c", title="Choose profile line color", parent=sett_window.window)[1]
            if color is not None:
                line_color = color
                line_color_label.config(text=f"Line Color: {line_color}")
                #Redraws the profile lines with new color
                for pt_ln in drawed_points:
                    for obj in pt_ln:
                        img_frame.canvas.delete(obj)
                drawed_points.clear()
                for pt_x, pt_y in profile_points:
                    draw_point(pt_x, image_height - pt_y - 1) 
        #Assigns the change_color function to the corresponding button          
        line_color_but.config(command=change_color)

        #Function that updates the top bar of the image window with information 
        # about the coordinates of the mouse pointer position
        def show_mouse_coords(event):
            cnv = img_frame.canvas
            x = int(cnv.canvasx(event.x))
            y = int(image_height - cnv.canvasy(event.y) - 1)
            imgwin_coord_label.config(text=f" x: {x}  y: {y}")
        #Adjusts the behavior and appearance of the mouse pointer when hovering over an image
        img_frame.canvas.bind("<Motion>", show_mouse_coords)
        img_frame.canvas.bind("<Leave>", lambda event: imgwin_coord_label.config(text=f" x: -  y: -"))
        img_frame.canvas.config(cursor="tcross")

        #Function to add profile breakpoint by clicking the mouse button
        def add_point_event(event):
            cnv = img_frame.canvas
            #Gets coordinates
            x = int(cnv.canvasx(event.x))
            y = int(cnv.canvasy(event.y))
            #If the point is the same as the previous point then do not add this point
            if len(profile_points) > 0 and profile_points[-1] == (x, image_height - y - 1):
                return
            #Updates the list of profile breakpoints
            profile_points.append((x, image_height - y - 1))
            #Draws the point (and the line) on the image
            draw_point(x, y)
            set_delbut_state()

        #Function to add profile breakpoint by clicking the "Add" button
        def add_point_command():
            #Gets coordinates
            x = x_coord_entry.get()
            y = y_coord_entry.get()
            #Checks if inputs are numbers
            try:
                x = float(x)
                y = float(y)
            except:
                messagebox.showinfo(title="Invalid coordinate value", message="The coordinate must be a number", 
                                    parent=sett_window.window)
                return
            #Converts coordinates to integers
            x, y = int(x), int(y)
            #Checks if coordinates are in range
            if not ((0 <= x < image_width) and (0 <= y < image_height)):
                messagebox.showinfo(title="Invalid coordinate value", message="The coordinate value is out of range", 
                                    parent=sett_window.window)
                return
            #If the point is the same as the previous point then do not add this point
            if len(profile_points) > 0 and profile_points[-1] == (x, y):
                return
            #Updates the list of profile breakpoints
            profile_points.append((x, y))
            #Draws the point (and the line) on the image
            draw_point(x, image_height - y - 1)
            set_delbut_state()

        #Function to delete the last profile breakpoint by clicking the "Delete" button
        def delete_point():
            profile_points.pop()
            for obj in drawed_points[-1]:
                img_frame.canvas.delete(obj)
            drawed_points.pop()
            set_delbut_state()

        #Assigns functions to the corresponding buttons and events
        addpt_but.config(command=add_point_command)
        img_frame.canvas.bind("<Button-1>", add_point_event)
        delpt_but.config(command=delete_point)

        #Function that plotting the profile graph
        def plot():
            #Plotting can only be done if there are at least two points (one line)
            if len(profile_points) >= 2:
                #Prepares window with the profile lines drawn on the image
                img_window = Toplevel(self.root)
                img_window.title(window_title)
                img_area = self.__create_image_frame(img_window)
                img_area.mainframe.pack(expand=1, fill=BOTH)
                img_cnv = img_area.canvas
                self.__draw_image_on_canvas(img_cnv, tab.image)
                pnt_x, pnt_y = profile_points[0]
                pnt_y = image_height - pnt_y - 1
                prev_pnt = img_cnv.create_oval(pnt_x-pt_size, pnt_y-pt_size, pnt_x+pt_size, pnt_y+pt_size, fill=line_color)
                for pnt_x, pnt_y in profile_points[1:]:
                    pnt_y = image_height - pnt_y - 1
                    prev_x, prev_y = img_cnv.coords(prev_pnt)[:2]
                    img_cnv.create_line(prev_x+pt_size, prev_y+pt_size, pnt_x, pnt_y, fill=line_color, width=ln_size)
                    prev_pnt = img_cnv.create_oval(pnt_x-pt_size, pnt_y-pt_size, pnt_x+pt_size, pnt_y+pt_size, fill=line_color)
                #Prepares window for the profile graph
                plot_window = Toplevel(self.root)
                plot_window.title(window_title)
                #Calls the function for plotting profile graph
                plot_profile(profile_points, tab.image, plot_window)
                sett_window.window.close()
            else:
               messagebox.showinfo(title="Too few points", message="Not enough points have been given") 
        #Assigns plotting function to the corresponding button
        sett_window.applybut.config(text="Plot Profile", command=plot)
    

    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Histogram
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    
    def show_histogram(self):
        '''
        Displays the histogram window for the selected image.
        '''
        tab = self.__get_selected_tab()
        histogram = tab.image.histogram()
        hist_window = Toplevel()
        hist_window.title(f"Histogram - {tab.label}")

        hist_stat = Frame(hist_window, pady=20)
        hist_stat.grid(row=2, column=0)
        label_min = Label(hist_stat, padx=15, pady=5, width=10)
        label_max = Label(hist_stat, padx=15, pady=5, width=10)
        label_curr_value = Label(hist_stat, text="value: -", padx=15, pady=5, width=10)
        label_curr_count = Label(hist_stat, text="count: -", padx=15, pady=5, width=10)

        hist_window.label_hist_currvalue = label_curr_value
        hist_window.label_hist_currcount = label_curr_count

        label_min.grid(row=0, column=0)
        label_max.grid(row=0, column=1)
        label_curr_value.grid(row=1, column=0)
        label_curr_count.grid(row=1, column=1)

        if len(tab.image.channels) == 1:
            hist_window.grid_rowconfigure(0, weight=1)
            hist_window.grid_columnconfigure(0, weight=1)
            hist_canvas = self.__generate_histogram_image(hist_window, histogram)
            hist_canvas.grid(row=0, column=0) 
            hist_max = max(histogram)
            hist_min = min(histogram)
            label_min.config(text=f"min: {hist_min}")
            label_max.config(text=f"max: {hist_max}")
        else:
            hist_window.grid_rowconfigure(1, weight=1)
            hist_window.grid_columnconfigure(0, weight=1)
            topbar = Frame(hist_window, pady=15)
            topbar.grid(row=0, column=0)
            canvases = []
            stats = []

            radiobut_index_prev = 0
            radiobut_index = IntVar()
            def change_hist():
                nonlocal radiobut_index_prev, radiobut_index, label_min, label_max
                canvases[radiobut_index_prev].grid_forget()
                canvases[radiobut_index.get()].grid(row=1, column=0)
                new_min = stats[radiobut_index.get()]["min"]
                new_max = stats[radiobut_index.get()]["max"]
                label_min.config(text=f"min: {new_min}")
                label_max.config(text=f"max: {new_max}")
                radiobut_index_prev = radiobut_index.get()

            for index, hist_channel_name in enumerate(tab.image.channels):
                rbut = Radiobutton(topbar, text=hist_channel_name, variable=radiobut_index, value=index, command=change_hist, padx=20)
                rbut.grid(row=0, column=index)
                if(index == 0):
                    rbut.select()

            hist_colors = tab.image.guicolor_repr
            for index, hist_channel in enumerate(histogram):
                canvases.append(self.__generate_histogram_image(hist_window, hist_channel, hist_colors[index]))
                hist_max = max(hist_channel)
                hist_min = min(hist_channel)
                stats.append({})
                stats[index]["min"] = hist_min
                stats[index]["max"] = hist_max

            canvases[0].grid(row=1, column=0)
            start_min = stats[0]["min"]
            start_max = stats[0]["max"]
            label_min.config(text=f"min: {start_min}")
            label_max.config(text=f"max: {start_max}")
            

    def __generate_histogram_image(self, parentwindow, histogram, color="black"):
        '''
        Generates canvas with histogram.

        Args:
            parentwindow (Toplevel, Frame): Parent container widget.
            histogram (list[int]): List representing image histogram (one channel).
            color (str): String representing the color of the histogram bars.
        
        Returns:
            Canvas: Histogram.
        '''
        hist_M = len(histogram)
        hist_max = max(histogram)

        hist_content_height = 450
        tpad, rpad, bpad, lpad,  = (20, 20, 30, 60)
        line_width = round(150 / hist_M) + 1
        line_height_unit = hist_content_height / hist_max

        width = lpad + (hist_M * line_width) + rpad
        height = tpad + hist_content_height + bpad
        canvas = Canvas(parentwindow, width=width, height=height, highlightthickness=0)

        self.__draw_histogram_borders(canvas, (lpad-1, tpad), (width-rpad-1, height-bpad))
        canvas.create_text(width-rpad-(line_width//2), height-bpad+6, anchor=N, text=str(hist_M-1), font=("", 8))
        canvas.create_text(lpad+(line_width//2), height-bpad+6, anchor=N, text="0", font=("", 8))

        auxline_unit_min = round(hist_max / 9)
        self.__draw_histogram_auxlines(canvas, (lpad-1, height-bpad, width-rpad-1), line_height_unit, auxline_unit_min, hist_max)
        self.__draw_histogram(histogram, canvas, (lpad, height-bpad), line_height_unit, line_width, color)

        if hasattr(parentwindow, "label_hist_currvalue") and hasattr(parentwindow, "label_hist_currcount"):
            def show_hist_value(event):
                x = event.x
                y = event.y
                if lpad <= x <= width-rpad and tpad <= y <= height-bpad:
                    h_value = (x - lpad) // line_width
                    if 0 <= h_value < hist_M:
                        parentwindow.label_hist_currvalue.config(text=f"value: {h_value}")
                        parentwindow.label_hist_currcount.config(text=f"count: {histogram[h_value]}")
                else:
                    parentwindow.label_hist_currvalue.config(text="value: -")
                    parentwindow.label_hist_currcount.config(text="count: -")

            canvas.bind("<Motion>", show_hist_value)
        return canvas


    def __draw_histogram_borders(self, canvas, startpoint, endpoint):
        '''
        Draws the borders of the histogram.

        Args:
            canvas (Canvas): Canvas on which the histogram borders will be drawn.
            startpoint (tuple): The tuple with the coordinates of the top-left corner of drawing area. 
            It should be in the form (left_x, top_y).
            endpoint (tuple): The tuple with the coordinates of the bottom-right corner of drawing area. 
            It should be in the form (right_x, bottom_y).
        '''
        start_x, start_y = startpoint
        end_x, end_y = endpoint
        canvas.create_line(start_x, start_y, start_x, end_y, fill="#dddddd", width=1)
        canvas.create_line(end_x, start_y, end_x, end_y, fill="#dddddd", width=1)
        canvas.create_line(start_x, end_y, end_x, end_y, fill="#dddddd", width=1)
        canvas.create_line(start_x, start_y, end_x, start_y, fill="#dddddd", width=1)


    def __draw_histogram_auxlines(self, canvas, coordinates, ln_height_unit, auxln_min_unit, maxval):
        '''
        Draws the auxiliary lines of the histogram.

        Args:
            canvas (Canvas): Canvas on which the histogram auxiliary lines will be drawn.
            coordinates (tuple): The tuple with the coordinates needed to draw the lines. 
            It should be in the form (left_x, bottom_y, right_x).
            ln_height_unit (float): Line height unit. It tells how many pixels a unit of value in the histogram should have.
            auxln_min_unit (int): The minimum value by which successive auxiliary lines will differ.
            maxval (int): The maximum histogram value.
        '''
        auxline_unit_base = 1
        while auxln_min_unit / auxline_unit_base > 10:
            auxline_unit_base *= 10
        auxline_unit = ceil(auxln_min_unit / auxline_unit_base) * auxline_unit_base
        auxline_value = auxline_unit
        start_x, start_y, end_x = coordinates
        while auxline_value <= maxval - (auxline_unit // 4):
            auxline_label = auxline_value
            auxline_y_shift = round(ln_height_unit* auxline_value)
            auxline_y = start_y - auxline_y_shift
            canvas.create_line(start_x, auxline_y, end_x, auxline_y, fill="#dddddd", width=1)
            canvas.create_text(start_x-5, auxline_y, anchor=E, text=str(auxline_label), font=("", 8))
            auxline_value += auxline_unit


    def __draw_histogram(self, histogram, canvas, coordinates, ln_height_unit, ln_width=1, color="black"):
        '''
        Draws the histogram bars.

        Args:
            histogram (list[int]): List representing image histogram (one channel).
            canvas (Canvas): Canvas on which the histogram bars will be drawn.
            coordinates (tuple): The tuple with the coordinates needed to draw the histogram bars. 
            It should be in the form (left_x, bottom_y).
            ln_height_unit (float): Line height unit. It tells how many pixels a unit of value in the histogram should have.
            ln_width (int): The width of the histogram bar in pixels.
            color (str): String representing the color of the histogram bars.
        '''
        start_x, start_y, end_x, end_y = coordinates + (None, None)
        start_x += ceil(ln_width // 2) - 1
        for hist_value in histogram:
            end_x = start_x
            end_y = start_y - round(ln_height_unit * hist_value)
            canvas.create_line(start_x, start_y, end_x, end_y, fill=color, width=ln_width)
            start_x += ln_width   



class Tab:
    '''
    A class that represents a tab with a top bar and a scrollable image area.
    '''
    def __init__(self, app, frame, canvas, path, label, image, scalelabel):
        self.app = app
        self.frame = frame
        self.canvas = canvas
        self.scalelabel = scalelabel
        self.path = path
        self.label = label
        self.image = image
        self.image_scalefactor = 1
        self.displayed_image = self.image.resize(self.image_scalefactor)
        self.window = None
        self.draw_image()
        if self.image.filename.startswith(app.internal_path_prefix):
            self.is_file_saved_on_disk = False
        else:
            self.is_file_saved_on_disk = True
        
    def setname(self, name):
        self.name = name
    
    def draw_image(self):
        width, height = self.displayed_image.size
        img_converted = self.displayed_image.getphotoimage()
        self.canvas.delete("all")
        self.canvas.config(height=height, width=width)
        self.canvas.create_image((0,0), image=img_converted, anchor=NW)
        self.canvas.photo_copy = img_converted
        self.canvas.event_generate("<Configure>")
    
    def redraw_image(self, image):
        if self.image.mode != image.mode:
            adjust_menu(self.app.menubar, image.mode)
        self.image = image
        self.displayed_image = self.image.resize(self.image_scalefactor)
        if self.window is not None:
            self.window.close()
            self.window = None
        self.draw_image()


if __name__ == "__main__":
    AppGui()

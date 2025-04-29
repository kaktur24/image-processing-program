from tkinter import *

#////////////////////////////////
# Creation and adjustment of menu
#////////////////////////////////
def prep_menu(app):
    '''
    Creates a menu and sets the buttons to their initial state.

    Args:
        app (AppGui): Root application for Menu.

    Returns:
        Menu: Application main menu.
    '''
    menubar = Menu(app.root)
    _create_menu(app, menubar)
    adjust_menu(menubar, "init")
    return menubar


# Creates a menu (using recursion function) according to the initialization scheme.
def _create_menu(app, rootmenu):
    menu_schema = _init_menu_schema(app)
    for opt in menu_schema:
        _create_submenu(rootmenu, opt, menu_schema[opt])   


# Creates recursively a submenu according to the initialization scheme.
def _create_submenu(parentmenu, opt_name, schema_dict):
    option_keys = list(schema_dict.keys())
    if option_keys == ["command"]:
        parentmenu.add_command(label=opt_name, command=schema_dict["command"])
    else:
        submenu = Menu(parentmenu, tearoff=0)
        parentmenu.add_cascade(label=opt_name, menu=submenu)
        for opt in option_keys:
            _create_submenu(submenu, opt, schema_dict[opt])


def adjust_menu(menu, mode):
    '''
    Sets the menu buttons to either active or disabled state depending on given mode.

    Args:
        menu (Menu): Root menu.
        mode (str): String representing image type or value "init".
    '''
    _adjust_menu(menu, _enabled_menu_options(mode))


# Sets recursively the menu buttons to either active or disabled state according to list of enabled options.
def _adjust_menu(menu_object, enabled_opts, path=""):
    all_options_disabled = True
    for index in range(0, menu_object.index(END)+1):
        opt_type = menu_object.type(index)
        if opt_type in ["command", "cascade"]:
            opt_label = menu_object.entrycget(index, "label")
            opt_path = f"{path}>{opt_label}"
            if opt_type == "cascade":
                opt_submenu_name = menu_object.entrycget(index, "menu")
                opt_children = menu_object.winfo_children()
                for opt_child in opt_children:
                    if str(opt_child) == opt_submenu_name:
                        opt_submenu = opt_child
                        break
                is_submenu_disabled = _adjust_menu(opt_submenu, enabled_opts, opt_path)
                if is_submenu_disabled:
                    menu_object.entryconfig(index, state=DISABLED)
                else:
                    menu_object.entryconfig(index, state=ACTIVE)
                    all_options_disabled = False
            elif opt_type == "command" and opt_path in enabled_opts:
                menu_object.entryconfig(index, state=ACTIVE)
                all_options_disabled = False
            else:
                menu_object.entryconfig(index, state=DISABLED)
    return all_options_disabled


#/////////////////////
# Menu schema
#/////////////////////

# Function _init_menu_schema returns a menu schema as a dictionary. 
# Parameter app is an application which is a source for menu buttons actions.
def _init_menu_schema(app):
    return {
            "File":{
                "Open ...":{"command":app.open_file},
                "Save":{"command":app.save_file},
                "Save as":{"command":app.saveas_file}
            },
            "Image":{
                "Duplicate":{"command":app.duplicate_img},
                "Convert ...":{
                    "Grayscale to Binary":{"command":lambda: app.convert_to("B")},
                    "Binary to Grayscale":{"command":lambda: app.convert_to("GS")},
                    "RGB to Grayscale":{"command":lambda: app.convert_to("GS")}
                },
                "Zoom in/out":{
                    "10%":{"command":lambda:app.zoom_inout(0.1)},
                    "20%":{"command":lambda:app.zoom_inout(0.2)},
                    "25%":{"command":lambda:app.zoom_inout(0.25)},
                    "50%":{"command":lambda:app.zoom_inout(0.5)},
                    "100%":{"command":lambda:app.zoom_inout(1)},
                    "150%":{"command":lambda:app.zoom_inout(1.5)},
                    "200%":{"command":lambda:app.zoom_inout(2)}
                },
                "Invert":{"command":app.invert_img},
                "Histogram":{"command":app.show_histogram},
                "Profile":{"command":app.show_profile},
                "Analyze Image":{"command":app.analyze_img}
            },
            "Transform":{
                "Thresholding":{
                    "Binary thresholding":{"command":app.threshold_binary},
                    "Thresholding with grayscale":{"command":app.threshold_grayscale},
                    "Thresholding with two thresholds":{"command":app.threshold_two}
                },
                "Segmentation":{
                    "Thresholding":{"command":app.segmentation_thresholding},
                },
                "Smooth":{
                    "with Mask":{"command":app.smooth_img},
                    "Median blur":{"command":app.medianblur_img}
                },
                "Edge detection":{
                    "with Mask":{"command":app.sharpen_img},
                    "Sobel's direction mask":{"command":app.edgedetection_sobel_mask},
                    "Operator":{"command":app.edgedetection_operators}
                },
                "Morphology":{
                    "Erode":{"command":app.morphology_erode},
                    "Dilate":{"command":app.morphology_dilate},
                    "Open":{"command":app.morphology_open},
                    "Close":{"command":app.morphology_close}
                },
                "Math":{
                    "Add...":{"command":app.add_const},
                    "Multiply...":{"command":app.multiply_by_const},
                    "Divide...":{"command":app.divide_by_const},
                },
                "Image Calculator":{
                    "Add":{"command":app.add_images},
                    "Difference":{"command":app.subtract_images},
                    "NOT":{"command":app.logic_not},
                    "AND":{"command":app.logic_and},
                    "OR":{"command":app.logic_or},
                    "XOR":{"command":app.logic_xor}
                },
                "Histogram transformation":{
                    "Linear stretching":{"command":app.hist_linear_stretch},
                    "Gamma stretching":{"command":app.hist_gamma_stretch},
                    "Equalization":{"command":app.hist_equalization}
                }
            }
        }


#//////////////////////////////
# Options availability schemes
#//////////////////////////////
def _enabled_menu_options(mode):
    '''
    Returns a list of enabled options for given mode according to active options schema.

    Args:
        mode (str): String representing image type or value "init".

    Returns:
        list[str]: List of enabled options.
    '''
    options = _ACTIVE_OPTS["always"].copy()
    if mode == "init":
        return options

    for opt in _ACTIVE_OPTS["all"]:
        options.append(opt) 
        
    for opt in _ACTIVE_OPTS[mode]:
        options.append(opt)
    return options


def supported_menu_options(mode):
    '''
    Returns a list of supported options for given mode according to supported options schema.

    Args:
        mode (str): String representing image type.

    Returns:
        list[str]: List of supported options.
    '''
    return [opt for opt in _SUPPORTED_OTPS.keys() if mode in _SUPPORTED_OTPS[opt]]


# Active options schema
_ACTIVE_OPTS = {
    "always" : [">File>Open ..."],
    "all" : [">File>Save", 
            ">File>Save as", 
            ">Image>Duplicate", 
            ">Image>Zoom in/out>10%", 
            ">Image>Zoom in/out>20%", 
            ">Image>Zoom in/out>25%", 
            ">Image>Zoom in/out>50%", 
            ">Image>Zoom in/out>100%", 
            ">Image>Zoom in/out>150%", 
            ">Image>Zoom in/out>200%", 
            ">Image>Histogram",
            ">Image>Profile", 
            ">Transform>Math>Add...", 
            ">Transform>Math>Multiply...", 
            ">Transform>Math>Divide...", 
            ">Transform>Image Calculator>Add", 
            ">Transform>Image Calculator>Difference",
            ">Transform>Image Calculator>NOT", 
            ">Transform>Image Calculator>AND", 
            ">Transform>Image Calculator>OR", 
            ">Transform>Image Calculator>XOR",],
    "RGB" : [">Image>Convert ...>RGB to Grayscale",
            ">Transform>Smooth>with Mask", 
            ">Transform>Smooth>Median blur",
            ">Transform>Edge detection>with Mask",
            ">Transform>Edge detection>Sobel's direction mask",
            ">Transform>Edge detection>Operator"],
    "GS" : [">Image>Invert",
            ">Image>Convert ...>Grayscale to Binary", 
            ">Image>Analyze Image", 
            ">Transform>Thresholding>Binary thresholding", 
            ">Transform>Thresholding>Thresholding with grayscale",
            ">Transform>Thresholding>Thresholding with two thresholds",
            ">Transform>Segmentation>Thresholding",
            ">Transform>Smooth>with Mask", 
            ">Transform>Smooth>Median blur",
            ">Transform>Edge detection>with Mask",
            ">Transform>Edge detection>Sobel's direction mask",
            ">Transform>Edge detection>Operator",
            ">Transform>Histogram transformation>Linear stretching", 
            ">Transform>Histogram transformation>Gamma stretching", 
            ">Transform>Histogram transformation>Equalization"],
    "B" : [">Image>Convert ...>Binary to Grayscale",
            ">Image>Analyze Image",
            ">Transform>Morphology>Erode", 
            ">Transform>Morphology>Dilate", 
            ">Transform>Morphology>Open", 
            ">Transform>Morphology>Close"]
}


# Supported options schema
_SUPPORTED_OTPS =  {
        "add int": ("GS"),
        "multiply int": ("GS"),
        "divide int": ("GS"),
        "add images": ("GS", "B"),
        "subtract images": ("GS", "B"),
        "logic not": ("GS", "B"),
        "logic and": ("GS", "B"),
        "logic or": ("GS", "B"),
        "logic xor": ("GS", "B"),
}
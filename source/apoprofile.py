import tkinter as tk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


def plot_profile(points, image, rootwindow):
    '''
    Draws a profile graph based on the given breakpoint list and displays the graph window.

    Args:
        points (list): List of profile breakpoints. The elements in the list should be of the form (x, y).
        image (ImageRGB/ImageGrayscale): Source image.
        rootwindow (Toplevel/Tk): Root window for the profile graph.
    '''
    #A list containing each profile point
    profile_points = []
    #A list of the x coordinates of the breakpoints as distance from the origin
    line_break_points = [0]
    #Line start point - (x1, y1)
    #Line end point - (x2, y2)
    x1, y1 = points[0]
    for x2, y2 in points[1:]:  #Do for each line in profile...
        #Temporary list for points of the processed line  
        line_points = []
        #Executes if the line is a vertical line
        if x1 == x2:
            line_points = [(x1, y) for y in range(y1, y2, (y2-y1)//abs(y2-y1))] 
        #Executes if the line is a horizontal line
        elif y1 == y2:
            line_points = [(x, y1) for x in range(x1, x2, (x2-x1)//abs(x2-x1))]
        #Executed if the line is neither vertical nor horizontal
        else:
            #Formula for a linear function -> y = a*x + b
            a = (y2 - y1) / (x2 - x1)  #Parameter a
            b = y2 - a * x2  #Parameter b
            #If the condition is true, treat the y coordinate as an argument
            if abs(a) > 1:
                for y in range(y1, y2, (y2-y1)//abs(y2-y1)):
                    x = round((y - b) / a)
                    line_points.append((x, y))
            #Otherwise, treat the x coordinate as an argument
            else:
                for x in range(x1, x2, (x2-x1)//abs(x2-x1)):
                    y = round(a * x + b)
                    line_points.append((x, y))
        #Adds the points of processed line to the result list
        profile_points += line_points
        #Computes and adds profile breakpoint to the list
        line_break_points.append(len(profile_points))
        x1, y1 = x2, y2
    #Adds the last point to the result list
    profile_points.append((x2, y2))

    #A list containing values corresponding to the each profile point
    profile = []
    #The image as a two-dimensional array
    image_array = image.imagearray
    #Image height
    image_height = image.size[1]
    #Gets the pixel values
    for x, y in profile_points:
        profile.append(image_array[image_height - y - 1][x])

    #Initializes the profile graph objects
    fig, ax = plt.subplots()
    #Draws dashed vertical lines at the breakpoints
    for pnt in line_break_points:
        ax.axvline(x=pnt, color='#e64552', linestyle="dashed", linewidth=1)
    #Prepares the list of values for x-axis of the graph
    x_axis_data = range(0, len(profile))
    #If the image has one channel, the pixel values are integers 
    # and can be plotted directly on the graph
    if len(image.channels) == 1:
        ax.plot(x_axis_data, profile, color=image.guicolor_repr[0])
    #If the image has more than one channel, the pixel values are tuples of several integer 
    # and need to be unpacked and then plotted as a separate profile lines for each channel
    else:
        for idx in range(len(image.channels)):
            y_axis_data = [pixel[idx] for pixel in profile]
            ax.plot(x_axis_data, y_axis_data, color=image.guicolor_repr[idx])
    #Sets labels, grid and layout of the graph
    ax.set_xlabel("Distance (pixels)")
    ax.set_ylabel("Pixel Value")
    ax.grid()
    plt.tight_layout()

    #Integrates the graph with the root window
    fig_canvas = FigureCanvasTkAgg(fig, master=rootwindow)
    fig_canvas.draw()
    toolbar = NavigationToolbar2Tk(fig_canvas, rootwindow)
    toolbar.update()

    toolbar.pack(side=tk.BOTTOM, fill=tk.X)
    fig_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    #Function to proper close of the graph window
    def close_profile():
        rootwindow.destroy()
        plt.close(fig.number)
    rootwindow.protocol("WM_DELETE_WINDOW", close_profile)


def close_profiles():
    '''
    Closes all graph objects.
    '''
    plt.close("all")
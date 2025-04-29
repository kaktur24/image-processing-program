from PIL import Image, ImageTk
import numpy as np
import cv2 as cv
import apoconv_morph as cm


def getimage(path):
    '''
    Opens the image located at the given path and returns the image as an object.

    Args:
        path (str): Image file path.
    
    Returns:
        ImageRGB/ImageGrayscale: Image wrapper object.
    '''
    try:
        image = Image.open(path)
    except:
        return None

    mode = image.mode
    if mode in ['RGB']:
        return ImageRGB(image)
    elif mode in ["L", "1"]:
        return ImageGrayscale(image)
    else:
        return None


# Dictionary containing values for conversion from RGB to Grayscale image
RGB2GRAY_CONVERSION_LUT = {"red":[0] * 256, "green":[0] * 256, "blue":[0] * 256}
for i in range(1, 256):
    RGB2GRAY_CONVERSION_LUT["red"][i] = 0.31 * i 
    RGB2GRAY_CONVERSION_LUT["green"][i] = 0.52 * i
    RGB2GRAY_CONVERSION_LUT["blue"][i] = 0.17 * i


#////////////////////////////
# Images Base
#//////////////////////////// 
class ImageBase:
    '''
    A base class for an image wrapper classes
    '''
    def __init__(self, image, filename=None):
        # Pillow image  object
        self.__image = image
        # Image size - (width, height)
        self.size = image.size
        # Image file name
        if filename is None:
            self.filename = image.filename
        else:
            self.filename = filename
    # Image mode given by Pillow
    @property
    def internalmode(self):
        return self.__image.mode
    # Image as the numpy array
    @property
    def imagearray(self):
        return np.array(self.__image)

    def getphotoimage(self):
        '''
        Converts the image to a PhotoImage object.

        Returns:
            PhotoImage: Image converted to PhotoImage object.
        '''
        return ImageTk.PhotoImage(self.__image)
    
    def duplicate(self):
        '''
        Duplicates the image.

        Returns:
            Image: Image duplicate as Pillow image object.
        '''
        return Image.fromarray(self.imagearray)

    def resize(self, factor):
        '''
        Resizes the image according to the given resize factor and returns the resized image as a new image object.

        Args:
            factor (float): Resize factor.
        
        Returns:
            Image: Resized image as a Pillow image object.
        '''
        return self.__image.resize((round(self.size[0]*factor), round(self.size[1]*factor)))
    
    def save(self, filename):
        '''
        Saves the image on the disk.

        Args:
            filename (str): Image file full name (path).
        '''
        if filename == self.filename:
            img_tmp = self.__image.copy()
            self.__image.close()
            img_tmp.save(filename)
            self.__image = img_tmp
        else: 
            self.__image.save(filename)

    def close(self):
        '''
        Closes the image.
        '''
        self.__image.close()

        
#////////////////////////////
# RGB Images
#////////////////////////////        
class ImageRGB(ImageBase):
    '''
    A class that represents an RGB image.
    '''
    def __init__(self, image, filename=None):
        super().__init__(image, filename)
        # Image mode
        self.mode = "RGB"
        # Number of pixel values
        self.M = 256
        # Maximum pixel value
        self.Lmax = self.M - 1
        # Minimum pixel value
        self.Lmin = 0
        # List of channel names
        self.channels = ["Red Channel", "Green Channel", "Blue Channel"]
        # List of color representations for channels in gui context
        self.guicolor_repr = ["red", "green", "blue"]

    def duplicate(self, filename):
        '''
        Duplicates the image.

        Args:
            filename (str): Image file name.

        Returns:
            ImageRGB: Image duplicate.
        '''
        return ImageRGB(super().duplicate(), filename)

    def resize(self, factor):
        '''
        Resizes the image according to the given resize factor and returns the resized image as a new image object.

        Args:
            factor (float): Resize factor.
        
        Returns:
            ImageRGB: Resized image.
        '''
        return ImageRGB(super().resize(factor), self.filename)

    def convert(self, trg_mode):
        '''
        Converts the image to the given image mode.

        Args:
            trg_mode (str): String representing the image mode.
        
        Returns:
            image object of the given type
        '''
        if trg_mode == "GS": return self.convert_rgb2gray()
    
    def convert_rgb2gray(self):
        '''
        Converts the RGB image to the grayscale image.

        Returns:
            ImageGrayscale: The image in grayscale representation.
        '''
        pixels_array = self.imagearray
        width, height = self.size
        new_array = np.zeros((height, width), dtype=np.uint8)
        for y in range(height):
            for x in range(width):
                red, green, blue = pixels_array[y][x]
                new_array[y][x] = round(RGB2GRAY_CONVERSION_LUT["red"][red] + 
                                        RGB2GRAY_CONVERSION_LUT["green"][green] + 
                                        RGB2GRAY_CONVERSION_LUT["blue"][blue])
        return ImageGrayscale(Image.fromarray(new_array), self.filename)

    def histogram(self):
        '''
        Returns the histogram of the image.

        Returns:
            list[[int] [int] [int]]: Histogram.
        '''
        pixels_array = self.imagearray
        width, height = self.size
        r_hist = [0] * self.M
        g_hist = [0] * self.M
        b_hist = [0] * self.M
        histogram = (r_hist, g_hist, b_hist) 

        for y in range(height):
            for x in range(width):
                pixel = pixels_array[y][x]
                for hist, value in zip(histogram, pixel):
                    hist[value] += 1
        return histogram

    #///////// Convolution operations /////////
    def smooth_avarage(self, bordertype_code, border_param=0):
        '''
        Performs an averaging smoothing operation on the image.

        Args:
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageRGB: Result image of applying the operation.
        '''
        ret_image = cm.smooth_avarage(self.imagearray, bordertype_code, (border_param)*3)
        return ImageRGB(Image.fromarray(ret_image), self.filename)
    
    def smooth_weighted_avarage(self, param_k, bordertype_code, border_param=0):
        '''
        Performs a weighted averaging smoothing operation on the image.

        Args:
            param_k (int): Parameter k for smoothing mask.
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageRGB: Result image of applying the operation.
        '''
        ret_image = cm.smooth_weighted_avarage(self.imagearray, param_k, bordertype_code, (border_param)*3)
        return ImageRGB(Image.fromarray(ret_image), self.filename)
    
    def smooth_gaussian(self, bordertype_code, border_param=0):
        '''
        Performs a gaussian smoothing operation on the image.

        Args:
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageRGB: Result image of applying the operation.
        '''
        ret_image = cm.smooth_gaussian(self.imagearray, bordertype_code, (border_param)*3)
        return ImageRGB(Image.fromarray(ret_image), self.filename)

    def median_blur(self, mask_size, bordertype_code, border_param=0):
        '''
        Performs a median blur operation on the image.

        Args:
            mask_size (int): Size of the squared median mask.
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageRGB: Result image of applying the operation.
        '''
        ret_image = cm.median_blur(self.imagearray, mask_size, bordertype_code, (border_param)*3)
        return ImageRGB(Image.fromarray(ret_image), self.filename)
    
    def sharpen_laplacian(self, mask_index, bordertype_code, border_param=0):
        '''
        Performs a laplacian sharpening operation on the image.

        Args:
            mask_index (int): Index of the mask in the list of available masks.
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageRGB: Result image of applying the operation.
        '''
        ret_image = cm.sharpen_laplacian(self.imagearray, mask_index, bordertype_code, (border_param)*3)
        return ImageRGB(Image.fromarray(ret_image), self.filename)

    def edgedetection_Sobel_mask(self, mask_code, bordertype_code, border_param=0):
        '''
        Performs a edge detection operation according to Sobel's mask on the image.

        Args:
            mask_code (str): String representing the direction of the Sobel's mask.
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageRGB: Result image of applying the operation.
        '''
        image = cv.cvtColor(self.imagearray, cv.COLOR_RGB2GRAY)
        ret_image = cm.edgedetection_Sobel_mask(image, mask_code, bordertype_code, (border_param)*3)
        return ImageRGB(Image.fromarray(cv.cvtColor(ret_image, cv.COLOR_GRAY2RGB)), self.filename)

    def edgedetection_Sobel_operator(self, bordertype_code, border_param=0):
        '''
        Performs a edge detection operation using the Sobel's operator on the image.

        Args:
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageRGB: Result image of applying the operation.
        '''
        image = cv.cvtColor(self.imagearray, cv.COLOR_RGB2GRAY)
        ret_image = cm.edgedetection_Sobel_operator(image, bordertype_code, (border_param)*3)
        return ImageRGB(Image.fromarray(cv.cvtColor(ret_image, cv.COLOR_GRAY2RGB)), self.filename)

    def edgedetection_Prewitt_operator(self, bordertype_code, border_param=0):
        '''
        Performs a edge detection operation using the Prewitt's operator on the image.

        Args:
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageRGB: Result image of applying the operation.
        '''
        image = cv.cvtColor(self.imagearray, cv.COLOR_RGB2GRAY)
        ret_image = cm.edgedetection_Prewitt_operator(image, bordertype_code, (border_param)*3)
        return ImageRGB(Image.fromarray(cv.cvtColor(ret_image, cv.COLOR_GRAY2RGB)), self.filename)

    def edgedetection_Canny_operator(self, tshd1, tshd2, bordertype_code, border_param=0):
        '''
        Performs a edge detection operation using the Canny's operator on the image.

        Args:
            tshd1 (int): Value of the first threshold.
            tshd2 (int): Value of the second threshold.
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageRGB: Result image of applying the operation.
        '''
        image = cv.cvtColor(self.imagearray, cv.COLOR_RGB2GRAY)
        ret_image = cm.edgedetection_Canny_operator(image, tshd1, tshd2, bordertype_code, (border_param)*3)
        return ImageRGB(Image.fromarray(cv.cvtColor(ret_image, cv.COLOR_GRAY2RGB)), self.filename)


#////////////////////////////
# Grayscale Images
#//////////////////////////// 
class ImageGrayscale(ImageBase):
    '''
    A class that represents a Grayscale image. It can represent either binary image and 8-bit grayscale image.
    '''
    def __init__(self, image, filename=None):
        super().__init__(image, filename)
        self.__validatemode()

    # Image validation and assigning appropriate values of image attributes
    def __validatemode(self):
        if self.internalmode == "L":
            # Image mode
            self.mode = "GS"
            # Number of pixel values
            self.M = 256
            # Maximum pixel value
            self.Lmax = self.M - 1
            # Minimum pixel value
            self.Lmin = 0
            # List of channel names
            self.channels = ["8-bit Channel"]
            # List of color representations for channels in gui context
            self.guicolor_repr = ["#555555"]
        elif self.internalmode == "1":
            # Image mode
            self.mode = "B"
            # Number of pixel values
            self.M = 2
            # Maximum pixel value
            self.Lmax = self.M - 1
            # Minimum pixel value
            self.Lmin = 0
            # List of channel names
            self.channels = ["1-bit Channel"]
            # List of color representations for channels in gui context
            self.guicolor_repr = ["#000000"]

    def duplicate(self, filename):
        '''
        Duplicates the image.

        Args:
            filename (str): Image file name.

        Returns:
            ImageGrayscale: Image duplicate.
        '''
        return ImageGrayscale(super().duplicate(), filename)

    def resize(self, factor):
        '''
        Resizes the image according to the given resize factor and returns the resized image as a new image object.

        Args:
            factor (float): Resize factor.
        
        Returns:
            ImageGrayscale: Resized image.
        '''
        return ImageGrayscale(super().resize(factor), self.filename)

    def convert(self, trg_mode):
        '''
        Converts the image to the given image mode.

        Args:
            trg_mode (str): String representing the image mode.
        
        Returns:
            image object of the given type
        '''
        src_mode = self.mode
        if src_mode == "GS" and trg_mode == "B": return self.convert_gray2bin()
        elif src_mode == "B" and trg_mode == "GS": return self.convert_bin2gray()

    def convert_bin2gray(self):
        '''
        Converts the binary image to the grayscale image.

        Returns:
            ImageGrayscale: The image in 8-bit grayscale representation.
        '''
        pixels_array = self.imagearray
        width, height = self.size
        new_array = np.zeros((height, width), dtype=np.uint8)
        lut = [0, 255]
        for y in range(height):
            for x in range(width):
                new_array[y][x] = lut[pixels_array[y][x]]
        return ImageGrayscale(Image.fromarray(new_array), self.filename)
    
    def convert_gray2bin(self):
        '''
        Converts the grayscale image to the binary image.

        Returns:
            ImageGrayscale: The image in 1-bit representation.
        '''
        return self.treshold_binary(self.Lmax // 2)
    
    def histogram(self):
        '''
        Returns the histogram of the image.

        Returns:
            list[int]: Histogram.
        '''
        pixels_array = self.imagearray
        width, height = self.size
        histogram = [0] * self.M

        for y in range(height):
            for x in range(width):
                pixel = pixels_array[y][x]
                histogram[pixel] += 1
        return histogram

    def negate(self):
        '''
        Negates the image.

        Returns:
            ImageGrayscale: Negated image.
        '''
        new_array = self.__point_operation_onearg(self.__get_lut(lambda pixel: self.Lmax - pixel))
        return ImageGrayscale(Image.fromarray(new_array), self.filename)

    #///////// Thresholding /////////
    def treshold_binary(self, treshold):
        '''
        Performs binary thresholding on the image.

        Args:
            treshold (int): Value of the threshold.

        Returns:
            ImageGrayscale: 1-bit image.
        '''
        lut = [0] * (treshold+1) + [1] * (self.M - treshold-1)
        new_array = self.__point_operation_onearg(lut)
        return ImageGrayscale(Image.fromarray(new_array.astype(np.bool_)), self.filename)

    def treshold_grayscale(self, treshold):
        '''
        Performs thresholding with maintaining gray levels on the image.

        Args:
            treshold (int): Value of the threshold.

        Returns:
            ImageGrayscale: Grayscale image.
        '''
        lut = [self.Lmin] * (treshold+1) + [v for v in range(treshold+1, self.M)]
        new_array = self.__point_operation_onearg(lut)
        return ImageGrayscale(Image.fromarray(new_array), self.filename)

    def treshold_two(self, tshd1, tshd2):
        '''
        Performs thresholding with two thresholds on the image.

        Args:
            tshd1 (int): Value of the first threshold.
            tshd2 (int): Value of the second threshold.

        Returns:
            ImageGrayscale: Grayscale image.
        '''
        lut = [self.Lmin] * (tshd1) + [self.Lmax] * (tshd2 - tshd1 + 1) + [self.Lmin] * (self.M - tshd2 - 1)
        new_array = self.__point_operation_onearg(lut)
        return ImageGrayscale(Image.fromarray(new_array), self.filename)

    #///////// Segmentation /////////
    def segmentation_threshold(self, code, *args, adaptivemode=0):
        '''
        Performs the segmentation by thresholding on the image.

        Args:
            code (str): String representing thresholding type. Code values:
                "bin": binary thresholding
                "gray": thresholding with maintaining gray levels
                "2th": thresholding with two thresholds
                "adapt": adaptive thresholding
                "otsu": otsu thresholding
            adaptivemode (int): Code for adaptive thresholding type. Code values:
                0: mean
                1: gaussian
            *args: Values of thresholds. Number of threshold values should match the selected thresholding method.

        Returns:
            ImageGrayscale: Segmented image.
        '''
        ret_image = None
        treshold = -1
        if code == "bin":
            treshold, tmp_image = cv.threshold(self.imagearray, args[0], 1, cv.THRESH_BINARY)
            ret_image = tmp_image.astype(np.bool_)
        elif code == "gray":
            treshold, ret_image = cv.threshold(self.imagearray, args[0], 0, cv.THRESH_TOZERO)
        elif code == "2th":
            treshold, tmp_image1 = cv.threshold(self.imagearray, args[0]-1, 1, cv.THRESH_BINARY)
            treshold, tmp_image2 = cv.threshold(self.imagearray, args[1], 1, cv.THRESH_BINARY_INV)
            ret_image = ((tmp_image1 + tmp_image2) - 1) * self.Lmax
        elif code == "adapt":
            if adaptivemode == 0:
                ret_image = cv.adaptiveThreshold(self.imagearray, self.Lmax, cv.ADAPTIVE_THRESH_MEAN_C , cv.THRESH_BINARY, 7, 0)
            elif adaptivemode == 1:
                ret_image = cv.adaptiveThreshold(self.imagearray, self.Lmax, cv.ADAPTIVE_THRESH_GAUSSIAN_C , cv.THRESH_BINARY, 7, 0)
        elif code == "otsu":
            treshold, ret_image = cv.threshold(self.imagearray, 0, self.Lmax, cv.THRESH_BINARY+cv.THRESH_OTSU)
        return (treshold, ImageGrayscale(Image.fromarray(ret_image), self.filename))

    #///////// Arithmetic operations with constant integer /////////
    def add_int(self, number, oversaturation=True):
        '''
        Adds the constant integer to the image.

        Args:
            number (int): Integer value which will be added to the image.
            oversaturation (bool): A flag for oversaturation.

        Returns:
            ImageGrayscale: Image after applying operation.
        '''
        new_array = self.__arithmetic_int(lambda pixel: pixel + number, oversaturation)
        return ImageGrayscale(Image.fromarray(new_array), self.filename)

    def multiply_int(self, number, oversaturation=True):
        '''
        Multiplies the image by the constant integer.

        Args:
            number (int): Integer value by which the image will be multiplied.
            oversaturation (bool): A flag for oversaturation.

        Returns:
            ImageGrayscale: Image after applying operation.
        '''
        new_array = self.__arithmetic_int(lambda pixel: pixel * number, oversaturation)
        return ImageGrayscale(Image.fromarray(new_array), self.filename)

    def divide_int(self, number, oversaturation=True):
        '''
        Divides the image by the constant integer.

        Args:
            number (int): Integer value by which the image will be divided.
            oversaturation (bool): A flag for oversaturation.

        Returns:
            ImageGrayscale: Image after applying operation.
        '''
        new_array = self.__arithmetic_int(lambda pixel: pixel / number, oversaturation)
        return ImageGrayscale(Image.fromarray(new_array), self.filename)
    
    #///////// Arithmetic operations between images /////////
    def add_images(self, image, oversaturation):
        '''
        Adds the actual image to the given image.

        Args:
            image (ImageGrayscale): The image which will be added to the actual image.
            oversaturation (bool): A flag for oversaturation.

        Returns:
            ImageGrayscale: Image after applying operation.
        '''
        if oversaturation:
            new_array = self.__point_operation_twoargs(image, lambda px1, px2: self.__oversaturation(px1 + px2))
        else:
            new_array = self.__point_operation_twoargs(image, lambda px1, px2: 
                                                self.__normalize_pixel(px1, self.Lmin, self.Lmax, trg_uprange=(self.Lmax-self.Lmin)//2) +
                                                self.__normalize_pixel(px2, self.Lmin, self.Lmax, trg_uprange=(self.Lmax-self.Lmin)//2))
        return ImageGrayscale(Image.fromarray(new_array), self.filename)

    def subtract_images(self, image):
        '''
        Performs absolute subtraction between the actual image and the given image.

        Args:
            image (ImageGrayscale): The image which will be subtracted from the actual image.

        Returns:
            ImageGrayscale: Image after applying operation.
        '''
        new_array = self.__point_operation_twoargs(image, lambda px1, px2: abs(px1 - px2))
        return ImageGrayscale(Image.fromarray(new_array), self.filename)

    #///////// Logic operations between images /////////
    def logic_not(self):
        '''
        Performs logical NOT operation on bits of the image.

        Returns:
            ImageGrayscale: Image after applying operation.
        '''   
        new_array = self.__point_operation_onearg(self.__get_lut(lambda pixel: self.Lmax ^ pixel))
        return ImageGrayscale(Image.fromarray(new_array), self.filename)

    def logic_and(self, mask):
        '''
        Performs logical AND operation between corresponding bits of the image and the given mask.

        Args:
            mask (ImageGrayscale): Logical operation mask.

        Returns:
            ImageGrayscale: Image after applying operation.
        '''
        new_array = self.__point_operation_twoargs(mask, lambda px1, px2: px1 & px2)
        return ImageGrayscale(Image.fromarray(new_array), self.filename)

    def logic_or(self, mask):
        '''
        Performs logical OR operation between corresponding bits of the image and the given mask.

        Args:
            mask (ImageGrayscale): Logical operation mask.

        Returns:
            ImageGrayscale: Image after applying operation.
        '''
        new_array = self.__point_operation_twoargs(mask, lambda px1, px2: px1 | px2)
        return ImageGrayscale(Image.fromarray(new_array), self.filename)

    def logic_xor(self, mask):
        '''
        Performs logical XOR operation between corresponding bits of the image and the given mask.

        Args:
            mask (ImageGrayscale): Logical operation mask.

        Returns:
            ImageGrayscale: Image after applying operation.
        '''
        new_array = self.__point_operation_twoargs(mask, lambda px1, px2: px1 ^ px2)
        return ImageGrayscale(Image.fromarray(new_array), self.filename)
    
    #///////// Histogram stretching /////////
    def hist_linear_stretch(self, rangevalues=None, cutoff=False):
        '''
        Performs linear stretching of histogram.

        Args:
            rangevalues (tuple(int, int)): The range of histogram which will be stretched to the full range.
            cutoff (bool): A flag for a stretch variant that cut off 5% of values on both sides when calculating the range. 

        Returns:
            ImageGrayscale: Image after applying operation.
        '''
        hist = self.histogram()
        minval, maxval = (0,0)

        if rangevalues is None:
            if cutoff:
                val_treshold = round(self.size[0] * self.size[1] * 0.05)
                sum = 0
                for minval in range(self.M):
                    sum += hist[minval]
                    if sum  > val_treshold:
                        break
                sum = 0
                for maxval in range(self.Lmax, self.Lmin-1, -1):
                    sum += hist[maxval]
                    if sum > val_treshold:
                        break
            else:
                for minval in range(self.M):
                    if hist[minval] > 0: break
                for maxval in range(self.Lmax, self.Lmin-1, -1):
                    if hist[maxval] > 0: break
        else:
            minval, maxval = rangevalues

        if minval >= maxval:
            return self.duplicate(self.filename)
        
        lut = self.__get_lut(lambda px: self.__normalize_pixel(px, minval, maxval) if minval <= px <= maxval else self.__oversaturation(px, minval, maxval))
        new_array = self.__point_operation_onearg(lut)
        return ImageGrayscale(Image.fromarray(new_array), self.filename)

    def hist_gamma_stretch(self, gamma):
        '''
        Performs gamma stretching of histogram.

        Args:
            gamma (float): Gamma parameter.

        Returns:
            ImageGrayscale: Image after applying operation.
        '''
        new_array = self.__point_operation_onearg(self.__get_lut(lambda pixel: round(self.Lmax * (pixel / self.Lmax)**(1/gamma))))
        return ImageGrayscale(Image.fromarray(new_array), self.filename)

    def hist_equalization(self):
        '''
        Performs equalization of histogram.

        Returns:
            ImageGrayscale: Image after applying operation.
        '''
        hist = self.histogram()
        sum_px = self.size[0] * self.size[1]

        for val in range(1, len(hist)):
            hist[val] += hist[val-1]
        for val in range(len(hist)):
            hist[val] /= sum_px
        
        for dst_min in hist:
            if dst_min > 0:
                break
        
        if dst_min == 1:
            return self.duplicate(self.filename)

        lut = [0] * self.M
        for val in range(self.M):
            lut[val] = self.__normalize_pixel(hist[val], dst_min, 1)
        new_array = self.__point_operation_onearg(lut)
        return ImageGrayscale(Image.fromarray(new_array), self.filename)

    #///////// Convolution operations /////////
    def smooth_avarage(self, bordertype_code, border_param=0):
        '''
        Performs an averaging smoothing operation on the image.

        Args:
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageGrayscale: Result image of applying the operation.
        '''
        ret_image = cm.smooth_avarage(self.imagearray, bordertype_code, border_param)
        return ImageGrayscale(Image.fromarray(ret_image), self.filename)
    
    def smooth_weighted_avarage(self, param_k, bordertype_code, border_param=0):
        '''
        Performs a weighted averaging smoothing operation on the image.

        Args:
            param_k (int): Parameter k for smoothing mask.
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageGrayscale: Result image of applying the operation.
        '''
        ret_image = cm.smooth_weighted_avarage(self.imagearray, param_k, bordertype_code, border_param)
        return ImageGrayscale(Image.fromarray(ret_image), self.filename)
    
    def smooth_gaussian(self, bordertype_code, border_param=0):
        '''
        Performs a gaussian smoothing operation on the image.

        Args:
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageGrayscale: Result image of applying the operation.
        '''
        ret_image = cm.smooth_gaussian(self.imagearray, bordertype_code, border_param)
        return ImageGrayscale(Image.fromarray(ret_image), self.filename)

    def median_blur(self, mask_size, bordertype_code, border_param=0):
        '''
        Performs a median blur operation on the image.

        Args:
            mask_size (int): Size of the squared median mask.
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageGrayscale: Result image of applying the operation.
        '''
        ret_image = cm.median_blur(self.imagearray, mask_size, bordertype_code, border_param)
        return ImageGrayscale(Image.fromarray(ret_image), self.filename)
    
    def sharpen_laplacian(self, mask_index, bordertype_code, border_param=0):
        '''
        Performs a laplacian sharpening operation on the image.

        Args:
            mask_index (int): Index of the mask in the list of available masks.
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageGrayscale: Result image of applying the operation.
        '''
        ret_image = cm.sharpen_laplacian(self.imagearray, mask_index, bordertype_code, border_param)
        return ImageGrayscale(Image.fromarray(ret_image), self.filename)

    def edgedetection_Sobel_mask(self, mask_code, bordertype_code, border_param=0):
        '''
        Performs a edge detection operation according to Sobel's mask on the image.

        Args:
            mask_code (str): String representing the direction of the Sobel's mask.
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageGrayscale: Result image of applying the operation.
        '''
        ret_image = cm.edgedetection_Sobel_mask(self.imagearray, mask_code, bordertype_code, border_param)
        return ImageGrayscale(Image.fromarray(ret_image), self.filename)

    def edgedetection_Sobel_operator(self, bordertype_code, border_param=0):
        '''
        Performs a edge detection operation using the Sobel's operator on the image.

        Args:
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageGrayscale: Result image of applying the operation.
        '''
        ret_image = cm.edgedetection_Sobel_operator(self.imagearray, bordertype_code, border_param)
        return ImageGrayscale(Image.fromarray(ret_image), self.filename)

    def edgedetection_Prewitt_operator(self, bordertype_code, border_param=0):
        '''
        Performs a edge detection operation using the Prewitt's operator on the image.

        Args:
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageGrayscale: Result image of applying the operation.
        '''
        ret_image = cm.edgedetection_Prewitt_operator(self.imagearray, bordertype_code, border_param)
        return ImageGrayscale(Image.fromarray(ret_image), self.filename)

    def edgedetection_Canny_operator(self, tshd1, tshd2, bordertype_code, border_param=0):
        '''
        Performs a edge detection operation using the Canny's operator on the image.

        Args:
            tshd1 (int): Value of the first threshold.
            tshd2 (int): Value of the second threshold.
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageGrayscale: Result image of applying the operation.
        '''
        ret_image = cm.edgedetection_Canny_operator(self.imagearray, tshd1, tshd2, bordertype_code, border_param)
        return ImageGrayscale(Image.fromarray(ret_image), self.filename)

    #///////// Morphology operations /////////
    def morph_erode(self, struct_code, bordertype_code, border_param=0):
        '''
        Performs a morphology erode operation on the image.

        Args:
            struct_code (int): Shape code of the structuring element. See _morph_operation() in module apoconv_morph 
            for the available types. 
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageGrayscale: Result image of applying the operation.
        '''
        return self.__morphology_operation(cm.morph_erode, struct_code, bordertype_code, border_param)

    def morph_dilate(self, struct_code, bordertype_code, border_param=0):
        '''
        Performs a morphology dilate operation on the image.

        Args:
            struct_code (int): Shape code of the structuring element. See _morph_operation() in module apoconv_morph 
            for the available types. 
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageGrayscale: Result image of applying the operation.
        '''
        return self.__morphology_operation(cm.morph_dilate, struct_code, bordertype_code, border_param)

    def morph_open(self, struct_code, bordertype_code, border_param=0):
        '''
        Performs a morphological opening operation on the image.

        Args:
            struct_code (int): Shape code of the structuring element. See _morph_operation() in module apoconv_morph 
            for the available types.
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageGrayscale: Result image of applying the operation.
        '''
        return self.__morphology_operation(cm.morph_open, struct_code, bordertype_code, border_param)

    def morph_close(self, struct_code, bordertype_code, border_param=0):
        '''
        Performs a morphological closing operation on the image.

        Args:
            struct_code (int): Shape code of the structuring element. See _morph_operation() in module apoconv_morph 
            for the available types.
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.
        
        Returns:
            ImageGrayscale: Result image of applying the operation.
        '''
        return self.__morphology_operation(cm.morph_close, struct_code, bordertype_code, border_param)

    #///////// Image analysis /////////
    def analyze(self, area, circuit, w1, w2, w3, w9, w10, w11, m1, m2, m3):
        '''
        Searches for objects in the image and calculates the selected parameters of these objects. Returns the result as 
        a list of strings formatted in csv style.

        Args:
            area (bool): A flag for calculating area of objects.
            circuit (bool): A flag for calculating circuit of objects.
            w1 (bool): A flag for calculating W1 parameter of objects.
            w2 (bool): A flag for calculating W2 parameter of objects.
            w3 (bool): A flag for calculating W3 parameter of objects.
            w9 (bool): A flag for calculating W9 parameter of objects.
            w10 (bool): A flag for calculating W10 parameter of objects.
            w11 (bool): A flag for calculating W11 parameter of objects.
            m1 (bool): A flag for calculating M1 moment of objects.
            m2 (bool): A flag for calculating M2 moment of objects.
            m3 (bool): A flag for calculating M3 moment of objects.
        
        Returns:
            list[str]: List of results formatted as strings according to csv file rules. Every element in the list represents 
            a row of csv file.
            
        '''
        image = self.imagearray
        if self.mode != "GS":
            image = self.convert("GS").imagearray
        object_contours = cv.findContours(image, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)[0]
        ret_list = []
        for obj_cntr in object_contours:
            area_S = cv.contourArea(obj_cntr)
            cir_L = cv.arcLength(obj_cntr, True)
            
            obj_features_list = []
            if area: obj_features_list.append(area_S)
            if circuit: obj_features_list.append(cir_L)

            if w1:
                val_w1 = 2 * ((area_S / np.pi)**(1/2))
                obj_features_list.append(val_w1)
            if w2:
                val_w2 = (cir_L / np.pi)
                obj_features_list.append(val_w2)
            if w3:
                val_w3 = (cir_L / (2 * ((area_S * np.pi)**(1/2)))) - 1
                obj_features_list.append(val_w3)
            if w9:
                val_w9 = (2 * ((np.pi * area_S)**(1/2))) / cir_L
                obj_features_list.append(val_w9)
            if w10:
                obj_convex_hull = cv.convexHull(obj_cntr)
                convex_S = cv.contourArea(obj_convex_hull)
                val_w10 = area_S / convex_S
                obj_features_list.append(val_w10)
            if w11:
                val_w11 = ((4 * area_S) / np.pi)**(1/2)
                obj_features_list.append(val_w11)

            if True in [m1, m2 , m3]:
                mnts = cv.moments(obj_cntr)
                if m1:
                    val_M1 = mnts["nu20"] + mnts["nu02"]
                    obj_features_list.append(val_M1)
                if m2:
                    val_M2 = (mnts["nu20"] - mnts["nu02"])**2 + (4 * (mnts["nu11"]**2))
                    obj_features_list.append(val_M2)
                if m3:
                    val_M3 = (mnts["nu30"] - (3 * mnts["nu12"]))**2 + ((3 * mnts["nu21"]) - mnts["nu03"])**2
                    obj_features_list.append(val_M3)

            ret_list.append(",".join([str(obj) for obj in obj_features_list]) + "\n")
        return ret_list

    #///////// Private metods /////////
    def __oversaturation(self, pixel, minval=None, maxval=None):
        '''
        Recalculates the pixel value according to the oversaturation rules. If a pixel is smaller than the minimum or 
        greater than the maximum, it takes the minimum value or maximum value, respectively.

        Args:
            pixel (int): Pixel value.
            minval (int): Minimum value. It is equal to Lmin by default.
            maxval (int): Maximum value. It is equal to Lmax by default.
        
        Returns:
            int: Pixel value.
        '''
        if minval is None: minval = self.Lmin
        if maxval is None: maxval = self.Lmax
        if pixel < minval:
            return self.Lmin
        elif pixel > maxval:
            return self.Lmax
        else:
            return pixel
        
    def __normalize_pixel(self, pixel, minval, maxval, trg_lowrange=None, trg_uprange=None):
        '''
        Normalizes the pixel value. Requires specifying the range to be normalized. The default target range is from Lmin to Lmax.

        Args:
            pixel (int): Pixel value.
            minval (int): Minimum value of the range to be normalized.
            maxval (int): Maximum value of the range to be normalized.
            trg_lowrange (int): Minimum value of the target range. It is equal to Lmin by default.
            trg_uprange (int): Maximum value of the target range. It is equal to Lmax by default.

        Returns:
            int: Pixel value.
        '''
        if trg_lowrange is None: trg_lowrange = self.Lmin
        if trg_uprange is None: trg_uprange = self.Lmax
        return round(((pixel - minval) / (maxval - minval)) * (trg_uprange - trg_lowrange) + trg_lowrange)
        
    def __get_lut(self, operation):
        '''
        Calculates the Look-Up Table for the image according to the given operation.

        Args:
            operation (function(int)): Function that takes one integer argument and returns a value for the LUT.
        
        Returns:
            list[int]: Look-Up Table.
        '''
        lut = [0] * self.M
        for val in range(self.M):
            lut[val] = operation(val)
        return lut

    def __point_operation_onearg(self, lut):
        '''
        Performs an unary point operation using the LUT.

        Args:
            lut (list[int]): Image Look-Up Table for operation.

        Returns:
            Array: Image array.
        '''
        pixels_array = self.imagearray
        width, height = self.size
        for y in range(height):
            for x in range(width):
                pixels_array[y][x] = lut[pixels_array[y][x]]
        return pixels_array

    def __arithmetic_int(self, operation, oversaturation):
        '''
        Performs an arithmetic operation with a fixed integer on the image.

        Args:
            operation (function(int)): Function that takes one integer argument and returns a new pixel value.
            oversaturation (bool): A flag for oversaturation. If the flag is False pixel value will be normalized.

        Returns:
            Array: Image array.
        '''
        lut = [0] * self.M
        if oversaturation: 
            for val in range(self.M):
                lut[val] = self.__oversaturation(operation(val))
        else:
            minval, maxval = operation(self.Lmin), operation(self.Lmax) 
            for val in range(self.M):
                lut[val] = self.__normalize_pixel(operation(val), minval, maxval) 
        return self.__point_operation_onearg(lut)

    def __point_operation_twoargs(self, other_image, operation):
        '''
        Performs a two arguments point operation on the actual image and the given image.

        Args:
            other_image (ImageGrayscale): Second image.
            operation (function(int, int)): Function that takes two integer arguments and returns a new pixel value.

        Returns:
            Array: Image array.
        '''
        pixels_array_1 = self.imagearray
        pixels_array_2 = other_image.imagearray
        pixels_array_ret = np.zeros_like(pixels_array_1)
        width, height = self.size
        for y in range(height):
            for x in range(width):
                pixels_array_ret[y][x] = operation(int(pixels_array_1[y][x]), int(pixels_array_2[y][x]))
        return pixels_array_ret

    def __morphology_operation(self, morph_func, struct_code, bordertype_code, border_param):
        '''
        Performs a morphology operation on the image.

        Args:
            morph_func (function(Array, int, str, int)): Morphological function.
            struct_code (int): Shape code of the structuring element. See _morph_operation() in module apoconv_morph 
            for the available types. 
            bordertype_code (str): String representing border type. See _prepare_border() in module apoconv_morph 
            for the available types.
            border_param (int): Parameter value for border types requiring parameter.

        Returns:
            ImageGrayscale: Resulting image.
        '''
        image = self.convert("GS")
        ret_image = morph_func(image.imagearray, struct_code, bordertype_code, border_param*image.Lmax)
        return ImageGrayscale(Image.fromarray(ret_image), self.filename).convert("B")


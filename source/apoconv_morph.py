import numpy as np
import cv2 as cv


def smooth_avarage(image, bordertype_code, border_param=0):
    '''
    Performs an averaging smoothing operation on the image.

    Args:
        image (Array): Array representing image.
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    image = _prepare_border(image, bordertype_code, 1, border_param)
    ret_image = cv.blur(image, (3,3))
    ret_image = _remove_border(ret_image, bordertype_code, 1, border_param)
    return ret_image


def smooth_weighted_avarage(image, param_k, bordertype_code, border_param=0):
    '''
    Performs a weighted averaging smoothing operation on the image.

    Args:
        image (Array): Array representing image.
        param_k (int): Parameter k for smoothing mask.
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    kernel = np.array([[1,1,1],[1,param_k,1],[1,1,1]])/(param_k + 8)
    ret_image = _filter2d_extended(image, kernel, bordertype_code, border_param)
    return ret_image


def smooth_gaussian(image, bordertype_code, border_param=0):
    '''
    Performs a gaussian smoothing operation on the image.

    Args:
        image (Array): Array representing image.
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    kernel = np.array([[1,2,1],[2,4,2],[1,2,1]])/16
    ret_image = _filter2d_extended(image, kernel, bordertype_code, border_param)
    return ret_image


def median_blur(image, mask_size, bordertype_code, border_param=0):
    '''
    Performs a median blur operation on the image.

    Args:
        image (Array): Array representing image.
        mask_size (int): Size of the squared median mask.
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    image = _prepare_border(image, bordertype_code, mask_size // 2, border_param)
    ret_image = cv.medianBlur(image, mask_size)
    ret_image = _remove_border(ret_image, bordertype_code, mask_size // 2, border_param)
    return ret_image


def sharpen_laplacian(image, mask_index, bordertype_code, border_param=0):
    '''
    Performs a laplacian sharpening operation on the image.

    Args:
        image (Array): Array representing image.
        mask_index (int): Index of the mask in the list of available masks.
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    masks = [np.array([[0,-1,0],[-1,4,-1],[0,-1,0]]),
            np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]]),
            np.array([[1,-2,1],[-2,4,-2],[1,-2,1]])]
    kernel = masks[mask_index]
    ret_image = _filter2d_extended(image, kernel, bordertype_code, border_param)
    return ret_image


def edgedetection_Sobel_mask(image, mask_code, bordertype_code, border_param=0):
    '''
    Performs a edge detection operation according to Sobel's mask on the image.

    Args:
        image (Array): Array representing image.
        mask_code (str): String representing the direction of the Sobel's mask.
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    kernels = {"W":np.array([[1,0,-1],[2,0,-2],[1,0,-1]]),
                "NW":np.array([[2,1,0],[1,0,-1],[0,-1,-2]]),
                "N":np.array([[1,2,1],[0,0,0],[-1,-2,-1]]),
                "NE":np.array([[0,1,2],[-1,0,1],[-2,-1,0]]),
                "E":np.array([[-1,0,1],[-2,0,2],[-1,0,1]]),
                "ES":np.array([[-2,-1,0],[-1,0,1],[0,1,2]]),
                "S":np.array([[-1,-2,-1],[0,0,0],[1,2,1]]),
                "WS":np.array([[0,-2,-1],[1,0,-1],[1,2,0]])}
    kernel = kernels[mask_code]
    ret_image = _filter2d_extended(image, kernel, bordertype_code, border_param)
    return ret_image


def edgedetection_Sobel_operator(image, bordertype_code, border_param=0):
    '''
    Performs a edge detection operation using the Sobel's operator on the image.

    Args:
        image (Array): Array representing image.
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    image = _prepare_border(image, bordertype_code, 1, border_param)
    ret_image = cv.Sobel(image, ddepth=-1, dx=1, dy=1)
    ret_image = _remove_border(ret_image, bordertype_code, 1, border_param)
    return ret_image


def edgedetection_Prewitt_operator(image, bordertype_code, border_param=0):
    '''
    Performs a edge detection operation using the Prewitt's operator on the image.

    Args:
        image (Array): Array representing image.
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    maskX = np.array([[1,0,-1],[1,0,-1],[1,0,-1]])
    maskY = np.array([[1,1,1],[0,0,0],[-1,-1,-1]])

    ret_image = np.zeros_like(image)
    height, width = np.shape(ret_image)

    gradientX = _filter2d_extended(image, maskX, bordertype_code, border_param)
    gradientY = _filter2d_extended(image, maskY, bordertype_code, border_param)

    for y in range(height):
        for x in range(width):
            ret_image[y][x] = (gradientX[y][x]**2 + gradientY[y][x]**2)**(1/2)
    return ret_image


def edgedetection_Canny_operator(image, tshd1, tshd2, bordertype_code, border_param=0):
    '''
    Performs a edge detection operation using the Canny's operator on the image.

    Args:
        image (Array): Array representing image.
        tshd1 (int): Value of the first threshold.
        tshd2 (int): Value of the second threshold.
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    image = _prepare_border(image, bordertype_code, 1, border_param)
    ret_image = cv.Canny(image, threshold1=tshd1, threshold2=tshd2, L2gradient=True)
    ret_image = _remove_border(ret_image, bordertype_code, 1, border_param)
    return ret_image


def _filter2d_extended(image, kernel, bordertype_code, border_param):
    '''
    Convolves an image with the kernel. Margins are handled according to the specified method.

    Args:
        image (Array): Array representing image.
        kernel (Array): Array representing kernel.
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    ret_image = _prepare_border(image, bordertype_code, 1, border_param)
    ret_image = cv.filter2D(ret_image, ddepth=-1, kernel=kernel)
    ret_image = _remove_border(ret_image, bordertype_code, 1, border_param)
    return ret_image


def morph_erode(image, struct_elem_type, bordertype_code, border_param):
    '''
    Performs a morphology erode operation on the image.

    Args:
        image (Array): Array representing binary image.
        struct_elem_type (int): Shape code of the structuring element. See _morph_operation() for the available types.
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    return _morph_operation(image, cv.MORPH_ERODE, struct_elem_type, bordertype_code, border_param)


def morph_dilate(image, struct_elem_type, bordertype_code, border_param):
    '''
    Performs a morphology dilate operation on the image.

    Args:
        image (Array): Array representing binary image.
        struct_elem_type (int): Shape code of the structuring element. See _morph_operation() for the available types.
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    return _morph_operation(image, cv.MORPH_DILATE, struct_elem_type, bordertype_code, border_param)


def morph_open(image, struct_elem_type, bordertype_code, border_param):
    '''
    Performs a morphological opening operation on the image.

    Args:
        image (Array): Array representing binary image.
        struct_elem_type (int): Shape code of the structuring element. See _morph_operation() for the available types.
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    return _morph_operation(image, cv.MORPH_OPEN, struct_elem_type, bordertype_code, border_param)


def morph_close(image, struct_elem_type, bordertype_code, border_param):
    '''
    Performs a morphological closing operation on the image.

    Args:
        image (Array): Array representing binary image.
        struct_elem_type (int): Shape code of the structuring element. See _morph_operation() for the available types.
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    return _morph_operation(image, cv.MORPH_CLOSE, struct_elem_type, bordertype_code, border_param)


def _morph_operation(image, operation, struct_elem_type, bordertype_code, border_param):
    '''
    Performs a morphology operation on the image.

    Args:
        image (Array): Array representing binary image.
        operation (int): Morphology operation code.
        struct_elem_type (int): Shape code of the structuring element.
            0: Cross
            1: Rectangle 
        bordertype_code (str): String representing border type. See _prepare_border() for the available types.
        border_param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    structuring_elem_shape = cv.MORPH_RECT if struct_elem_type else cv.MORPH_CROSS
    structuring_elem = cv.getStructuringElement(structuring_elem_shape, (3,3))
    ret_image = _prepare_border(image, bordertype_code, 1, border_param)
    ret_image = cv.morphologyEx(ret_image, operation, structuring_elem)
    ret_image = _remove_border(ret_image, bordertype_code, 1, border_param)
    return ret_image


def _prepare_border(image, typecode, size, param):
    '''
    Expands the image by adding a margin according to the specified rule.

    Args:
        image (Array): Array representing image.
        typecode (str): String representing border (margin) type.
            "const": Fill margin with constant value. Requires parameter.
            "reflect": Reflect the pixels on the edges.
            "wrap": Wrap the pixels.
            "const_result": Add no margins and fill the pixels on the edges with constant value. Requires parameter.
        size (int): Border size.
        param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    if typecode == "const":
        ret_image = cv.copyMakeBorder(image, size, size, size, size, borderType=cv.BORDER_CONSTANT, value=param)
    elif typecode == "reflect":
        ret_image = cv.copyMakeBorder(image, size, size, size, size, borderType=cv.BORDER_REFLECT)
    elif typecode == "wrap":
        ret_image = cv.copyMakeBorder(image, size, size, size, size, borderType=cv.BORDER_WRAP)
    else:
        ret_image = cv.copyMakeBorder(image, size, size, size, size, borderType=cv.BORDER_DEFAULT)
    return ret_image


def _remove_border(image, typecode, size, param):
    '''
    Removes margins from the image. Completes image margin processing if the border type requires it.

    Args:
        image (Array): Array representing image.
        typecode (str): String representing border (margin) type. See _prepare_border() for the available types.
        size (int): Border size.
        param (int): Parameter value for border types requiring parameter.
    
    Returns:
        Array: Image array.
    '''
    ret_image = image[size:(-1)*size, size:(-1)*size]
    if typecode == "const_result":
        ret_image = _add_const_border(ret_image, size, param)
    return ret_image


def _add_const_border(image, size, value):
    '''
    Adds a border to the image. The pixels at the edges of the image are filled with the specified value.

    Args:
        image (Array): Array representing image.
        size (int): Border size.
        value (int): Value to fill the border with.
    
    Returns:
        Array: Image array.
    '''
    image[0:size, :] = value
    image[(-1)*size:, :] = value
    image[:, 0:size] = value
    image[:, (-1)*size:] = value
    return image

    
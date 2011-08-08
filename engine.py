import ctypes as ct
import os
import os.path

class matlab(object):
  def __init__(self, matlab_path):
    """Access the MATLAB C/C++ APIs.

    This class provides raw access to the C/C++ APIs.  It'll probably be
    more helpful to use a higher-level object.  Also provides some
    helpful functions to programs trying to move data back and forth
    between MATLAB and Python.

    """
    self.matlab_path = matlab_path

    self.__setup_ctypes()

  def __arch(self):
    mexext_path = os.path.sep.join( \
        ( self.matlab_path, "bin", "mexext" ) )
    mexext_output = os.popen(mexext_path).read()

    # FIXME this almost certainly won't work on other platforms
    conv = { "mexa64":"glnxa64" }

    return conv[mexext_output.strip()]

  def __setup_ctypes(self):
    arch = self.__arch()

    self.__setup_eng(arch)
    self.__setup_mx(arch)

    mex_dll_path = os.path.sep.join( \
        (self.matlab_path, "bin", arch,
        "libmex.so" ) )
    self.__mex = ct.cdll.LoadLibrary(mex_dll_path)

  def __result_check(self, predicate):
    def to_return(result, func, args):
      if not predicate(result):
        raise Exception("error calling %s with args %s" % (func, args))
      else:
        return result
    return to_return

  def __setup_eng(self, arch):
    eng_dll_path = os.path.sep.join( \
        ( self.matlab_path, "bin", arch,
        "libeng.so" ) )
    self.__eng = ct.cdll.LoadLibrary(eng_dll_path)

    self.engOpen = self.__eng.engOpen
    self.engOpen.restype = ct.c_void_p
    self.engOpen.argtypes = [ ct.c_char_p ]
    self.engOpen.errcheck = self.__result_check(lambda x: x != 0)

    self.engClose = self.__eng.engClose
    self.engClose.restype = ct.c_int
    self.engClose.argtypes = [ ct.c_void_p ]
    self.engClose.errcheck = self.__result_check( \
        lambda x: x == 0 )

    self.engEvalString = self.__eng.engEvalString
    self.engEvalString.restype = ct.c_int
    self.engEvalString.argtypes = [ ct.c_void_p, ct.c_char_p ]
    self.engEvalString.errcheck = self.__result_check( \
        lambda x: x == 0 )

    self.engGetVariable = self.__eng.engGetVariable
    self.engGetVariable.restype = ct.c_void_p
    self.engGetVariable.argtypes = [ ct.c_void_p, ct.c_char_p ]
    self.engGetVariable.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.engPutVariable = self.__eng.engPutVariable
    self.engPutVariable.restype = ct.c_int
    self.engPutVariable.argtypes = [ ct.c_void_p, ct.c_char_p,
        ct.c_void_p ]
    self.engPutVariable.errcheck = self.__result_check( \
        lambda x: x == 0 )

  def __setup_mx(self, arch):
    mx_dll_path = os.path.sep.join( \
        (self.matlab_path, "bin", arch,
        "libmat.so" ) )
    self.__mx = ct.cdll.LoadLibrary(mx_dll_path)

    # a few enumerations (optimistic guesses from the header files)

    # mxComplexity
    self.mxREAL = 0
    self.mxCOMPLEX = 1

    # mxClassID 
    self.mxUNKNOWN_CLASS = 0
    self.mxCELL_CLASS = 1
    self.mxSTRUCT_CLASS = 2
    self.mxLOGICAL_CLASS = 3
    self.mxCHAR_CLASS = 4
    self.mxVOID_CLASS = 5
    self.mxDOUBLE_CLASS = 6
    self.mxSINGLE_CLASS = 7
    self.mxINT8_CLASS = 8
    self.mxUINT8_CLASS = 9
    self.mxINT16_CLASS = 10
    self.mxUINT16_CLASS = 11
    self.mxINT32_CLASS = 12
    self.mxUINT32_CLASS = 13
    self.mxINT64_CLASS = 14
    self.mxUINT64_CLASS = 15
    self.mxFUNCTION_CLASS = 16
    self.mxOPAQUE_CLASS = 17
    self.mxOBJECT_CLASS = 18

    # many, many function bindings

    self.mxAddField = self.__mx.mxAddField
    self.mxAddField.restype = ct.c_int
    self.mxAddField.argtypes = [ ct.c_void_p, ct.c_char_p ]
    self.mxAddField.errcheck = self.__result_check( \
        lambda x: x != -1 )

    self.mxCreateCellArray = self.__mx.mxCreateCellArray
    self.mxCreateCellArray.restype = ct.c_void_p
    self.mxCreateCellArray.argtypes = [ ct.c_size_t,
        ct.POINTER(ct.c_size_t) ]
    self.mxCreateCellArray.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxCreateCellMatrix = self.__mx.mxCreateCellMatrix
    self.mxCreateCellMatrix.restype = ct.c_void_p
    self.mxCreateCellMatrix.argtypes = [ ct.c_size_t, ct.c_size_t ]
    self.mxCreateCellMatrix.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxCreateCharArray = self.__mx.mxCreateCharArray
    self.mxCreateCharArray.restype = ct.c_void_p
    self.mxCreateCharArray.argtypes = [ ct.c_size_t,
        ct.POINTER(ct.c_size_t) ]
    self.mxCreateCharArray.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxCreateCharMatrixFromString = \
        self.__mx.mxCreateCharMatrixFromStrings
    self.mxCreateCharMatrixFromString.restype = ct.c_void_p
    self.mxCreateCharMatrixFromString.argtypes = \
        [ ct.c_size_t, ct.POINTER(ct.c_char_p) ]
    self.mxCreateCharMatrixFromString.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxCreateDoubleMatrix = self.__mx.mxCreateDoubleMatrix
    self.mxCreateDoubleMatrix.restype = ct.c_void_p
    self.mxCreateDoubleMatrix.argtypes = \
        [ ct.c_size_t, ct.c_size_t, ct.c_int ]
    self.mxCreateDoubleMatrix.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxCreateDoubleScalar = self.__mx.mxCreateDoubleScalar
    self.mxCreateDoubleScalar.restype = ct.c_void_p
    self.mxCreateDoubleScalar.argtypes = [ ct.c_double ]
    self.mxCreateDoubleScalar.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxCreateLogicalArray = self.__mx.mxCreateLogicalArray
    self.mxCreateLogicalArray.restype = ct.c_void_p
    self.mxCreateLogicalArray.argtypes = [ ct.c_size_t,
        ct.POINTER( ct.c_size_t ) ]
    self.mxCreateLogicalArray.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxCreateLogicalMatrix = self.__mx.mxCreateLogicalMatrix
    self.mxCreateLogicalMatrix.restype = ct.c_void_p
    self.mxCreateLogicalMatrix.argtypes = [ ct.c_size_t, ct.c_size_t ]
    self.mxCreateLogicalMatrix.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxCreateLogicalScalar = self.__mx.mxCreateLogicalScalar
    self.mxCreateLogicalScalar.restype = ct.c_void_p
    self.mxCreateLogicalScalar.argtypes = [ ct.c_bool ]
    self.mxCreateLogicalScalar.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxCreateNumericArray = self.__mx.mxCreateNumericArray
    self.mxCreateNumericArray.restype = ct.c_void_p
    self.mxCreateNumericArray.argtypes = [ ct.c_size_t,
        ct.POINTER(ct.c_size_t), ct.c_int, ct.c_int ]
    self.mxCreateNumericArray.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxCreateNumericMatrix = self.__mx.mxCreateNumericMatrix
    self.mxCreateNumericMatrix.restype = ct.c_void_p
    self.mxCreateNumericMatrix.argtypes = [ ct.c_size_t,
        ct.c_size_t, ct.c_int, ct.c_int ]
    self.mxCreateNumericMatrix.errcheck = self.__result_check( \
        lambda x: x != 0)

    self.mxCreateSparse = self.__mx.mxCreateSparse
    self.mxCreateSparse.restype = ct.c_void_p
    self.mxCreateSparse.argtypes = [ ct.c_size_t, ct.c_size_t,
        ct.c_size_t, ct.c_int ]
    self.mxCreateSparse.errcheck = self.__result_check( \
        lambda x: x != 0)

    self.mxCreateSparseLogicalMatrix = self.__mx.mxCreateSparseLogicalMatrix
    self.mxCreateSparseLogicalMatrix.restype = ct.c_void_p
    self.mxCreateSparseLogicalMatrix.argtypes = [ ct.c_size_t,
        ct.c_size_t, ct.c_size_t ]
    self.mxCreateSparseLogicalMatrix.errcheck = self.__result_check( \
        lambda x: x != 0)

    self.mxCreateString = self.__mx.mxCreateString
    self.mxCreateString.restype = ct.c_void_p
    self.mxCreateString.argtypes = [ ct.c_char_p ]
    self.mxCreateString.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxCreateStructArray = self.__mx.mxCreateStructArray
    self.mxCreateStructArray.restype = ct.c_void_p
    self.mxCreateStructArray.argtypes = [ ct.c_size_t, 
        ct.POINTER(ct.c_size_t), ct.c_int, 
        ct.POINTER(ct.c_char_p) ]
    self.mxCreateStructArray.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxCreateStructMatrix = self.__mx.mxCreateStructMatrix
    self.mxCreateStructMatrix.restype = ct.c_void_p
    self.mxCreateStructMatrix.argtypes = [ ct.c_size_t,
        ct.c_size_t, ct.c_int, 
        ct.POINTER(ct.c_char_p) ]
    self.mxCreateStructMatrix.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxDestroyArray = self.__mx.mxDestroyArray
    self.mxDestroyArray.restype = None
    self.mxDestroyArray.argtypes = [ ct.c_void_p ]

    self.mxDuplicateArray = self.__mx.mxDuplicateArray
    self.mxDuplicateArray.restype = ct.c_void_p
    self.mxDuplicateArray.argtypes = [ ct.c_void_p ]
    self.mxDuplicateArray.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxGetCell = self.__mx.mxGetCell
    self.mxGetCell.restype = ct.c_void_p
    self.mxGetCell.argtypes = [ ct.c_void_p, ct.c_size_t ]
    self.mxGetCell.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxGetChars = self.__mx.mxGetChars
    self.mxGetChars.restype = ct.POINTER(ct.c_uint16)
    self.mxGetChars.argtypes = [ ct.c_void_p ]
    self.mxGetChars.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxGetClassID = self.__mx.mxGetClassID
    self.mxGetClassID.restype = ct.c_int
    self.mxGetClassID.argtypes = [ ct.c_void_p ]

    # can't get this one to not crash
    #self.mxGetClassName = self.__mx.mxGetClassName
    #self.mxGetClassName.restype = ct.c_char_p
    #self.mxGetClassID.argtypes = [ ct.c_void_p ]

    self.mxGetData = self.__mx.mxGetData
    self.mxGetData.restype = ct.c_void_p
    self.mxGetData.argtypes = [ ct.c_void_p ]
    self.mxGetData.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxGetDimensions = self.__mx.mxGetDimensions
    self.mxGetDimensions.restype = ct.POINTER(ct.c_size_t)
    self.mxGetDimensions.argtypes = [ ct.c_void_p ]
    self.mxGetDimensions.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxGetField = self.__mx.mxGetField
    self.mxGetField.restype = ct.c_void_p
    self.mxGetField.argtypes = [ ct.c_void_p, ct.c_size_t,
        ct.c_char_p ]
    self.mxGetField.errcheck = self.__result_check( \
        lambda x: x != 0)

    self.mxGetFieldByNumber = self.__mx.mxGetFieldByNumber
    self.mxGetFieldByNumber.restype = ct.c_void_p
    self.mxGetFieldByNumber.argtypes = [ ct.c_void_p, ct.c_size_t, 
        ct.c_int ]
    self.mxGetFieldByNumber.errcheck = self.__result_check( \
        lambda x: x != 0)

    self.mxGetFieldNameByNumber = self.__mx.mxGetFieldNameByNumber
    self.mxGetFieldNameByNumber.restype = ct.c_char_p
    self.mxGetFieldNameByNumber.argtypes = [ ct.c_void_p, ct.c_int ]

    self.mxGetFieldNumber = self.__mx.mxGetFieldNumber
    self.mxGetFieldNumber.restype = ct.c_int
    self.mxGetFieldNumber.argtypes = [ ct.c_void_p, ct.c_char_p ]
    self.mxGetFieldNumber.errcheck = self.__result_check( \
        lambda x: x != -1 )

    self.mxGetImagData = self.__mx.mxGetImagData
    self.mxGetImagData.restype = ct.c_void_p
    self.mxGetImagData.argtypes = [ ct.c_void_p ]
    self.mxGetImagData.errcheck = self.__result_check( \
        lambda x: x != -1 )

    self.mxGetIr = self.__mx.mxGetIr
    self.mxGetIr.restype = ct.POINTER(ct.c_size_t)
    self.mxGetIr.argtypes = [ ct.c_void_p ]
    self.mxGetIr.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxGetJc = self.__mx.mxGetJc
    self.mxGetJc.restype = ct.POINTER(ct.c_size_t)
    self.mxGetJc.argtypes = [ ct.c_void_p ]
    self.mxGetJc.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxGetLogicals = self.__mx.mxGetLogicals
    self.mxGetLogicals.restype = ct.POINTER(ct.c_bool)
    self.mxGetLogicals.argtypes = [ ct.c_void_p ]
    self.mxGetLogicals.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxGetNumberOfDimensions = self.__mx.mxGetNumberOfDimensions
    self.mxGetNumberOfDimensions.restype = ct.c_size_t
    self.mxGetNumberOfDimensions.argtypes = [ ct.c_void_p ]

    self.mxGetNumberOfElements = self.__mx.mxGetNumberOfElements
    self.mxGetNumberOfElements.restype = ct.c_size_t
    self.mxGetNumberOfElements.argtypes = [ ct.c_void_p ]

    self.mxGetNumberOfFields = self.__mx.mxGetNumberOfFields
    self.mxGetNumberOfFields.restype = ct.c_int
    self.mxGetNumberOfFields.argtypes = [ ct.c_void_p ]

    self.mxGetNzmax = self.__mx.mxGetNzmax
    self.mxGetNzmax.restype = ct.c_size_t
    self.mxGetNzmax.argtypes = [ ct.c_void_p ]
    
    self.mxGetProperty = self.__mx.mxGetProperty
    self.mxGetProperty.restype = ct.c_void_p
    self.mxGetProperty.argtypes = [ ct.c_void_p, 
        ct.POINTER(ct.c_size_t), ct.c_char_p ]
    self.mxGetProperty.errcheck = self.__result_check( \
        lambda x: x != 0 )

    self.mxGetString = self.__mx.mxGetString
    self.mxGetString.restype = ct.c_int
    self.mxGetString.argtypes = [ ct.c_void_p, ct.c_char_p, ct.c_size_t ]
    self.mxGetString.errcheck = self.__result_check( \
        lambda x: x == 0)

    self.mxIsSparse = self.__mx.mxIsSparse
    self.mxIsSparse.restype = ct.c_bool
    self.mxIsSparse.argtypes = [ ct.c_void_p ]

    self.mxRemoveField = self.__mx.mxRemoveField
    self.mxRemoveField.restype = None
    self.mxRemoveField.argtypes = [ ct.c_void_p, ct.c_int ]

    self.mxSetCell = self.__mx.mxSetCell
    self.mxSetCell.restype = None
    self.mxSetCell.argtypes = [ ct.c_void_p, ct.c_size_t, ct.c_void_p ]

    self.mxSetClassName = self.__mx.mxSetClassName
    self.mxSetClassName.restype = ct.c_int
    self.mxSetClassName.argtypes = [ ct.c_void_p, ct.c_char_p ]
    self.mxSetClassName.errcheck = self.__result_check( \
        lambda x: x == 0 )

    self.mxSetDimensions = self.__mx.mxSetDimensions
    self.mxSetDimensions.restype = ct.c_int
    self.mxSetDimensions.argtypes = [ ct.c_void_p, 
        ct.POINTER(ct.c_size_t), ct.c_size_t ]
    self.mxSetDimensions.errcheck = self.__result_check( \
        lambda x: x == 0 )

    self.mxSetField = self.__mx.mxSetField
    self.mxSetField.restype = None
    self.mxSetField.argtypes = [ ct.c_void_p, ct.c_size_t,
        ct.c_char_p, ct.c_void_p ]

    self.mxSetFieldByNumber = self.__mx.mxSetFieldByNumber
    self.mxSetFieldByNumber.restype = None
    self.mxSetFieldByNumber.argtypes = [ ct.c_void_p, ct.c_size_t,
        ct.c_int, ct.c_void_p ]

    self.mxSetIr = self.__mx.mxSetIr
    self.mxSetIr.restype = None
    self.mxSetIr.argtypes = [ ct.c_void_p, ct.POINTER(ct.c_size_t) ]

    self.mxSetJc = self.__mx.mxSetJc
    self.mxSetJc.restype = None
    self.mxSetJc.argtypes = [ ct.c_void_p, ct.POINTER(ct.c_size_t) ]

    self.mxSetNzmax = self.__mx.mxSetNzmax
    self.mxSetNzmax.restype = None
    self.mxSetNzmax.argtypes = [ ct.c_void_p, ct.c_size_t ]

    self.mxSetProperty = self.__mx.mxSetProperty
    self.mxSetProperty.restype = None
    self.mxSetProperty.argtypes = [ ct.c_void_p, ct.c_size_t,
        ct.c_char_p, ct.c_void_p ]

class engine_function_proxy(object):
  def __init__(self, engine, name):
    self.engine = engine
    self.name = name

  def __call__(*args):
    pass

class engine(object):
  def __init__(self, matlab_path):
    """MATLAB engine abstraction.
    
    """
    self.api = matlab(matlab_path)
    self.__function_proxies = {}

  def function_proxy(self, name):
    if name in self.__function_proxies.keys():
      return self.__function_proxies[name]
    else: 
      f = engine_function_proxy(self, name)
      self.__function_proxies[name] = f
      return f

  def eval(self, text):
    pass

  def __call__(self, text):
    return self.eval(text)


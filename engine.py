import ctypes as ct
import os
import os.path

class matlab(object):
  def __init__(self, matlab_path):
    """Access the MATLAB C API.

    This class provides raw access to the C/C++ APIs.  It'll probably be
    more helpful to use a higher-level object.  Also provides some
    helpful functions to programs trying to move data back and forth
    between MATLAB and Python.

    """
    self.matlab_path = matlab_path

    self.__setup_ctypes()

    # define some helpers for conversion
    import numpy as np
    self.__matlab2numpy = { self.mxLOGICAL_CLASS: ct.c_bool,
        self.mxCHAR_CLASS: ct.c_char,
        self.mxDOUBLE_CLASS: ct.c_double,
        self.mxSINGLE_CLASS: ct.c_float,
        self.mxINT8_CLASS: ct.c_int8,
        self.mxUINT8_CLASS: ct.c_uint8,
        self.mxINT16_CLASS: ct.c_int16,
        self.mxUINT16_CLASS: ct.c_uint16,
        self.mxINT32_CLASS: ct.c_int32,
        self.mxUINT32_CLASS: ct.c_uint32,
        self.mxINT64_CLASS: ct.c_int64,
        self.mxUINT64_CLASS: ct.c_uint64 }
    self.__numpy2matlab = { \
        np.bool_ : self.mxLOGICAL_CLASS,
        np.double : self.mxDOUBLE_CLASS,
        np.float64 : self.mxDOUBLE_CLASS,
        np.float : self.mxSINGLE_CLASS,
        np.float32 : self.mxSINGLE_CLASS,
        np.single : self.mxSINGLE_CLASS,
        np.int8 : self.mxINT8_CLASS,
        np.uint8 : self.mxUINT8_CLASS,
        np.int16 : self.mxINT16_CLASS,
        np.uint16 : self.mxUINT16_CLASS,
        np.int32 : self.mxINT32_CLASS,
        np.uint32 : self.mxUINT32_CLASS,
        np.int64 : self.mxINT64_CLASS,
        np.uint64 : self.mxUINT64_CLASS }

  def classID_to_dtype(self, classID):
    return self.__matlab2numpy[classID]

  def dtype_to_classID(self, dtype):
    return self.__numpy2matlab[dtype.type]

  def index_to_coords(self, dims, index):
    """Given an object with dimensions dims, and an index number, find
    the (base-0) coordinates into that object.
    
    """
    if not hasattr(dims, "__len__"): 
      return index
    to_return = [0]*len(dims)
    div = reduce(lambda x,y:x*y, dims[:-1])
    for d in xrange(len(dims)-1, -1, -1):
      to_return[d] = int(index / div)
      index -= to_return[d] * div
      div /= dims[d]
    return to_return

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
        "libmx.so" ) )
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

    self.mxIsComplex = self.__mx.mxIsComplex
    self.mxIsComplex.restype = ct.c_bool
    self.mxIsComplex.argtypes = [ ct.c_void_p ]

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

    self.mxCreateCharMatrixFromStrings = \
        self.__mx.mxCreateCharMatrixFromStrings
    self.mxCreateCharMatrixFromStrings.restype = ct.c_void_p
    self.mxCreateCharMatrixFromStrings.argtypes = \
        [ ct.c_size_t, ct.POINTER(ct.c_char_p) ]
    self.mxCreateCharMatrixFromStrings.errcheck = self.__result_check( \
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

    self.mxFree = self.__mx.mxFree
    self.mxFree.restype = None
    self.mxFree.argtypes = [ ct.c_void_p ]

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
  def __init__(self, engine, name, docs="", is_handle=False):
    self.engine = engine
    self.name = name
    self.is_handle = is_handle
    self.docs = docs
    self.__doc__ = self.docs
    self.is_handle = is_handle

  def __expecting(self):
    # scary devil trick to figure out the number of desired arguments to
    # return.  this comes from http://code.activestate.com/recipes/284742
    # and it makes me sorry to use it.
    import dis
    import sys
    f = sys._getframe().f_back.f_back
    i = f.f_lasti + 3
    bytecode = f.f_code.co_code
    instruction = ord(bytecode[i])
    while True:
        if instruction == dis.opmap['DUP_TOP']:
            if ord(bytecode[i + 1]) == dis.opmap['UNPACK_SEQUENCE']:
                return ord(bytecode[i + 2])
            i += 4
            instruction = ord(bytecode[i])
            continue
        if instruction == dis.opmap['STORE_NAME']:
            return 1
        if instruction == dis.opmap['UNPACK_SEQUENCE']:
            return ord(bytecode[i + 1])
        return 0

  def __call__(self, *args):
    nargout = self.__expecting()

    # get a list of temporary names for the arguments and copy them
    # across to MATLAB
    temp_names = [ self.engine.temp_name() for arg in args ]
    for (temp_name, arg) in zip(temp_names, args):
      self.engine.set_variable(temp_name, arg)

    # get a list of temporary names for the return values
    out_names = [ self.engine.temp_name() for i in xrange(nargout) ]

    # make the call
    out_names_str = ", ".join(out_names)
    in_names_str = ", ".join(temp_names)
    eval_str = None
    if nargout > 0:
      eval_str =  "[%s] = %s(%s);" % (out_names_str, self.name, in_names_str)
    else:
      eval_str = "%s(%s);" % (self.name, in_names_str)
    self.engine(eval_str)

    # get results from MATLAB and return
    to_return = tuple([ self.engine.get_variable(argname) \
        for argname in out_names ])
    if nargout == 0:
      return
    elif nargout == 1:
      return to_return[0]
    else:
      return to_return

class engine(object):
  def __init__(self, matlab_path):
    """MATLAB engine abstraction.
    
    """
    self.api = matlab(matlab_path)
    self.__function_proxies = {}
    self.__mat2py_converters = {}
    self.__py2mat_converters = {}

    self.__engine_pointer = None
    self.__engine_pointer = self.api.engOpen("")

    self.__tmp_num = 0

    self.register_mat2py_converter("struct", self.__mat2py_struct)
    self.register_mat2py_converter("cell", self.__mat2py_cell)
    self.register_mat2py_converter("function_handle",
        self.__mat2py_func)
    self.register_mat2py_converter("strum", self.__mat2py_strum)

  def __del__(self):
    if self.__engine_pointer is not None:
      self.api.engClose(self.__engine_pointer)

  def register_mat2py_converter(self, class_name, func):
    self.__mat2py_converters[class_name] = func

  def register_py2mat_converter(self, klass, func):
    self.__py2mat_converters[klass] = func

  def temp_name(self):
    to_return = "matropylis_tmp%d" % self.__tmp_num
    self.__tmp_num += 1
    return to_return

  def __getattr__(self, name):
    return self.function_proxy(name)

  def function_proxy(self, name):
    if name in self.__function_proxies.keys():
      return self.__function_proxies[name]
    else: 
      # get docs
      docs_tmp_name = self.temp_name()
      self("%s = help('%s')" % (docs_tmp_name, name))
      docs = self.get_variable(docs_tmp_name)
      f = engine_function_proxy(self, name, docs, is_handle=False)
      self.__function_proxies[name] = f
      return f

  def eval(self, text):
    self.api.engEvalString(self.__engine_pointer, text)

  def __call__(self, text):
    return self.eval(text)

  def __set_string_variable(self, name, value):
    array_ptr = None
    try:
      array_ptr = self.api.mxCreateCharMatrixFromStrings(1, 
          ct.pointer(ct.c_char_p(value)))
      self.api.engPutVariable(self.__engine_pointer, name, array_ptr)
    except Exception, e:
      raise e
    finally:
      if array_ptr is not None and array_ptr != 0:
        self.api.mxDestroyArray(array_ptr)

  def __set_dict_variable(self, name, value):
    # we _could_ construct a struct object using the C api and move it
    # across all at once, but we would lose type checking.  instead, we
    # resort to the (possibly less satisfying) process of recursively
    # pushing across variables
    raise Exception("not implemented")
    pass

  def __set_scalar_variable(self, name, value):
    # this one's easy :-)
    import numpy as np
    # argh, this is a touch annoying
    if isinstance(value, bool) or isinstance(value, np.bool_):
      # Python says True/False, MATLAB says true/false
      if value:
        self("%s = true" % name)
      else:
        self("%s = false" % name)

    else:
      # rely on Python's object->string conversion
      self("%s = %s" % (name, value))

  def __set_vector_variable(self, name, value):
    import numpy as np
    vec_ptr = None
    try:
      # dimension stuff
      ndim = len(value.shape)
      dims = (ct.c_size_t * ndim)()
      for i in xrange(ndim): 
        dims[i] = value.shape[i]

      # determine if vector is complex
      is_complex = not np.allclose(value.imag, 0)
      complexity_flag = \
        self.api.mxCOMPLEX if is_complex else self.api.mxREAL

      # classID shizz
      classID = self.api.dtype_to_classID(value.dtype)
      ctypeID = self.api.classID_to_dtype(classID)

      # MATLAB provides different APIs for creating numerical and
      # logical arrays.  we'll play their game.
      if classID == self.api.mxLOGICAL_CLASS:
        raise TypeError("boolean arrays not quite supported yet")
        ptr = ct.cast( dims, ct.POINTER(ct.c_size_t) )
        vec_ptr = self.api.mxCreateLogicalArray( ndim,
            ptr )
      else:
        ptr = ct.cast( dims, ct.POINTER(ct.c_size_t) )
        vec_ptr = self.api.mxCreateNumericArray( ndim,
            ptr, classID, complexity_flag )

      # copy data into place
      real_dst_ptr = ct.cast(self.api.mxGetData(vec_ptr), 
          ct.POINTER(ctypeID))
      imag_dst_ptr = ct.cast(self.api.mxGetImagData(vec_ptr),
          ct.POINTER(ctypeID))

      # potentially very slow, but at least it works
      # TODO figure out how to do this with memmove
      for (i, r, c) in zip(xrange(value.size), 
          value.real.flat, value.imag.flat):
        real_dst_ptr[i] = r
        if is_complex: imag_dst_ptr[i] = c

      # push data to MATLAB
      self.api.engPutVariable(self.__engine_pointer, name, vec_ptr)

    except Exception, e:
      raise e
    finally:
      if vec_ptr is not None and vec_ptr != 0:
        self.api.mxDestroyArray(vec_ptr)

  def __set_cell_variable(self, name, value):
    raise Exception("writing cells not implemented... yet.")
    pass

  def __set_array_variable(self, name, value):
    if value.dtype == object:
      # potentially heterogeneous ndarray; looks like a job for a MATLAB
      # cell
      self.__set_cell_variable(name, value)
    else:
      self.__set_vector_variable(name, value)

  def set_variable(self, name, value):
    # there's a somewhat limited number of types of variables we can
    # push to MATLAB, and it seems that we need to resort to heuristics
    # in order to figure out how to dispatch an arbitrary type.

    # string check (string -> string)
    if isinstance(value, str):
      self.__set_string_variable(name, value)
      return

    # see if we're dealing with a dict (dict -> struct)
    if isinstance(value, dict):
      self.__set_dict_variable(name, value)
      return

    # what if we're trying to pass a function?
    # TODO come up with a nicer way to write this
    if isinstance(value, self.set_variable.__class__):
      raise TypeError("passing function handles to MATLAB not supported")

    # attempt to make an array out of it
    import numpy as np
    try:
      array = np.array(value, order='F')
      if len(array.shape) == 0:
        # actually dealing with a scalar
        self.__set_scalar_variable(name, array.flat[0])
        return
      elif len(array.shape) == 1:
        # automatically promote to Nx1 vector
        array.shape = (array.shape[0],1)

      self.__set_array_variable(name, array)
      return
    except Exception, e:
      print "conversion error: ", e.__class__, e

    # see if some brave soul has added a converter for us
    if value.__class__ in self.__py2mat_converters.keys():
      # TODO figure out the right way to do this esp. the function
      # signature
      raise Exception("user-defined py2mat converters not done yet")
      self.__py2mat_converters[value.__class__](name, value)

    # we couldn't find a way to make the conversion to MATLAB... :-(
    raise TypeError("couldn't convert '%s' to MATLAB" % value)

  def get_variable(self, name):
    # first, we want to know about they variable we're pulling across.
    # sadly, at this level we can't rely on the nice function_proxy
    # machinery 
    tmp_name = self.temp_name()
    self.eval("%s = whos('%s')" % (tmp_name, name))

    whos_ptr = None
    class_name_ptr = None
    try:
      whos_ptr = self.api.engGetVariable(self.__engine_pointer, tmp_name)

      # the most important part about the whos structure is the "class"
      # field, which contains a text version of the class of the object 
      # we're trying to pull across, e.g., "double" or "function_handle"
      field_num = self.api.mxGetFieldNumber(whos_ptr, "class")
      class_name_ptr = self.api.mxGetFieldByNumber(whos_ptr, 0,
          field_num)

      num_chars = self.api.mxGetNumberOfElements(class_name_ptr)

      name_buf_class = ct.c_char * (num_chars + 1)
      name_buf = name_buf_class()

      self.api.mxGetString(class_name_ptr, name_buf, num_chars+1)
      class_name = name_buf.value

      return self.__get_variable_with_class_name(name, class_name)
    except Exception, e:
      import traceback
      traceback.print_exc()
      raise e
    finally:
      if whos_ptr is not None and whos_ptr != 0:
        self.api.mxDestroyArray(whos_ptr)

  def __mat2py_strum(self, var_name, class_name):
    assert(class_name == "strum")
    tmp_name = self.temp_name()
    self("%s = struct(%s);" % (tmp_name, var_name))
    to_return = self.get_variable(tmp_name)
    # mark this as a strum ... ?
    return to_return

  def __get_variable_with_class_name(self, var_name, class_name):
    print var_name, class_name
    # check for special handlers
    if class_name in self.__mat2py_converters:
      return self.__mat2py_converters[class_name](var_name, class_name)
    else:
      return self.__get_variable_normal(var_name, class_name)

  def __mat2py_func(self, var_name, class_name):
    proxy = engine_function_proxy(self, var_name, 
      docs="proxy for MATLAB function handle -- no docs",
      is_handle = True)
    return proxy

  def __mat2py_cell(self, var_name, class_name):
    assert(class_name == "cell")
    # we need to get the size of the cell without attempting to copy
    # over the cell itself
    size_tmp_name = self.temp_name()
    self("%s = size(%s)" % (size_tmp_name, var_name))
    size = self.get_variable(size_tmp_name)

    import numpy as np
    to_return = np.empty(dtype=object, shape=size)
    for i in xrange(to_return.size):
      elem_tmp_name = self.temp_name()
      coords_base0 = self.api.index_to_coords(size, i)
      coords_base1_str = None
      if hasattr(coords_base0, "__len__"):
        coords_base1 = [ x+1 for x in coords_base0 ]
        coords_base1_str = ", ".join(coords_base1)
      else:
        coords_base1_str = "%s" % (coords_base0 + 1)

      self("%s = %s{%s}" % (elem_tmp_name, var_name, coords_base1_str))
      to_return.flat[i] = self.get_variable(elem_tmp_name)

    return to_return.T

  def __mat2py_struct(self, var_name, class_name):
    assert(class_name == "struct")
    # in order to avoid attempting to copy over e.g., function handles,
    # we need to specifically get the names of the members of the struct
    field_names_tmp = self.temp_name()
    self("%s = fieldnames(%s)" % (field_names_tmp, var_name))

    # we know this is a cell of strings, so we can safely directly copy
    # it over
    field_names_ptr = None
    try:
      # get the field names ptr and the number of names
      field_names_ptr = self.api.engGetVariable(self.__engine_pointer,
          field_names_tmp)
      num_names = self.api.mxGetDimensions(field_names_ptr)[0]

      # pull across each by building a dictionary
      to_return = {}
      for name_id in xrange(num_names):
        field_tmp_name = self.temp_name()
        self("%s = %s{%d}" % (field_tmp_name, field_names_tmp, name_id+1))
        field_name = self.get_variable(field_tmp_name)

        field_data_tmp_name = self.temp_name()
        print "getting %s" % field_name
        self("%s = %s.%s" % (field_data_tmp_name, var_name, field_name))
        to_return[field_name] = self.get_variable(field_data_tmp_name)

      return to_return
    except Exception, e:
      raise e
    finally:
      if field_names_ptr is not None and field_names_ptr != 0:
        self.api.mxDestroyArray(field_names_ptr)

    raise TypeError("not quite supported yet")

  def __get_variable_normal(self, var_name, class_name):
    # handler for loading dense and sparse arrays of fundamental types
    ptr = None
    try:
      ptr = self.api.engGetVariable(self.__engine_pointer, var_name)

      # get a bit of helpful info:
      # - sparsity:
      is_sparse = self.api.mxIsSparse(ptr)

      # - dimensions:
      num_dimensions = self.api.mxGetNumberOfDimensions(ptr)
      dims_buf = self.api.mxGetDimensions(ptr)
      dims = [ dims_buf[i] for i in xrange(num_dimensions) ]

      # - classID, numpy datatype
      classID = self.api.mxGetClassID(ptr)
      is_string = classID == self.api.mxCHAR_CLASS
      numpy_dtype = self.api.classID_to_dtype(classID)

      # - real/complex?
      is_complex = self.api.mxIsComplex(ptr)

      if is_string:
        # dense (MATLAB's limitation) string
        import numpy as np

        num_chars = self.api.mxGetNumberOfElements(ptr)
        char_buf = (ct.c_char * (num_chars+1))()

        self.api.mxGetString(ptr, char_buf, num_chars+1)

        dims[1] = 1
        dims = tuple(dims)
        tmp = np.ctypeslib.as_array(ct.pointer(char_buf),
            shape=dims).copy()

        vals = []
        for r in xrange(dims[0]):
          vals.append( str(tmp[r,0]).strip() )
        to_ret = np.array(vals)

        if to_ret.shape[0] == 1:
          # just one string
          return to_ret[0]
        else:
          return to_ret
      elif is_sparse:
        # sparse, non-string
        from scipy.sparse import csc_matrix
        import numpy as np
        dims = tuple(dims)

        row_ind_ptr = self.api.mxGetIr(ptr)
        col_ptr = self.api.mxGetJc(ptr)
        data_addr = self.api.mxGetData(ptr)

        num_entries = self.api.mxGetNzmax(ptr)
        sparse_shape = (num_entries,)
        
        data_ptr = ct.pointer(numpy_dtype.from_address(data_addr))

        row_ind = np.ctypeslib.as_array(row_ind_ptr, shape=sparse_shape)
        row_ind = np.array(row_ind, dtype=np.int, copy=True)
        col = np.ctypeslib.as_array(col_ptr, shape=(dims[1]+1,))
        col = np.array(col, dtype=np.int, copy=True)
        col[-1] = num_entries
        data = np.ctypeslib.as_array(data_ptr,
            shape=sparse_shape).copy()

        if is_complex:
          imag_addr = self.api.mxGetImagData(ptr)
          imag_ptr = ct.pointer(numpy_dtype.from_address(imag_addr))
          imag = np.ctypeslib.as_array(imag_ptr,
              shape=sparse_shape).copy()
          data = data + 1j*imag

        return csc_matrix( (data, row_ind, col), dims )

      else:
        # dense, non-string
        import numpy as np
        dims = tuple(dims)

        real_addr = self.api.mxGetData(ptr)
        if real_addr == None:
          # we attempted to get an empty array
          print "empty"
          return np.empty(dtype=numpy_dtype, shape=())

        real_ptr = ct.pointer(numpy_dtype.from_address(real_addr))
        real = np.ctypeslib.as_array(real_ptr, shape=dims)

        if is_complex:
          imag_addr = self.api.mxGetImagData(ptr)
          imag_ptr = ct.pointer(numpy_dtype.from_address(imag_addr))
          imag = np.ctypeslib.as_array(imag_ptr, shape=dims)
          real = 1j*imag + real

        real = np.array(real, order="F", copy=True)
        if len(real) == 1:
          return real.flat[0]
        else:
          return real
    except Exception, e:
      raise e
    finally:
      if ptr is not None and ptr != 0:
        self.api.mxDestroyArray(ptr)


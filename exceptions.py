class NPZCorruptException(Exception):
    """NPZCorruptException: raised when an npz file is in an invalid format
    Args:
        Exception: Inherits from the base exception class
    """
    def __init__(self, msg="The NPZ file was corrupted."):
        self.msg=msg
        super().__init__(self.msg)
    def __str__(self):
        return (f"{self.msg}")

class IncorrectFileTypeException(Exception):
    """IncorrectFileTypeException: raised when a file is not a .npz type of file.
    Args:
        Exception: Inherits from the base exception class
    """
    def __init__(self,filename="", msg="Invalid file type. Only npz files allowed."):
        self.msg=msg
        self.filename=filename
        super().__init__(self.msg)
    def __str__(self):
        if self.filename != "":
           return (f"The file : {self.filename} is an invalid file type. It must be npz.") 
        return (f"{self.msg}")

class EmptyFile(Exception):
    """EmptyFile: raised when a there are no .npz files.
    Args:
        Exception: Inherits from the base exception class
    """
    def __init__(self, msg="No valid .npz files were provided."):
        self.msg=msg
        super().__init__(self.msg)
    def __str__(self):
        return (f"{self.msg}")


class UltimateException(Exception):
    """UltimateException: raised when a file the error is not recoverable forcing the program to quit.
    Args:
        Exception: Inherits from the base exception class
    """
    def __init__(self, msg="Unrecoverable error."):
        self.msg=msg
        super().__init__(self.msg)
    def __str__(self):
        return (f"{self.msg}")
from osgeo import gdal

class GdalErrorHandler(object):
    def __init__(self):
        self.err_level=gdal.CE_None
        self.err_no=0
        self.err_msg=''

    def handler(self, err_level, err_no, err_msg):
        self.err_level=err_level
        self.err_no=err_no
        self.err_msg=err_msg

if __name__=='__main__':

    err=GdalErrorHandler()
    handler=err.handler # Note don't pass class method directly or python segfaults
                        # due to a reference counting bug 
                        # http://trac.osgeo.org/gdal/ticket/5186#comment:4

    gdal.PushErrorHandler(handler)
    gdal.UseExceptions() #Exceptions will get raised on anything >= gdal.CE_Failure

    try:
        gdal.Error(gdal.CE_Warning,1,'gdal.CE_Warning warning')
    except Exception as e:
        print 'Operation raised an exception'
        print e
    else:
        print 'No exception'
        if err.err_level >= gdal.CE_Warning:
            raise RuntimeError(err.err_level, err.err_no, err.err_msg)
    finally:
        print err.err_level, err.err_no, err.err_msg
        gdal.PopErrorHandler()
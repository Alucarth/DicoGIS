# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function



import multiprocessing


class test_MP():
    """ """
    def read_featureClass(self, featureclass):
        """  """
        print(featureclass)
        print(len(featureclass))

        # end of function
        return


    def process(self, list_targets):
        """  """
        # create a pool to multi-process the features classes found
        pool = multiprocessing.Pool()
        print('\n\tpool_creation')
        pool.map(lambda:self.read_featureClass, list_targets)
        print('pool mapped')

        # Synchronize the main process with the job processes to ensure proper cleanup.
        pool.close()      
        pool.join()

        # end of function
        return

################################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS/)"""
    li_test = ['youpi','youhou','yahou','youplaboum']
    test_MP().process(li_test)
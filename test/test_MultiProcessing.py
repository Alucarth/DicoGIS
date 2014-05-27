# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals




import multiprocessing



def read_featureClass(featureclass):
    """  """
    print featureclass
    print len(featureclass)

    # end of function
    return


def main(list_targets):
    """  """
    # create a pool to multi-process the features classes found
    pool = multiprocessing.Pool()
    print('\n\tpool_creation')
    pool.map(read_featureClass, list_targets)
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
    multiprocessing.freeze_support()
    li_test = ['youpi','youhou','yahou','youplaboum']
    # main(li_test)

    # create a pool to multi-process the features classes found
    pool = multiprocessing.Pool()
    print('\n\tpool_creation')
    pool.map(read_featureClass, li_test)
    print('pool mapped')

    # Synchronize the main process with the job processes to ensure proper cleanup.
    pool.close()
    pool.join()

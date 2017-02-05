# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function
# -----------------------------------------------------------------------------
# Name:         OpenCatalog to Excel
# Purpose:      Get metadatas from an Isogeo OpenCatlog and store it into
#               an ordered dictionary
#
# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      14/08/2014
# Updated:      27/10/2015
# -----------------------------------------------------------------------------

# ############################################################################
# ######### Libraries #############
# #################################

# Standard library
from collections import OrderedDict  # Python 3 backported
import json
import logging
from math import ceil
import os
from urllib2 import Request, URLError, urlopen

# ############################################################################
# ######### Classes ###############
# #################################


class ReadIsogeoOpenCatalog():
    """Read an Isogeo OpenCatalog and store metadata into an ordered dictionary.

    see: http://www.isogeo.com
    """
    def __init__(self, url_catalog, lang, dico_mds):
        """
        url_catalog: should looks like to http://open.isogeo.com/s/SHARE_ID/TOKEN
        lang: fr or en
        dico_mds: dictionary to store metadata
        """
        # extract share identifier
        share_id = url_catalog.rsplit('/')[4]
        # extract security token
        share_token = url_catalog.rsplit('/')[5]

        # offset
        start = 0

        ## Checking lang parameter
        # preventing bad language standard used
        if len(lang) > 2:
            print("Language parameter has to be passed in 2 letters")
            return None
        else:
            pass
        # if language passed is not available, then force switch into English
        lang_available = ['en', 'fr']
        if lang.lower() not in lang_available:
            lang = 'fr'
            print("Language asked is not supported by the API.\nShould be one of: {0}.\nHas been automatically switched into English".format(', '.join(lang_available)))
        else:
            pass

        # formatting the request to the API
        search_req = Request('http://v1.api.isogeo.com/resources/search?ct={0}&s={1}&_limit=100&_lang={2}&_offset={3}'.format(share_token, share_id, lang, start))

        # testing request
        try:
            search_resp = urlopen(search_req)
            search_rez = json.load(search_resp)
        except URLError as e:
            print(e)

        if not search_rez:
            print("Request failed. Check your connection state.")
        else:
            pass

        # tags
        tags = search_rez.get('tags')
        dico_mds['tags'] = tags
        print(tags.keys())
        # getting different owners (= workgroups)
        dico_mds['owners'] = [tags.get(tag) for tag in tags.keys() if tag.startswith('owner')]
        # getting different SRS (=coordinate systems)
        dico_mds['srs'] = [tags.get(tag) for tag in tags.keys() if tag.startswith('coordinate-system')]

        # metadatas
        tot_results = search_rez.get('total')
        metadatas = search_rez.get('results')
        dico_mds['li_ids'] = [md.get('_id') for md in metadatas]

        # considering Isogeo API limit
        # see: https://docs.google.com/document/d/11dayY1FH1NETn6mn9Pt2y3n8ywVUD0DoKbCi9ct9ZRo/edit#heading=h.bg6le8mcd07z
        if tot_results > 100:
            # if API returned more than one page of results, let's get the rest!
            for idx in range(1, int(ceil(tot_results / 100)) + 1):
                start = idx * 100 + 1
                search_req = Request('http://v1.api.isogeo.com/resources/search?ct={0}&s={1}&_limit=100&_lang={2}&_offset={3}'.format(share_token, share_id, lang, start))
                print(search_req)
                try:
                    search_resp = urlopen(search_req)
                    search_rez = json.load(search_resp)
                except URLError as e:
                    print(e)
                metadatas.extend(search_rez.get('results'))
        else:
            pass
        dico_mds['resources'] = metadatas


# ############################################################################
# #### Stand alone program ########
# #################################

if __name__ == '__main__':
    """ standalone execution """
    # test variables
    url_catalog = "http://open.isogeo.com/s/ad6451f1f9ca405ca6f78fabf46aeb10/Bue0ySfhmGOPw33jHMyaJtcOM4MY0"
    lang = "fr"
    dico_md = OrderedDict()

    # testing class
    ReadIsogeoOpenCatalog(url_catalog, lang, dico_md)
    print("Worksgroups represented: " + unicode(dico_md.get('owners')))

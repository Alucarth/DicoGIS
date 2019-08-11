# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import absolute_import, print_function, unicode_literals

# -----------------------------------------------------------------------------
# Name:         DicoGIS
# Purpose:      Automatize the creation of a dictionnary of geographic data
#               contained in a folders structures.
#               It produces an Excel output file (.xlsx)
#
# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      14/02/2013
# Updated:      19/03/2017
#
# Licence:      GPL 3
# ------------------------------------------------------------------------------

# ##############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from Tkinter import PhotoImage, StringVar, Tk, VERTICAL
from ttk import Frame, Label, Separator

import logging
from os import path

# ##############################################################################
# ############ Globals ############
# #################################

# LOG
logger = logging.getLogger("DicoGIS")

# ##############################################################################
# ########## Classes ###############
# ##################################


class TabIsogeo(Frame):
    def __init__(self, parent, txt=dict(), dicogis_path="../../"):
        """Instanciating the output workbook."""
        self.parent = parent
        Frame.__init__(self)

        # ## GLOBAL ##
        self.app_metrics = StringVar(self)
        self.oc_msg = StringVar(self)
        self.url_input = StringVar(self)

        # logo
        ico_path = path.normpath(
            path.join(path.abspath(dicogis_path), "data/img/logo_isogeo.gif")
        )
        self.logo_isogeo = PhotoImage(master=self, file=ico_path)
        logo_isogeo = Label(self, borderwidth=2, image=self.logo_isogeo)

        # metrics
        self.app_metrics.set(
            "{} metadata in\n" "{} shares owned by\n" "{} workgroups.".format(10, 1, 2)
        )
        lb_app_metrics = Label(self, textvariable=self.app_metrics)

        # # OpenCatalog check
        # self.lb_input_oc = Label(self,
        #                          textvariable=self.oc_msg)

        # if len(self.shares_info[2]) != 0:
        #     logger.error("Any OpenCatalog found among the shares")
        #     self.oc_msg.set(_("{} shares don't have any OpenCatalog."
        #                       "\nAdd OpenCatalog to every share,"
        #                       "\nthen reboot isogeo2office.").format(len(self.shares_info[2])))
        #     self.msg_bar.set(_("Error: some shares don't have OpenCatalog"
        #                        "activated. Fix it first."))
        #     self.status_bar.config(foreground='Red')
        #     btn_open_shares = Button(self,
        #                              text=_("Fix the shares"),
        #                              command=lambda: self.utils.open_urls(self.shares_info[2]))
        #     status_launch = DISABLED
        # elif len(self.shares) != len(self.shares_info[1]):
        #     logger.error("More than one share by workgroup")
        #     self.oc_msg.set(_("Too much shares by workgroup."
        #                       "\nPlease red button to fix it"
        #                       "\nthen reboot isogeo2office.")
        #                     .format(len(self.shares) - len(self.shares_info[1])))
        #     self.msg_bar.set(_("Error: more than one share by worgroup."
        #                        " Click on Admin button to fix it."))
        #     self.status_bar.config(foreground='Red')
        #     btn_open_shares = Button(self,
        #                              text=_("Fix the shares"),
        #                              command=lambda: self.utils.open_urls(self.shares_info[3]),
        #                              style="Error.TButton")
        #     status_launch = DISABLED
        # else:
        #     logger.info("All shares have an OpenCatalog")
        #     self.oc_msg.set(_("Configuration OK."))
        #     li_oc = [share[3] for share in self.shares_info[0]]
        #     btn_open_shares = Button(self,
        #                              text="\U00002692 " + _("Admin shares"),
        #                              command=lambda: self.utils.open_urls(li_oc))
        #     status_launch = ACTIVE

        # # settings
        # txt = _(u"Settings")
        # btn_settings = Button(self,
        #                       text=str("\U0001F510 {}") + _(u"Settings"),
        #                       command=lambda: self.ui_settings_prompt())

        # griding widgets
        logo_isogeo.grid(row=1, rowspan=3, column=0, padx=2, pady=2, sticky="W")
        Separator(self, orient=VERTICAL).grid(
            row=1, rowspan=3, column=1, padx=2, pady=2, sticky="NSE"
        )
        lb_app_metrics.grid(row=1, column=2, rowspan=3, sticky="NWE")
        # self.lb_input_oc.grid(row=2, column=2, sticky="WE")
        # btn_settings.grid(row=2, rowspan=1,
        #                   column=3, padx=2, pady=2,
        #                   sticky="NWE")


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """To test"""
    root = Tk()
    frame = TabIsogeo(root)
    frame.pack()
    root.mainloop()

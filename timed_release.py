#!/usr/bin/env python3

import os
from datetime import date

thedate = date.today()

rasdir = "where the files are stored"
folder = thedate.strftime('%y%B')
file = thedate.strftime('%d/%m/%y')

wdir = os.getcwd()

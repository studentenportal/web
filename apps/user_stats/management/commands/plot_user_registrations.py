# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num


class Command(BaseCommand):
    help = "Plot user registrations. Use --save option to save the plot to a png file."
    option_list = BaseCommand.option_list + (
        make_option(
            "--save",
            action="store",
            dest="save",
            help="Save the graph as a png to the specified location",
        ),
    )

    def handle(self, *args, **options):
        # Get user join dates
        User = get_user_model()
        datetimes = User.objects.values_list("date_joined", flat=True).order_by(
            "date_joined"
        )
        dates = [dt.date() for dt in datetimes]

        # Get some auxilliary values
        min_date = date2num(dates[0])
        max_date = date2num(dates[-1])
        days = max_date - min_date + 1

        # Initialize X and Y axes
        x = np.arange(min_date, max_date + 1)
        y = np.zeros(days)

        # Iterate over dates, increase registration array
        for date in dates:
            index = int(date2num(date) - min_date)
            y[index] += 1
        y_sum = np.cumsum(y)

        # Plot
        plt.plot_date(x, y_sum, xdate=True, ydate=False, ls="-", ms=0, color="#16171E")
        plt.fill_between(x, 0, y_sum, facecolor="#D0F3FF")
        plt.title("Studentenportal: Registrierte Benutzer")
        plt.rc("font", size=8)
        if options["save"]:
            plt.savefig(options["save"])
        else:
            plt.show()

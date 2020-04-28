# -*- coding: utf-8 -*-

__author__ = 'Samir Adrik'
__email__ = 'samir.adrik@gmail.com'
__version__ = "0.1.2"

import os
import sys
import datetime
from time import time, sleep

from pandas import read_csv
from pyfiglet import Figlet
from argparse import ArgumentParser
from geopy.geocoders import Nominatim


def betat(args):
    start = time()

    csv_file = args.csv
    address_col = args.col
    na = args.na if args.na else ""

    geocoder = Nominatim(user_agent="betat", timeout=600)
    full_df = read_csv(csv_file, delimiter=";").fillna(value=na)
    row_numbers = len(full_df.index)

    longitude = []
    latitude = []
    cache = {}
    for row_num, address in enumerate(full_df[address_col]):
        percent = (row_num / row_numbers) * 100

        sys.stdout.write("\rprocessing '{}' [row nr. {} ({}%)]".format(
            csv_file, row_num, round(percent, 3)))
        sys.stdout.flush()
        try:
            if address not in cache.keys():
                sleep(1)
                location = geocoder.geocode(address)
                lat = location.latitude
                long = location.longitude

                latitude.append(lat)
                longitude.append(long)
            else:
                latitude.append(cache[address][0])
                longitude.append(cache[address][1])
        except AttributeError:
            longitude.append(na)
            latitude.append(na)

    sys.stdout.write("\rfinished processing '{}' rows from '{}', elapsed: {}s".format(
        row_numbers, csv_file, round((time() - start), 7)))
    sys.stdout.flush()

    full_df["Longitude"] = longitude
    full_df["Latitude"] = latitude

    timestamp = datetime.datetime.now().isoformat().replace(".", "_").replace(":", "_")
    file_dir = os.path.dirname(os.path.abspath(__file__))
    saved_file_name = r"{}\betat_{}.xlsx".format(file_dir, timestamp)

    full_df.reset_index(drop=True).to_excel(saved_file_name, index=False)
    print("\n\nfinished creating and saving '{}', elapsed: {}s".format(saved_file_name,
                                                                       round((time() - start), 7)))


def main():
    """
    main program, i.e. primary entrance point to the application

    """
    fig = Figlet(font='standard')
    print(fig.renderText('betat'))
    print('Authors: ' + __author__)
    print('Email: ' + __email__)
    print('Version: ' + __version__ + '\n')

    parser = ArgumentParser(description="get long / lat for addresses from .cvs")
    parser.add_argument("-csv", help="name or path to csv file to process", dest="csv", type=str,
                        required=True)
    parser.add_argument("-col", help="column name of address column", dest="col", type=str,
                        required=True)
    parser.add_argument("-na",
                        help="optional, string representation for NaN values, default is ''",
                        dest="na", type=str, required=False)
    parser.set_defaults(func=betat)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

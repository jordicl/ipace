#!/usr/local/bin/python3
import os
import jlrpy
import math
import argparse
import configparser
import logging

# CLI
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-d", "--debug", help="add debugging",
                    action="store_true")
args = parser.parse_args()

# Set logging to ERROR
logger = logging.getLogger('jply')
if args.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.ERROR)


def printStatus(status):
    n = 0
    for i in status:
        print(n, ": ", i)
        n = n + 1


def setupConnectionToVehicle():
    logger.info("Reading credentials from file")
    try:
        config = configparser.ConfigParser()
        config.read(os.path.expanduser('~') + "/.ipace.conf")

        email = config.get('credentials', 'email')
        password = config.get('credentials', 'password')
    except configparser.Error:
        exit("Error reading configfile!")

    c = jlrpy.Connection(email, password)
    v = c.vehicles[0]

    return(v)


def currentCharge(status):
    # Print current SOC
    return int(status[38].get('value'))


def chargePerHour(status):
    # Charge per hour
    charge = status[148].get('value')
    if charge != "UNKNOWN":
        return float(charge)
    else:
        return "?"


def preconditioningStatus(status):
    return str(status[112].get('value'))


def preconditioningRemainingRuntime(status):
    return int(status[138].get('value'))


def rangeInKM(status):
    if status[6].get('key') == 'EV_RANGE_COMFORTx10':
        return round(float(status[6].get('value')))
    elif status[7].get('key') == 'EV_RANGE_COMFORTx10':
        return round(float(status[7].get('value')))
    else:
        return 'error'


def doorsLocked(status):
    if status[4].get('key') == 'DOOR_IS_ALL_DOORS_LOCKED':
        return str(status[4].get('value'))
    elif status[5].get('key') == 'DOOR_IS_ALL_DOORS_LOCKED':
        return str(status[5].get('value'))
    else:
        return 'error'


def chargingStatus(status):
    if status[6].get('key') == 'EV_CHARGING_STATUS':
        return str(status[6].get('value'))
    elif status[7].get('key') == 'EV_CHARGING_STATUS':
        return str(status[7].get('value'))
    else:
        return 'error'


def chargingTime(status):
    # Print charging time
    total_minutes = int(status[70].get('value'))
    hours = math.floor(total_minutes / 60)
    remaining_minutes = round(math.fmod(total_minutes, 60))
    return([hours, remaining_minutes])


def outputBTT(status, departure):
    # Print current state of charge
    message = str(chargingStatus(status))
    if message == "No Message":
        print('No cable', end='')
    else:
        print(message.capitalize(), end='')

    print(' |', str(currentCharge(status)) + '% | ', end='')

    # Print charging rate
    if message != "No Message":
        print(str(chargePerHour(status)), 'kwh | ', end='')

    # Print range in KM
    print(str(rangeInKM(status)), 'km ', end='')

    # Print remaining charging time
    hours = chargingTime(status)[0]
    mins = chargingTime(status)[1]
    if message != "No Message":
        if hours > 0:
            print('|', str(hours) + ':', end='')
        if mins > 0 and hours > 0:
            print(str(mins).zfill(2) + ' mins', end='')
        if mins > 0 and hours == 0:
            print('|', str(mins).zfill(2) + ' mins', end='')
        else:
            print('|', '??', end='')

    # Doors locked?
    if doorsLocked(status) != 'TRUE':
        print(' | DOORS OPEN', end='')

    # Preconditioning
    if preconditioningStatus(status) != 'INACTIVE':
        if preconditioningStatus(status) == 'IMMEDIATE':
            print(
                ' | Climate (' + str(preconditioningRemainingRuntime(status)).zfill(2) + 'mins)')
        if preconditioningStatus(status) == 'TIMED':
            print(
                ' | Preconditioning')
        else:
            print(str(' | ' + preconditioningStatus(status).capitalize()))
    else:
        print()


vehicle = setupConnectionToVehicle()
status = vehicle.get_status()['vehicleStatus']
departure = vehicle.get_departure_timers()['departureTimerSetting']['timers']

# Print some additional information aiding development
if args.verbose:
    printStatus(status)
    printStatus(departure)

outputBTT(status, departure)
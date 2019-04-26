#!/usr/local/bin/python3
import os
import jlrpy
import math
import argparse
import configparser
import logging
import datetime

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


def currentCharge(v):
    # Print current SOC
    return int(v.get_status("EV_STATE_OF_CHARGE"))


def chargePerHour(v):
    # Charge per hour
    charge = v.get_status("EV_CHARGING_RATE_SOC_PER_HOUR")

    if charge != "UNKNOWN":
        return float(charge)
    else:
        return "?"


def preconditioningStatus(v):
    return str(v.get_status("EV_PRECONDITIONING_MODE"))


def preconditioningRemainingRuntime(v):
    return int(v.get_status("EV_PRECONDITION_REMAINING_RUNTIME_MINUTES"))


def rangeInKM(v):
    return round(float(v.get_status("EV_RANGE_COMFORTx10")))


def doorsLocked(v):
    return str(v.get_status("DOOR_IS_ALL_DOORS_LOCKED"))


def chargingStatus(v):
    return str(v.get_status("EV_CHARGING_STATUS"))


def chargingTime(v):
    # Print charging time
    total_minutes = int(v.get_status("EV_MINUTES_TO_BULK_CHARGED"))
    hours = math.floor(total_minutes / 60)
    remaining_minutes = round(math.fmod(total_minutes, 60))
    return([hours, remaining_minutes])


def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))


def nextDeparture(departure):
    i = 0
    departureTimes = []
    for i in range(len(departure)):
        if departure[i]['timerTarget']['singleDay']:
            this_date = datetime.datetime(departure[i]['timerTarget']['singleDay']['year'], departure[i]['timerTarget']
                                        ['singleDay']['month'], departure[i]['timerTarget']['singleDay']['day'], departure[i]['departureTime']['hour'], departure[i]['departureTime']['minute'])
            departureTimes.append(this_date)
        else:
            for key, value in departure[i]['timerTarget']['repeatSchedule'].items():
                if value is True:
                    print("YES!")
                    d = datetime.datetime.now()
                    while d.strftime('%A') != key.capitalize():
                        d += datetime.timedelta(1)
                    d1 = d.replace(
                        hour=departure[i]['departureTime']['hour'], minute=departure[i]['departureTime']['minute'], second=0, microsecond=0)
                departureTimes.append(d1)
        i = i + 1
    return nearest(departureTimes, datetime.datetime.now())


def outputBTT(v, departure):
    # Print current state of charge
    message = str(chargingStatus(v))
    if message == "No Message":
        print('No cable', end='')
    else:
        print(message.capitalize(), end='')

    print(' |', str(currentCharge(v)) + '% | ', end='')

    # Print charging rate
    if message != "No Message":
        print(str(chargePerHour(v)), 'kwh | ', end='')

    # Print range in KM
    print(str(rangeInKM(v)), 'km ', end='')

    # Print remaining charging time
    hours = chargingTime(v)[0]
    mins = chargingTime(v)[1]
    if message != "No Message":
        if hours > 0:
            print('|', str(hours) + 'h ', end='')
        if mins > 0 and hours > 0:
            print(str(mins).zfill(2) + 'm', end='')
        if mins > 0 and hours == 0:
            print('|', str(mins).zfill(2) + 'm', end='')
    else:
        print('|', '??', end='')

    # Doors locked?
    if doorsLocked(v) != 'TRUE':
        print(' | DOORS OPEN', end='')

    # Preconditioning
    if preconditioningStatus(v) != 'INACTIVE':
        if preconditioningStatus(v) == 'IMMEDIATE':
            print(
                ' | Climate (' + str(preconditioningRemainingRuntime(v)).zfill(2) + 'mins)')
        if preconditioningStatus(v) == 'TIMED':
            print(
                ' | Preconditioning')
        else:
            print(str(' | ' + preconditioningStatus(v).capitalize()))
    else:
        print(end='')

    # Disabled for now

    # Next departure
    # nextDep = nextDeparture(departure)
    # now = datetime.datetime.now()
    # roundedNext = nextDep.replace(hour=0, minute=0, second=0, microsecond=0)
    # roundedNow = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # days = (roundedNext - roundedNow).days

    # if nextDep:
    #     if days == 0:
    #         print(' | ', 'Today', " ", nextDep.hour,
    #               ":", nextDep.minute, sep='')
    #     elif days == 1:
    #         print(' | ', 'Tomorrow', " ", nextDep.hour,
    #               ":", nextDep.minute, sep='')
    #     else:
    #         print(' | ', nextDep.strftime("%A"), " ",
    #               nextDep.hour, ":", nextDep.minute, sep='')


vehicle = setupConnectionToVehicle()
departure = vehicle.get_departure_timers()['departureTimerSetting']['timers']

# Print some additional information aiding development
if args.verbose:
    print(vehicle.get_status())
    printStatus(departure)

outputBTT(vehicle, departure)

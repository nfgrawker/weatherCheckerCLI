import os, sys
import requests
import json
import argparse
from datetime import datetime


def callWeather(
        city="Minneapolis", country="us",
):
    '''our api call, taking two arguments of city and country'''
    if type(city) == list:
        city = " ".join(city)
    response = requests.get(
        f"http://api.openweathermap.org/data/2.5/forecast?q={city},{country}&units=imperial&APPID=09110e603c1d5c272f94f64305c09436"
    )
    if response.status_code != 200:
        print(f"Api call failed with {response.status_code}")
        print(json.loads(response.content)["message"])
        sys.exit(1)
    data = json.loads(response.content)
    return data


def parse_dict(dictToParse):
    '''This sets time to a readable string for our prograb as well as makes the data cleaner for our extraction'''
    dayTempDict = {}
    print(dictToParse.keys())
    for entry in dictToParse["list"]:
        time = entry["dt"]
        dayTime = datetime.fromtimestamp(time)
        day = dayTime.strftime("%d/%B")
        time = dayTime.strftime("%H:%M")
        if day not in dayTempDict:
            dayTempDict[day] = {}
        dayTempDict[day][time] = {}
        dayTempDict[day][time]["temp"] = entry["main"]["temp"]
        dayTempDict[day][time]["weather"] = entry["weather"][0]["main"]
    return dayTempDict


def parse_values(tempDict):
    '''This function will parse all values from our custom dictionary that we created from the API call'''
    found_media_for_day_flag = False
    for key in tempDict:
        found_media_for_day_flag = False
        for time in tempDict[key]:
            for media in mediaList:
                if found_media_for_day_flag:
                    break
                timeDict = tempDict[key][time]
                rating = 0
                modifier = True
                if media["topTemp"] > timeDict["temp"] > media["botTemp"]:
                    rating = 100
                elif media["topTemp"] < timeDict["temp"]:
                    rating = 100 - (timeDict["temp"] - media["topTemp"])
                elif media["botTemp"] > timeDict["temp"]:
                    rating = 100 - (media["botTemp"] - timeDict["temp"])
                if media["modifier"] is not None and media["modType"] == "and":
                    if media["modifier"] == timeDict["weather"] and rating == 100:
                        dayChoices.append(
                            f"Due to the temperature being {timeDict['temp']} and a {timeDict['weather']} forcast {media['type']} would be the best outreach method for {key} "
                        )
                        found_media_for_day_flag = True
                elif media["modifier"] is not None and media["modType"] == "or":
                    if media["modifier"] == timeDict["weather"] or rating == 100:
                        dayChoices.append(
                            f"Due to the temperature being {timeDict['temp']} and a {timeDict['weather']} forcast {media['type']} would be the best outreach method for {key} "
                        )
                        found_media_for_day_flag = True
                elif rating == 100 and media["modifier"] == None:
                    dayChoices.append(
                        f"Due to the temperature being {timeDict['temp']} and a {timeDict['weather']} forcast {media['type']} would be the best outreach method for {key} "
                    )
                    found_media_for_day_flag = True
        if found_media_for_day_flag == False:
            dayChoices.append(f"Weather conditions do not match with any of our outreach methods for the day of {key}")


if __name__ == "__main__":
    # initialize our parser and global vars
    # changing values here is easier than hard coding into functions
    bestEmail = {
        "type": "email",
        "message": "",
        "rating": 0,
        "topTemp": 75,
        "botTemp": 55,
        "modifier": None,
        "modType": None,
        "status": None,
    }
    bestText = {
        "type": "text",
        "message": "",
        "rating": 0,
        "topTemp": 150,
        "botTemp": 75,
        "modifier": "Clear",
        "modType": "and",
        "status": None,
    }
    bestPhone = {
        "type": "phone",
        "message": "",
        "rating": 0,
        "topTemp": 55,
        "botTemp": -200,
        "modifier": "Rain",
        "modType": "or",
        "status": None,
    }
    mediaList = [bestEmail, bestPhone, bestText]
    dayChoices = []
    # Set up parser to accept command line args.
    # TODO add extra interface and media functions
    parser = argparse.ArgumentParser(description="Process command line args.")
    parser.add_argument(
        "-interface",
        metavar="Interface",
        type=bool,
        default=False,
        help="Would you like command line args? True or False",
    )
    parser.add_argument(
        "-city",
        type=str,
        help="The location for which you need the weather report",
        metavar="City",
        default="Minneapolis",
        nargs="+",
    )
    parser.add_argument(
        "-media",
        metavar="Media",
        type=str,
        default="all",
        help="What Media Types does your campaign use?",
    )
    args = parser.parse_args()

    globals().update(vars(args))
    #############################################################################
    # Everything has been instantiated and now the api calls and parsing starts #
    #############################################################################
    print("starting to Collect data...")
    # Grab the data from API
    infoDict = callWeather(city=city,)
    # make the dict a little more personalized to our use.
    formattedDict = parse_dict(infoDict)
    # build our ratings out and check weather for each media.
    parse_values(formattedDict)
    # print out each day
    for day in dayChoices:
        print(day)

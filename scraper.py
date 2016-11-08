# coding=UTF-8
from bs4 import BeautifulSoup
import datetime
import urllib.request
import urllib.error
import re
import unicodedata
import csv


def get_dates():
    dates = []
    print('populating dates... ', end='', flush=True)
    # # NCAA basketball
    # start_date2013 = datetime.date(2013, 11, 8)
    # end_date2013 = datetime.date(2014, 4, 3)
    # day = start_date2013
    # while day <= end_date2013:
    #     dates.append(day.strftime("%Y-%m-%d"))
    #     day += datetime.timedelta(days=1)
    #
    # start_date2014 = datetime.date(2014, 11, 14)
    # end_date2014 = datetime.date(2015, 4, 4)
    # day = start_date2014
    # while day <= end_date2014:
    #     dates.append(day.strftime("%Y-%m-%d"))
    #     day += datetime.timedelta(days=1)
    #
    # start_date2015 = datetime.date(2015, 11, 10)
    # end_date2015 = datetime.date(2016, 4, 4)
    # day = start_date2015
    # while day <= end_date2015:
    #     dates.append(day.strftime("%Y-%m-%d"))
    #     day += datetime.timedelta(days=1)
    #

    # NBA regular season
    start_date2012 = datetime.date(2012, 10, 30)
    end_date2012 = datetime.date(2013, 4, 17)
    day = start_date2012
    while day <= end_date2012:
        dates.append(day.strftime("%Y-%m-%d"))
        day += datetime.timedelta(days=1)

    start_date2013 = datetime.date(2013, 10, 29)
    end_date2013 = datetime.date(2014, 4, 16)
    day = start_date2013
    while day <= end_date2013:
        dates.append(day.strftime("%Y-%m-%d"))
        day += datetime.timedelta(days=1)

    start_date2014 = datetime.date(2014, 10, 28)
    end_date2014 = datetime.date(2015, 4, 15)
    day = start_date2014
    while day <= end_date2014:
        dates.append(day.strftime("%Y-%m-%d"))
        day += datetime.timedelta(days=1)

    start_date2015 = datetime.date(2015, 10, 17)
    end_date2015 = datetime.date(2016, 4, 13)
    day = start_date2015
    while day <= end_date2015:
        dates.append(day.strftime("%Y-%m-%d"))
        day += datetime.timedelta(days=1)

    test_date = datetime.date(2013, 11, 8)
    test_date2 = datetime.date(2013, 11, 9)

    print('done.')
    return dates
    # return [test_date.strftime("%Y-%m-%d"), test_date2.strftime("%Y-%m-%d")]


def scrape(dates, sport='cbb'):
    regex_match = None
    if sport == 'cbb':
        regex_match = re.compile("College Basketball Scores.*")
    elif sport == 'nba':
        regex_match = re.compile("NBA Scores.*")

    games = []
    print('scraping data (this will take a while)... ', end='', flush=True)
    for date in dates:
        url = urllib.request.urlopen("http://scores.sportsoptions.com/scores/" + date + "/all.html")
        soup = BeautifulSoup(url, "html.parser")

        is_sport = False
        for current_table in soup.find_all('table'):
            if current_table.find('td', {'bgcolor': '#0172c2'}):
                # ok we found a table that describes what the next stuff is because its blue. fuck.
                if re.match(regex_match, current_table.text.strip('\n')):
                    # ok, it's college basketball (or whatever) under here.
                    is_sport = True
                    continue
                else:
                    # its some other god damn thing probably tennis
                    is_sport = False
                    continue

            elif is_sport:
                # more nested tables. find the other table. eternal nested hell tables.
                table = current_table.find('table')
                if table:
                    table = table.text
                    table = date + '\n' + table  # add the date
                games.append(table)
    print('done.')
    return [game for game in games if game is not None]  # somehow Nones sneak in and fuck this up otherwise


def clean_cbb(data):
    overtime_games = []
    regulation_games = []
    regulation_header = ['1', '2', 'T', '1H', '2H', 'Open', 'Close', 'ATS', '2H Op', '2H Cl', '2H ATS']
    overtime_header = ['1', '2', 'OT', 'OT 2', 'OT 3', 'OT 4', 'OT 5', 'OT 6', 'T',
                       '1H', '2H', 'Open', 'Close', 'ATS', '2H Op', '2H Cl', '2H ATS']
    print('cleaning data... ', end='', flush=True)
    for raw_game in data:
        game = []

        raw_game = raw_game.splitlines()  # split into chunks
        raw_game = list(filter(None, raw_game))  # get rid of empty values

        for g in raw_game:  # strip unicode characters and replace '½' with .5
            g = list(g)  # since strings are immutable...
            for index, item in enumerate(g):  # hunt down the ½s and replace with .5
                if item == '½':
                    g[index] = '.5'
            g = ''.join(g)  # ok convert back to string
            clean_game = unicodedata.normalize("NFKD", g)  # get rid of miscellaneous unicode...
            game.append(clean_game)  # now we have a nice tidy game table

        if game[4] == 'OT':  # somehow deal with overtime games, not sure the best way yet. will deal with this later.
            overtime_games.append([g for g in game if g not in overtime_header])  # account for up to 6 OT periods
        else:
            gm = [g for g in game if g not in regulation_header]  # strip header data
            if len(gm) == 29:  # not all games have complete information. not fucking dealing with that. dumpster them.
                regulation_games.append(gm)

    print('done.')
    return regulation_games


def clean_nba(data):
    overtime_games = []
    regulation_games = []
    regulation_header = ['1', '2', '3', '4', 'T', '1H', '2H', 'Open', 'Close', 'ATS', '2H Op', '2H Cl', '2H ATS']
    overtime_header = ['1', '2', 'OT', 'OT 2', 'OT 3', 'OT 4', 'OT 5', 'OT 6', 'T',
                       '1H', '2H', 'Open', 'Close', 'ATS', '2H Op', '2H Cl', '2H ATS']
    print('cleaning data... ', end='', flush=True)
    for raw_game in data:
        game = []

        raw_game = raw_game.splitlines()  # split into chunks
        raw_game = list(filter(None, raw_game))  # get rid of empty values
        # print(raw_game)
        for g in raw_game:  # strip unicode characters and replace '½' with .5
            g = list(g)  # since strings are immutable...
            for index, item in enumerate(g):  # hunt down the ½s and replace with .5
                if item == '½':
                    g[index] = '.5'
            g = ''.join(g)  # ok convert back to string
            clean_game = unicodedata.normalize("NFKD", g)  # get rid of miscellaneous unicode...
            game.append(clean_game)  # now we have a nice tidy game table

        if game[6] == 'OT':  # somehow deal with overtime games, not sure the best way yet. will deal with this later.
            overtime_games.append([g for g in game if g not in overtime_header])  # account for up to 6 OT periods
        else:
            gm = [g for g in game if g not in regulation_header]  # strip header data
            if len(gm) == 33:  # not all games have complete information. not fucking dealing with that. dumpster them.
                regulation_games.append(gm)

    print('done.')
    return regulation_games


def write_csv(data, filename='output.csv'):
    try:
        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile, dialect='unix')
            print('writing csv... ', end='', flush=True)
            for line in data:
                writer.writerow(line)
            csvfile.close()
            print('done.')
    except PermissionError:
        exit("close the csv and try again")


def main():
    dates = get_dates()
    games = scrape(dates, sport='nba')
    # games = clean_cbb(games)
    games = clean_nba(games)
    write_csv(games, filename='NBA.csv')

if __name__ == "__main__":
    main()

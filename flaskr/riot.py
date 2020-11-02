import requests

from flask import Blueprint, current_app

bp = Blueprint('riot', __name__)


def get_highest_rank(data):
    ranks = ["UNRANKED", "IRON", "BRONZE", "SILVER", "GOLD",
             "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
    if len(data) == 0:
        return "UNRANKED"
    elif len(data) == 1:
        return data[0]["tier"]
    else:
        return ranks[max([ranks.index(data[0]["tier"]), ranks.index(data[1]["tier"])])]


def get_summoner_data(nickname):
    riot_api_key = current_app.config["RIOT_API_KEY"]

    headers = {
        "X-Riot-Token": riot_api_key
    }
    r = requests.get("https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-name/%s" % nickname, headers=headers)

    responsedata = r.json()

    playerdata = {
        "id": responsedata["id"],
        "level": responsedata["summonerLevel"],
        "puuid": responsedata["puuid"],
        "icon": responsedata["profileIconId"]
    }

    q = requests.get("https://eun1.api.riotgames.com/lol/league/v4/entries/by-summoner/%s" % playerdata["id"],
                     headers=headers)
    playerdata["tier"] = get_highest_rank(q.json())

    return playerdata


def get_tournament_code(tournamentid, summoner_ids: list, metadata = "", maptype = "SUMMONERS_RIFT",
                        picktype = "TOURNAMENT_DRAFT", spectatortype = "ALL", teamsize = 5):

    riot_api_key = current_app.config["RIOT_API_KEY"]
    payload = {
        "allowedSummonerIds": summoner_ids,
        "mapType": maptype,
        "metadata": metadata,
        "pickType": picktype,
        "spectatorType": spectatortype,
        "teamSize": teamsize
    }
    headers = {
        "X-Riot-Token": riot_api_key
    }
    r = requests.post(
        "https://eun1.api.riotgames.com/lol/tournament-stub/v4/codes" + "?count=1&tournamentId=%s" % tournamentid,
        payload=payload, headers=headers)

    return r.json()


def get_matches_id(tournament_code):
    riot_api_key = current_app.config["RIOT_API_KEY"]
    headers = {
        "X-Riot-Token": riot_api_key
    }
    r = requests.get("https://eun1.api.riotgames.com/lol/match/v4/matches/by-tournament-code/%s/ids",
                     tournament_code, headers=headers)

    return r.json()


def get_match_data(match_id):
    riot_api_key = current_app.config["RIOT_API_KEY"]
    headers = {
        "X-Riot-Token": riot_api_key
    }
    r = requests.get("https://eun1.api.riotgames.com/lol/match/v4/matches/%s" % match_id, headers=headers)

    data = r.json()
    return {
        "matchdata": data,
        "blue": data["teams"][0]["win"],
        "red": data["teams"][1]["win"]
    }


def verify_account(summoner, code):
    riot_api_key = current_app.config["RIOT_API_KEY"]
    headers = {
        "X-Riot-Token": riot_api_key
    }
    r = requests.get("https://eun1.api.riotgames.com/lol/platform/v4/third-party-code/by-summoner/%s" % summoner,
                     headers=headers)

    if r.content.decode("UTF-8").replace('"', '') == code:
        return True
    else:
        return False


@bp.route('/riot/getpuuid/<nickname>')
def give_data(nickname):
    d = get_summoner_data(nickname)

    return d


@bp.route('/riot/getmatchdata/<matchdata>')
def givematchdata(matchdata):
    d = get_match_data(matchdata)

    return d


@bp.route('/riot/verify/<summoner>/<string:code>')
def verify(summoner, code):
    d = verify_account(summoner, code)

    return str(d)
from flask import (
    Blueprint, render_template, redirect, url_for
)

from flaskr.db import get_db
from flaskr.groups import get_players_from_team
from flaskr.player import get_player_data

bp = Blueprint(__name__, "teams")


def get_team_matches(id_team):
    cur = get_db().cursor()
    cur.execute("""
        SELECT
            idteams1,
            idteams2,
            matchdata,
            result,
            matchcode,
            playdate
        FROM
            matches,
            teams
        WHERE
            (matches.idteams1 = teams.idteams OR
            matches.idteams2 = teams.idteams) AND
            teams.idteams = %s
    """ % id_team)

    d = cur.fetchall()
    matches = []
    for m in d:
        matches.append({
            "mainteam": id_team,
            "vsteam": (lambda x, y, z: x if x == z else y)(m[0], m[1], id_team),
            "result": m[3],
            "matchcode": m[4],
            "playdate": m[5],
            "matchdata": m[2]
        })

    return matches


def get_team_by_id(id_team):
    cur = get_db().cursor()
    cur.execute("""
            SELECT
                t.`name`,
                t.tag,
                t.wins,
                t.loses,
                g.`name`
            FROM
                teams as t,
                `groups` as g
            WHERE
                t.idgroups = g.idgroups AND
                t.idteams = %s
        """ % id_team)

    d = cur.fetchone()
    if not d:
        return None

    team = {
        "name": d[0],
        "tag": d[1],
        "wins": d[2],
        "loses": d[3],
        "group": d[4]
    }

    return team


def get_all_teams():
    cur = get_db().cursor()
    cur.execute("""
        SELECT
            t.idteams,
            t.`name`,
            t.tag,
            t.wins,
            t.loses,
            g.`name`
        FROM
            teams as t,
            `groups` as g
        WHERE
            t.idgroups = g.idgroups
    """)

    rdata = cur.fetchall()
    teams = []

    for t in rdata:
        teams.append({
            "id": t[0],
            "name": t[1],
            "tag": t[2],
            "wins": t[3],
            "loses": t[4],
            "group": t[5]
        })

    return teams


@bp.route("/teams")
def list_of_teams():
    teams = get_all_teams()

    return render_template("teams/list.html", teams=teams)


@bp.route("/teams/<int:idteam>")
def team_profile(idteam=None):
    if idteam is None:
        return redirect(url_for("flaskr.teams.list_of_teams"))

    players = get_players_from_team(idteam)
    teamdata = get_team_by_id(idteam)
    if teamdata is None:
        return redirect(url_for("flaskr.teams.list_of_teams"))
    pdata = []
    for p in players:
        pdata.append(get_player_data(p["playerid"]))

    teamdata["matches"] = get_team_matches(idteam)
    teamdata["players"] = pdata

    return render_template("teams/team.html", teamdata=teamdata)
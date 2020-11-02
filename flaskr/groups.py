from flask import Blueprint, render_template

from flaskr.db import get_db
from flaskr.player import get_player_data

"""
Group data structure in db:
id - int
groupname - varchar (displays as "Group " + groupname)
phase - int - 0 for group stage, 1 for ladder stage (if ladder then it displays as just "Finals")
"""


bp = Blueprint("groups", __name__)


def get_players_from_team(team):
    cur = get_db().cursor()
    cur.execute("""
        SELECT
            pl.idplayers
        FROM
            player as pl
        WHERE
            pl.idteams = %s 
    """ % team)

    rdata = cur.fetchall()
    players = []
    for p in rdata:
        a = get_player_data(p[0])
        players.append(a)

    return players


def get_teams_in_group(group):
    cur = get_db().cursor()
    cur.execute("""
        SELECT 
            t.idteams,
            t.`name`,
            t.tag,
            t.wins,
            t.loses
        FROM
            teams as t,
            `groups` as g
        WHERE
            g.`name` = '%s' AND
            t.idgroups = g.idgroups;    
    """ % group)

    rdata = cur.fetchall()
    teams = []
    for t in rdata:
        a = {
            "id": t[0],
            "name": t[1],
            "tag": t[2],
            "wins": t[3],
            "loses": t[4]
        }
        a["players"] = get_players_from_team(a["id"])
        teams.append(a)

    return teams


def get_groups_from_phase(phase_id):
    cur = get_db().cursor()
    cur.execute("""
        SELECT
            `name`
        FROM
            `groups`
        WHERE
            idphase = %s
    """ % phase_id)

    rdata = cur.fetchall()
    groups = []
    for g in rdata:
        groups.append(g[0])

    return groups


def get_phase_id(phase):
    cur = get_db().cursor()
    cur.execute("""
        SELECT
            idphase
        FROM
            phases
        WHERE
            `name` = '%s'
    """ % phase)

    rdata = cur.fetchone()

    return rdata[0]


def get_phases_name():
    cur = get_db().cursor()
    cur.execute("""
            SELECT
                `name`
            FROM
                phases
        """)

    rdata = cur.fetchall()
    names = []
    for n in rdata:
        names.append(n[0])

    return names


@bp.route('/groups')
def groups_index():
    return render_template('groups/groups.html')


@bp.route('/groups/standings')
@bp.route('/groups/standings/<string:phase_name>')
def groups_standings(phase_name=None):
    if phase_name is not None:
        groups_list = get_groups_from_phase(get_phase_id(phase_name))
        groups = []
        for g in groups_list:
            a = {
                "name": g,
                "teams": get_teams_in_group(g)
            }
            groups.append(a)

        return render_template('groups/standings.html', groups=groups)
    else:
        return render_template('groups/standings.html', phases=get_phases_name())

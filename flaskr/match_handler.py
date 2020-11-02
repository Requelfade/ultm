import json

from flaskr.db import get_db

"""
Match data structure:
[team name or id or whatever] = [
    {
        opponent_id: id
        match_date: date stamp
        phase: int
        result: X-X (left num is for this team right for opponent)
        side: 0 for blue 1 for red
    }
]
"""

error_messages = [
    "All went well",
    "Team 1 has match then",
    "Team 2 has match then",
    "Those teams has a match in this phase",
]


def get_team_matches(team_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT matches FROM teams WHERE idteams = %s", (team_id,))
    matches = cursor.fetchone()
    return matches


def create_match(match_data):
    try:
        cursor = get_db().cursor()
        team1_matches = json.loads(get_team_matches(match_data["team1_id"]))
        team2_matches = json.loads(get_team_matches(match_data["team2_id"]))
        for t1 in team1_matches:
            if abs(t1["match_date"] - match_data["match_date"]) < 3600:
                return error_messages[1]
            if t1["opponent_id"] == match_data["team2_id"] and t1["phase"] == match_data["phase"]:
                return error_messages[3]

        for t2 in team2_matches:
            if abs(t2["match_date"] - match_data["match_date"]) < 3600:
                return error_messages[2]
            if t2["opponent_id"] == match_data["team1_id"] and t2["phase"] == match_data["phase"]:
                return error_messages[3]

        team1_matches.append(match_data)
        team2_matches.append(match_data)
        cursor.execute("UPDATE teams SET matches = %s WHERE idteams = %s", (team1_matches, match_data["team1_id"]))
        cursor.execute("UPDATE teams SET matches = %s WHERE idteams = %s", (team2_matches, match_data["team2_id"]))

        return error_messages[0]

    except:
        return "Something went wrong"


def delete_match(match_data):
    try:
        cursor = get_db().cursor()
        team1_matches = json.loads(get_team_matches(match_data["team1_id"]))
        team2_matches = json.loads(get_team_matches(match_data["team2_id"]))

        team1_matches.remove(match_data)
        team2_matches.remove(match_data)

        cursor.execute("UPDATE teams SET matches = %s WHERE idteams = %s", (team1_matches, match_data["team1_id"]))
        cursor.execute("UPDATE teams SET matches = %s WHERE idteams = %s", (team2_matches, match_data["team2_id"]))

        return error_messages[0]

    except:
        return "Something went wrong"

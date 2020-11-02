import random
import string

from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)
from password_strength import PasswordPolicy
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
from flaskr.riot import verify_account

policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 1 uppercase letters
    numbers=1,  # need min. 1 digits
    special=1,  # need min. 1 special characters
    nonletters=1,  # need min. 1 non-letter characters (digits, specials, anything)
)

bp = Blueprint("player", __name__)


def get_player_data(player_id):
    cur = get_db().cursor()
    cur.execute("""
                    SELECT 
                        u.username, 
                        u.displayedname, 
                        u.`name`, 
                        u.surname,
                        u.email,
                        u.discordid,
                        u.permissionslevel,
                        s.`name`, 
                        s.shortname, 
                        c.classname,
                        pl.nickname,
                        pl.riotpuuid,
                        pl.`level`,
                        pl.rankedrank,
                        pl.iconid,
                        pl.isverified,
                        pl.lastupdate,
                        pl.issub,
                        ps.position,
                        t.`name`,
                        t.tag,
                        t.wins,
                        t.loses,
                        g.`name`,
                        ph.`name`,
                        pl.summonerid
                    FROM 
                        users as u, 
                        schools as s, 
                        classes as c,
                        player as pl,
                        teams as t,
                        `groups` as g,
                        phases as ph,
                        positions as ps
                    WHERE
                        u.idusers = %s AND
                        u.idplayers = pl.idplayers AND
                        u.idschools = s.idschools AND
                        u.idclass = c.idclass AND
                        pl.idposition = ps.idpositions AND
                        pl.idteams = t.idteams AND
                        t.idteams = g.idgroups AND
                        g.idphase = ph.idphase
                    ;""", (player_id,))
    usr = cur.fetchone()
    if usr is not None:
        playerdata = {
            "playerid": player_id,
            "username": usr[0],
            "displayedname": usr[1],
            "name": usr[2],
            "surname": usr[3],
            "email": usr[4],
            "discordid": usr[5],
            "permissions": usr[6],
            "schoolname": usr[7],
            "schoolshortname": usr[8],
            "classname": usr[9],
            "nickname": usr[10],
            "riotpuuid": usr[11],
            "level": usr[12],
            "rankedrank": usr[13],
            "iconid": usr[14],
            "isverified": usr[15],
            "lastupdate": usr[16],
            "issub": usr[17],
            "position": usr[18],
            "teamname": usr[19],
            "teamtag": usr[20],
            "wins": usr[21],
            "loses": usr[22],
            "groupname": usr[23],
            "phasename": usr[24],
            "summonerid": usr[25],
        }
    else:
        playerdata = {
            'error': "Couldn't find user"
        }

    return playerdata


@bp.route('/player/')
@bp.route('/player/<int:playerid>/')
@bp.route('/player/<int:playerid>/<string:edit>/')
def player_home_page(playerid=0, edit=None):
    isself = False
    editmode = False
    if 'user' in session:
        if playerid == 0:
            playerid = session['user']["playerid"]
            isself = True
        elif session['user'] == playerid:
            isself = True
    if edit == 'edit':
        editmode = True

    playerdata = get_player_data(playerid)
    if isself:
        playerdata["isself"] = True
    else:
        playerdata["isself"] = False

    return render_template("player/player.html", playerdata=playerdata, editmode=editmode)


@bp.route("/player/register", methods=('GET', 'POST'))
def register_player():
    if 'user' in session:
        return redirect(url_for('index.index'))

    message, message_type, message_header = None, None, None
    if request.method == 'POST':
        username = request.form['login']
        email = request.form['email']
        password = request.form['password']
        rpassword = request.form['rpassword']
        cur = get_db().cursor()
        cur.execute('SELECT idusers FROM users WHERE username = %s or email = %s', (username, email))
        usr = cur.fetchone()

        if not username:
            message = "Brak nazwy użytkownika"
        elif not email:
            message = "Brak adresu email"
        elif not password or not password or password != rpassword:
            message = "Hasła nie są identyczne"
        elif len(policy.test(password)) > 0:
            message = "Hasło nie spełnia wymagań bezpieczeństwa"
        elif usr is not None:
            message = "Użytkownik jest już zarejestrowany lub podany adres email jest już w użyciu"

        if message is None:
            cur.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                        (username, generate_password_hash(password), email)
                        )
            get_db().commit()
            return redirect(url_for('index.index'))
        else:
            message_type = "error"
            message_header = "Nie zarejestrowano użytkownika"

    return render_template("player/register.html", message=message, message_type=message_type,
                           message_header=message_header)


@bp.route("/player/login", methods=('GET', 'POST'))
def login():
    message, message_type, message_header = None, None, None
    if 'user' in session:
        return redirect(url_for('index.index'))

    if request.method == 'POST':
        username = request.form['login']
        password = request.form['password']
        cur = get_db().cursor()
        cur.execute(
            'SELECT * FROM users WHERE username = %s', (username,)
        )
        user = cur.fetchone()
        if user is None:
            message = "Nieznana nazwa użytkownika"
        elif not check_password_hash(user[2], password):
            message = "Błędne hasło"

        if message is None:
            session.clear()
            session['user'] = get_player_data(user[0])
            return redirect(url_for('index.index'))
        else:
            message_type = "error"
            message_header = "Błąd logowania"

    return render_template("player/login.html", message=message, message_header=message_header,
                           message_type=message_type)


@bp.route("/player/logout", methods=['GET', 'POST'])
def logout():
    if 'user' in session:
        session.pop('user', None)
    return redirect(url_for('index.index'))


@bp.route("/player/verify", methods=["GET", "POST"])
def verify():

    if 'user' in session:
        if not session['user']['isverified']:
            if request.method != "POST":
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                return render_template("/player/verify.html", code=code)
            else:
                code = request.form['code']
                if verify_account(session["user"]["summonerid"], code):
                    cur = get_db().cursor()
                    cur.execute("""
                    UPDATE `player`
                    SET
                    `isverified` = 1
                    WHERE idplayers=%s;""" % session["user"]["playerid"])
                    get_db().commit()
                    session["user"]["isverified"] = 1
                    return redirect(url_for('player.player_home_page'))
                else:
                    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                    return render_template("/player/verify.html", code=code, message="Wpisano nieprawidłowy kod",
                                           message_type="error", message_header="Błędny kod")
        else:
            return redirect(url_for("player.player_home_page"))

    else:
        return redirect(url_for("player.login"))

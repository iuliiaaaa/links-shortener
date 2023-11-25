import os
import random
from db import *
import flask
from flask import Flask, render_template, url_for, request, session, redirect, abort
import sqlite3
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = '2349236467892165471602946928163478628746923'


menu1 = [
    {"name": "главная", "url": "/"},
    {"name": "авторизация", "url": "auth"},
    {"name": "регистрация", "url": "reg"}
]

menu2 = [
    {"name": "главная", "url": "/"},
    {"name": "профиль", "url": "profile"},
    # {"name": "выйти", "url": "logout"}
]

@app.route("/createUser", methods=['POST'])
def createUser():
    connect = sqlite3.connect('base.db')
    cursor = connect.cursor()
    user_names = cursor.execute('''SELECT * FROM 'users' WHERE login = ?''', (request.form["log"],)).fetchone()
    if (request.form["log"] == '' or request.form["pass"] == ''):
        flask.flash('для регистрации заполните все поля')
        return redirect('/reg', code=302)
    else:
        if user_names != None:
            flask.flash('выбранное имя занято')
            return redirect('/reg', code=302)
        else:
            if request.form["pass"] != request.form["passtwo"]:
                flask.flash('пароли не совпадают')
                return redirect('/reg', code=302)
            else:
                hashas = hashlib.md5(request.form["pass"].encode())
                passw = hashas.hexdigest()
                cursor.execute('''INSERT INTO users('login', password) VALUES(?, ?)''', (request.form["log"],passw))
                connect.commit()
                user = cursor.execute('''SELECT * FROM 'users' WHERE login = ?''', (request.form["log"],)).fetchone()
                session['user_id'] = user[0]
                return redirect('/profile', code=302)


@app.route("/authUser", methods=['POST'])
def authUser():
    connect = sqlite3.connect('base.db')
    cursor = connect.cursor()
    user = cursor.execute('''SELECT * FROM 'users' WHERE login = ?''', (request.form["log"],)).fetchone()
    hashas = hashlib.md5(request.form["pass"].encode())
    passw = hashas.hexdigest()

    if user != None:
        if passw == user[2]:
            session['user_id'] = user[0]
            if 'all' in session and session['all'] != None:
                if session['type'] == 'all':
                    ad = session['all'][1]
                    href = cursor.execute(
                        '''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE links.id = ?''',
                        (session['all'][0],)).fetchone()
                    cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (href[5] + 1, href[0]))
                    print('alarm')
                    connect.commit()
                    session['all'] = None
                    session['user_id'] = None
                    connect.close()
                    return redirect(f"{ad}")
                else:
                    if session['all'][3] == session['user_id']:
                        ad = session['all'][1]
                        href = cursor.execute(
                            '''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE links.id = ?''',
                            (session['all'][0],)).fetchone()
                        cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (href[5] + 1, href[0]))
                        print('alarm')
                        connect.commit()
                        session['all'] = None
                        session['user_id'] = None
                        connect.commit()
                        connect.close()
                        return redirect(f"{ad}")
                    else:
                        session['user_id'] = None
                        session['all'] = None
                        connect.close()
                        return 'доступ закрыт'
            else:
                connect.close()
                return redirect('/profile', code=302)
        else:
            flask.flash('пароль неверный')
            connect.close()
            return redirect('/auth', code=302)
    else:
        flask.flash('аккаунта не существует')
        connect.close()
        return redirect('/auth', code=302)


@app.route("/createhref", methods=['POST'])
def createhref():
    connect = sqlite3.connect('base.db')
    cursor = connect.cursor()

    povtor = cursor.execute("SELECT * from links WHERE link = ? and user_id = ?", (request.form['href'], session['user_id'])).fetchall()

    if (povtor == []):
        if request.form['href'] == '':
            session['nameshref'] = 1
            flask.flash(f'вставьте ссылку')
            connect.close()
            return redirect('/', code=302)
        else:
            if request.form['nameshref'] == '':
                user_adress = hashlib.md5(request.form['href'].encode()).hexdigest()[:random.randint(8, 12)]
            else:
                name_psevdo = cursor.execute('''SELECT * FROM 'links' WHERE hreflink=? ''', (request.form['nameshref'],)).fetchall()
                if name_psevdo != []:
                    session['nameshref'] = 1
                    flask.flash(f'выбранный псевдоним занят')
                    connect.close()
                    return redirect('/', code=302)
                else:
                    user_adress = request.form['nameshref']

            if request.form['how'] == 'public':
                if ('user_id' in session and session['user_id'] != None):
                    type_id = cursor.execute('''SELECT id FROM links_types WHERE type="public"''').fetchone()
                    cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['href'], user_adress, session['user_id'], type_id[0],0))
                    connect.commit()
                    flask.flash(user_adress)
                    connect.close()
                    return redirect('/', code=302)
                else:
                    type_id = cursor.execute('''SELECT id FROM links_types WHERE type="public"''').fetchone()
                    cursor.execute('''INSERT INTO links('link', 'hreflink', 'link_type_id', 'user_id', 'count') VALUES(?, ?, ?, ?, ?)''', (request.form['href'], user_adress, type_id[0], None, 0))
                    connect.commit()
                    flask.flash(user_adress)
                    connect.close()
                    return redirect('/', code=302)
            elif request.form['how'] == 'all':
                type_id = cursor.execute('''SELECT id FROM links_types WHERE type="all"''').fetchone()
                cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['href'], user_adress, session['user_id'], type_id[0], 0))
                connect.commit()
                flask.flash(user_adress)
                connect.close()
                return redirect('/', code=302)
            else:
                type_id = cursor.execute('''SELECT id FROM links_types WHERE type="privat"''').fetchone()
                cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['href'], user_adress, session['user_id'], type_id[0], 0))
                connect.commit()
                flask.flash(user_adress)
                connect.close()
                return redirect('/', code=302)
    else:
        session['est'] = 'yes'
        flask.flash(f'выбранная ссылка уже сокращена')
        connect.close()
        return redirect('/', code=302)

@app.route("/go/<link>")
def go(link):
    connect = sqlite3.connect('base.db')
    cursor = connect.cursor()
    where = cursor.execute('''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE hreflink = ?''', (link, )).fetchone()
    long = cursor.execute('''SELECT link FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE hreflink = ?''', (link, )).fetchone()
    if long == None:
        abort(404)
    else:
        if where[7] == 'public':
            cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (where[5] + 1, where[0]))
            connect.commit()
            connect.close()
            print('123')
            return redirect(where[1])
        elif where[7] == 'all':
            if 'user_id' in session and session['user_id'] != None:
                cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (where[5] + 1, where[0]))
                connect.commit()
                connect.close()
                return redirect(where[1])
            else:
                session['type'] = 'all'
                session['all'] = where
                connect.close()
                return redirect('/auth', code=302)
        elif where[7] == 'privat':
            if 'user_id' in session and session['user_id'] != None:
                if (where[3] == session['user_id']):
                    cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (where[5] + 1, where[0]))
                    connect.commit()
                    connect.close()
                    return redirect(where[1])
                else:
                    connect.close()
                    return 'доступ закрыт'
            else:
                session['all'] = where
                session['type'] = 'privat'
                connect.close()
                return redirect('/auth', code=302)

@app.route("/up", methods=['POST'])
def up():
    connect = sqlite3.connect('base.db')
    cursor = connect.cursor()
    name = cursor.execute('''SELECT * FROM 'links' WHERE hreflink = ? ''', (request.form["hreflink"],)).fetchone()
    long = request.form["long"]
    newshortlink = hashlib.md5(long.encode()).hexdigest()[:random.randint(8, 12)]

    if (name != None):
        if (request.form['hreflink'] == ''):
            cursor.execute('''UPDATE links SET hreflink = ? WHERE id = ?''', (newshortlink, request.form["idlink"],))
            connect.commit()
            connect.close()
            flask.flash('название ссылки изменено')
            return redirect('/profile', code=302)

        elif (name[3] == session['user_id']):
            if (request.form["types"] != '0'):
                cursor.execute('''UPDATE links SET link_type_id = ? WHERE id = ?''', (request.form["types"], request.form["idlink"]))
                connect.commit()
                flask.flash('тип ссылки изменён')
                connect.close()
                return redirect('/profile', code=302)
            else:
                connect.close()
                flask.flash('псевдоним уже задействован')
                return redirect('/profile', code=302)
    else:
        if (request.form["types"] != '0'):
            cursor.execute('''UPDATE links SET hreflink = ?, link_type_id = ? WHERE id = ?''', (request.form["hreflink"],  request.form["types"], request.form["idlink"]))
            connect.commit()
            flask.flash('успешно изменено')
            connect.close()
            return redirect('/profile', code=302)
        else:
            cursor.execute('''UPDATE links SET hreflink = ? WHERE id = ?''', (request.form["hreflink"], request.form["idlink"]))
            connect.commit()
            flask.flash('название ссылки изменено')
            connect.close()
            return redirect('/profile', code=302)

@app.route("/delete", methods=['POST'])
def delete():
    connect = sqlite3.connect('base.db')
    cursor = connect.cursor()
    cursor.execute('''DELETE FROM 'links' WHERE id = ?''', (request.form['idd'],))
    connect.commit()
    connect.close()
    return redirect('/profile', code=302)

@app.route("/")
def index():
    connect = sqlite3.connect('base.db')
    cursor = connect.cursor()
    if 'nameshref' in session and session['nameshref'] != 1:
        baselink = request.base_url
    else:
        baselink = ''
    session['nameshref'] = 0

    if 'user_id' in session and session['user_id'] != None:
        session['user_id'] = session['user_id']
    else:
        session['user_id'] = None

    type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
    connect.close()

    if 'user_id' in session and session['user_id'] != None:
        return render_template('index.html', title="главная", menu=menu2, type=type, baselink=baselink)
    else:
        return render_template('index.html', title="главная", menu=menu1, type=type, baselink=baselink)


@app.route("/reg")
def reg():
    return render_template('reg.html', title="регистрация", menu=menu1)

@app.route("/auth")
def auth():
    return render_template('auth.html', title="авторизация", menu=menu1)


@app.route("/profile")
def profile():
    baselink = request.base_url
    connect = sqlite3.connect('base.db')
    cursor = connect.cursor()

    if 'user_id' in session and session['user_id'] != None:
        login = cursor.execute('''SELECT * FROM 'users' WHERE id = ?''', (session['user_id'],)).fetchone()
        login = login[1]
        hrefs = cursor.execute(
            '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
            (session['user_id'],)).fetchall()
        type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
        connect.close()
        return render_template('profile.html', title="профиль", menu=menu2, hrefs=hrefs, type=type, baselink=baselink[:-7], login=login)
    else:
        connect.close()
        return render_template('index.html', title="главная", menu=menu1)


@app.route("/logout", methods=['POST'])
def logout():
    session['user_id'] = None
    return redirect('/', code=302)

if __name__ =="__main__":
    app.run(debug=True)
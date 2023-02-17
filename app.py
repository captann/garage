import sqlite3
import os
import time
from flask import *
import shutil
from db_api import Local_API
from app_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, \
    current_user
from UserLogin import UserLogin
from threading import Thread
from flask_cors import CORS, cross_origin
app = Flask(__name__)
app.config.from_object(__name__)
login_manager = LoginManager(app)
UPLOAD_FOLDER = 'files'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = {'.png', '.jpg', '.jpeg', '.bmp', '.tif'}
app.config['UPLOAD_PATH'] = 'files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager.login_view = 'login'

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

login_manager.login_message = 'Для просмотра данной страницы нужно войти в профиль'
login_manager.login_message_category = 'ok'
AUTOLOGIN = (not AUTOLOGIN) * '//'

def find_summ(x):
    p = x.split()[0].split(".")
    y = int(p[0]) * 365
    m = int(p[1])
    if m in [1, 3, 5, 7, 8, 10, 12]:
        m = m * 31
    if m in [4, 6, 9, 11]:
        m = m * 30
    if m == 2:
        if int(p[0]) % 4 == 0:
            m = m * 29
        else:
            m = m * 28
    d = int(p[2])
    if len(x.split()) > 1:
        time = [int(i) for i in x.split()[1].split(":")]
        time = time[0] * 60 + time[1] + (y + m + d) * 24 * 60
    else:
        time = (y + m + d) * 24 * 60
    return time


        
def sort_by_date(mas, reverse):
    res = []
    mas = [[find_summ(mas[i]['date']), mas[i]] for i in range(len(mas))]
    mas.sort(key=lambda x: x[0], reverse=reverse)
    for i in range(len(mas)):
        res.append(mas[i][1])

    return res

def update_time():
    while True:
        time.sleep(900)
        dbase.update()


def make_cute_name(url, num):
    n = url.split('/')[-1]
    if len(n) > num:
        n = n[0:num-1] + '...'  + n.split('.')[0][-1] + '.' + n.split('.')[-1]
    return n

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDb(user_id, dbase)



@app.teardown_appcontext
def close_db(e):
    if hasattr(g, 'link_db'):
        g.link_db.close()

dbase = Local_API()

@app.route("/add_car", methods=['POST', 'GET'])
@login_required
def add_car():
    if not dbase.state:
        flash('Произошла ошибка во время добавления ТС', category='error')
        return redirect('/db_updating/add_car')
    if request.method == 'POST':
        if len(request.form['car_name']) > -1 and len(request.form['description']) > -1:
            uploaded_files = request.files.getlist("file")
            for uploaded_file in uploaded_files:
                filename = (uploaded_file.filename)
                if filename != '':
                    file_ext = os.path.splitext(filename)[1]
                    if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                        flash(f"Недопустимое разрешение файла {file_ext}",
                              category='error')
                        break
            else:
                uploaded_files = request.files.getlist("file")
                files = []
                r = current_user.get_id()

                for file in uploaded_files:
                    if file.filename != "":
                        files.append(url_for('upload', filename=f'{r}/{file.filename}'))
                desc = request.form['description'].strip()
                if desc == "":
                    desc = " "
                dist = request.form['distance']
                if dist == "":
                    dist = 0
                if dbase.get_car_id(request.form['car_name'].strip(), current_user.get_id()) == -1:
                    number = request.form['number']
                    res = dbase.add_car(current_user.get_id(), request.form['car_name'].strip(), '\n'.join(
                        desc.split('\n')).strip(), dist, number.strip())
                    if not res:
                        flash(f"Ошибка добавления ТС. Попробуйте повторить позже",
                              category='error')

                    else:

                        uploaded_files = request.files.getlist("file")
                        for uploaded_file in uploaded_files:
                            folder = str(r)
                            filename = (uploaded_file.filename)
                            if filename != '':
                                file_ext = os.path.splitext(filename)[1]
                                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                                    flash(
                                        f"Недопустимое разрешение файла {file_ext}",
                                        category='error')

                                    if os.path.isdir(folder):
                                        shutil.rmtree(
                                            os.path.join(app.config['UPLOAD_PATH'],
                                                         folder),
                                            ignore_errors=True)
                                    break
                                if not os.path.isdir(
                                        os.path.join(app.config['UPLOAD_PATH'],
                                                     folder)):
                                    os.mkdir(
                                        os.path.join(app.config['UPLOAD_PATH'],
                                                     folder))
                                uploaded_file.save(
                                    os.path.join(app.config['UPLOAD_PATH'], folder,
                                                 filename))
                        else:
                            flash("ТС успешно добавлено", category='success')
                else:
                    c = 1
                    while dbase.get_car_id(request.form['car_name'].strip() + f" ({c})", current_user.get_id()) != -1:
                        c += 1
                    number = request.form['number'].strip()
                    res = dbase.add_car(current_user.get_id(), request.form['car_name'].strip() + f" ({c})", '\n'.join(
                        desc.split('\n')).strip(), dist, number.strip())
                    if not res:
                        flash(f"Ошибка добавления ТС. Попробуйте повторить позже",
                              category='error')


                    else:

                        uploaded_files = request.files.getlist("file")
                        for uploaded_file in uploaded_files:
                            folder = str(r)
                            filename = (uploaded_file.filename)
                            if filename != '':
                                file_ext = os.path.splitext(filename)[1]
                                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                                    flash(
                                        f"Недопустимое разрешение файла {file_ext}",
                                        category='error')

                                    if os.path.isdir(folder):
                                        shutil.rmtree(
                                            os.path.join(app.config['UPLOAD_PATH'],
                                                         folder),
                                            ignore_errors=True)
                                    break
                                if not os.path.isdir(
                                        os.path.join(app.config['UPLOAD_PATH'],
                                                     folder)):
                                    os.mkdir(
                                        os.path.join(app.config['UPLOAD_PATH'],
                                                     folder))
                                uploaded_file.save(
                                    os.path.join(app.config['UPLOAD_PATH'], folder,
                                                 filename))
                        else:
                            flash(
                                f"ТС с таки именем уже есть, поэтому новое записано с индексом {c}",
                                category='ok')

        else:
            flash("Ошибка добавления ТС: мало символов", category='error')

    return redirect('/profile')



@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    if not dbase.state:
        return redirect('/db_updating/index')
    if request.method == 'POST':
        model = request.form['for']
        date = request.form['date']
        operation = request.form.getlist("operation")
        model_l = set(["всех ТС"] + [car["car_name"] for car in dbase.get_cars(current_user.get_id())]) - {model}
        model_l = list(model_l)
        model_l = [model] + model_l

        date_l = {"новые", "старые"} - {date}
        date_l = list(date_l)
        date_l = [date] + date_l

        operation_l = set([operation["operation"] for operation in dbase.get_operations_na(current_user.get_id())]) - set(operation)
        operation_l = list(operation_l)
        operation_l = list(operation) + operation_l
        posts = [post for post in dbase.get_posts(current_user.get_id()) if dbase.is_post_deleted(post) == False]
        copy = []
        for i in range(len(posts)):
            if not dbase.is_car_deleted(posts[i]['car_id']) and posts[i]['car_id'] != -1:
                posts[i]['file_url'] = ''.join(posts[i]['file_url']).split('>')
                posts[i]['file_name'] = ''.join(posts[i]['file_name']).split(
                    '>')

                posts[i]['distance'] = int(posts[i]['distance'])
                posts[i]['car_name'] = dbase.get_car(int(posts[i]["car_id"]))["car_name"]
                posts[i]['files'] = [{'file_url': posts[i]['file_url'][j],
                                      'file_name': posts[i]['file_name'][j]} for j
                                     in range(len(posts[i]['file_url']))]
                posts[i]['file_number'] = len(
                    list(filter(lambda x: x != '', posts[i]['file_url'])))
                copy.append(posts[i])
        del posts
        posts = [copy[i] for i in range(len(copy))]
        if model != 'всех ТС':
            posts = list(filter(lambda x: x['car_name'] == model, posts))


        posts = sort_by_date(posts, date == 'новые')
        if 'не имеет значения' not in operation:
            if request.form['type'] == 'хотя бы один тип':
                posts = list(filter(lambda x: any([i in request.form.getlist('operation') for i in x['operation'].split(", ")]), posts))
            else:
                posts = list(filter(lambda x: set(x['operation'].split(", ")) == set(request.form.getlist('operation')), posts))

        if not posts:
            flash("Совпадений по заданным параметрам нет.\nФильтры сброшены", category='ok')
        else:
            return render_template('main.html', menu=dbase.get_menu(current_user.is_authenticated, current_user.get_id()),
                                   flb=100 // len(dbase.get_menu(
                                       current_user.is_authenticated, current_user.get_id())),
                               posts=posts, title='Главная',
                               carlist=model_l,
                               date=date_l,
                               operations=operation_l,
                               url="/", sorting='1', cars=dbase.get_cars(current_user.get_id()),
                                   is_authed=current_user.is_authenticated, user_id=current_user.get_id(),
                                   operations_selected=request.form.getlist("operation"), type=[request.form['type']] + list({"хотя бы один тип", "только все типы"} - set([request.form['type']])))
    posts = [post for post in dbase.get_posts(current_user.get_id()) if not dbase.is_post_deleted(post)]
    copy = []


    for i in range(len(posts)):
        if not dbase.is_car_deleted(posts[i]['car_id']) and posts[i]['car_id'] != -1:

            posts[i]['file_url'] = ''.join(posts[i]['file_url']).split('>')
            posts[i]['file_name'] = ''.join(posts[i]['file_name']).split('>')

            posts[i]['distance'] = int(posts[i]['distance'])
            posts[i]['car_name'] = dbase.get_car(int(posts[i]["car_id"]))[
                "car_name"]

            posts[i]['files'] = [{'file_url': posts[i]['file_url'][j], 'file_name': posts[i]['file_name'][j]} for j in range(len(posts[i]['file_url']))]
            posts[i]['file_number'] = len(list(filter(lambda x: x != '', posts[i]['file_url'])))
            copy.append(posts[i])
    del posts
    posts = [copy[i] for i in range(len(copy))]
    op1 = [operation["operation"] for operation in dbase.get_operations_na(current_user.get_id())]
    op = []
    for i in op1:
        if i not in op:
            op.append(i)
    posts = sort_by_date(posts, True)
    if not posts:
        return redirect(url_for('profile'))
    return render_template('main.html', menu=dbase.get_menu(current_user.is_authenticated, current_user.get_id()),
                               flb=100 // len(dbase.get_menu(
                                   current_user.is_authenticated, current_user.get_id())),
                               posts=posts, title='Главная',
                               revers=["обычном", "обратном"],
                               carlist=["всех ТС"] + [car["car_name"]
                                                         for car in
                                                         dbase.get_cars(
                                                             current_user.get_id())],
                               date=["новые", "старые"],
                               operations=op,
                               url="/", cars=dbase.get_cars(current_user.get_id()), is_authed=current_user.is_authenticated, user_id=current_user.get_id(),
                           operations_selected=["не имеет значения"], type=["хотя бы один тип", "только все типы"])

@app.route('/archive', methods=['POST', 'GET'])
@login_required
def archive():
    if not dbase.state:
        return redirect('/db_updating/archive')
    if request.method == 'POST':
        model = request.form['for']
        date = request.form['date']
        operation = request.form.getlist('operation')
        model_l = set(["всех ТС"] + [car["car_name"] for car in dbase.get_archived_cars(current_user.get_id())]) - {model}
        model_l = list(model_l)
        model_l = [model] + model_l

        date_l = {"новые", "старые"} - {date}
        date_l = list(date_l)
        date_l = [date] + date_l

        operation_l = set([operation["operation"] for operation in
                           dbase.get_operations_na(current_user.get_id())]) - set(
            operation)
        operation_l = list(operation_l)
        operation_l = list(operation) + operation_l


        posts = [post for post in dbase.get_posts(current_user.get_id()) if dbase.is_post_deleted(post) == False]
        copy = []

        for i in range(len(posts)):
            if dbase.is_car_deleted(posts[i]['car_id']) and posts[i]['car_id'] != -1:
                posts[i]['file_url'] = ''.join(posts[i]['file_url']).split('>')
                posts[i]['file_name'] = ''.join(posts[i]['file_name']).split(
                    '>')

                posts[i]['distance'] = int(posts[i]['distance'])
                posts[i]['car_name'] = dbase.get_archived_car(int(posts[i]["car_id"]))["car_name"]

                posts[i]['files'] = [{'file_url': posts[i]['file_url'][j],
                                      'file_name': posts[i]['file_name'][j]} for j
                                     in range(len(posts[i]['file_url']))]
                posts[i]['file_number'] = len(
                    list(filter(lambda x: x != '', posts[i]['file_url'])))
                copy.append(posts[i])

        del posts
        posts = [copy[i] for i in range(len(copy))]

        if model != 'всех ТС':
            posts = list(filter(lambda x: x['car_name'] == model, posts))
        posts = sort_by_date(posts, date == 'новые')
        if 'не имеет значения' not in operation:
            if request.form['type'] == 'хотя бы один тип':
                posts = list(filter(lambda x: any([i in request.form.getlist('operation') for i in x['operation'].split(", ")]), posts))
            else:
                posts = list(filter(lambda x: set(x['operation'].split(", ")) == set(request.form.getlist('operation')), posts))
        if not posts:
            flash("Совпадений по заданным параметрам нет.\nФильтры сброшены", category='ok')
        else:
            return render_template('archive.html', menu=dbase.get_menu(current_user.is_authenticated, current_user.get_id()),
                                   flb=100 // len(dbase.get_menu(
                                       current_user.is_authenticated, current_user.get_id())),
                               posts=posts, title='Архив',
                               carlist=model_l,
                               date=date_l,
                               operations=operation_l,
                               url="/archive", sorting='1', cars=dbase.get_archived_cars(current_user.get_id()), is_authed=current_user.is_authenticated, user_id=current_user.get_id(),
                                   operations_selected=request.form.getlist('operation'), type=[request.form['type']] + list({"хотя бы один тип", "только все типы"} - set([request.form['type']])))
    posts = [post for post in dbase.get_posts(current_user.get_id()) if dbase.is_post_deleted(post) == False]
    copy = []
    for i in range(len(posts)):
        if dbase.is_car_deleted(posts[i]['car_id']) and posts[i]['car_id'] != -1:
            posts[i]['file_url'] = ''.join(posts[i]['file_url']).split('>')

            posts[i]['file_name'] = ''.join(posts[i]['file_name']).split('>')
            posts[i]['distance'] = int(posts[i]['distance'])
            posts[i]["car_name"] = dbase.get_archived_car(int(posts[i]["car_id"]))["car_name"]
            posts[i]['files'] = [{'file_url': posts[i]['file_url'][j],
                                      'file_name': posts[i]['file_name'][j]} for j
                                     in range(len(posts[i]['file_url']))]
            posts[i]['file_number'] = len(
                    list(filter(lambda x: x != '', posts[i]['file_url'])))
            copy.append(posts[i])
    del posts
    posts = [copy[i] for i in range(len(copy))]
    op1 = [operation["operation"] for operation in
           dbase.get_operations_na(current_user.get_id())]
    op = []
    for i in op1:
        if i not in op:
            op.append(i)
    posts = sort_by_date(posts, True)
    if not posts:

        return redirect(url_for('profile'))

    return render_template('archive.html', menu=dbase.get_menu(current_user.is_authenticated, current_user.get_id()),
                               flb=100 // len(dbase.get_menu(
                                   current_user.is_authenticated, current_user.get_id())),
                               posts=posts, title='Архив',
                               revers=["обычном", "обратном"],
                               carlist=["всех ТС"] + [car["car_name"]
                                                         for car in
                                                         dbase.get_archived_cars(
                                                             current_user.get_id())],
                               date=["новые", "старые"],
                               operations=op,
                               url="/archive", cars=[car for car in dbase.get_archived_cars(
                current_user.get_id())], is_authed=current_user.is_authenticated, user_id=current_user.get_id(),
                           operations_selected=["не имеет значения"], type=["хотя бы один тип", "только все типы"])



@app.route('/operations',  methods=['POST', 'GET'])
@login_required
def operations():
    if not dbase.state:
        return redirect('/db_updating/operations')

    url = 'operations'
    if request.method == "POST":
        operation = request.form['operation']
        p = request.form["period"]
        res = dbase.add_operation(operation.strip().lower(), current_user.get_id(), p.strip())
        if not res:
            flash(f"Ошибка добавления нового типа работ",
                  category='error')
            operation = request.form['operation']

        else:
            flash("Новый тип работ успешно добавлен", category='success')
            operation = ""
    commands = dbase.get_operations(current_user.get_id())
    return render_template('operations.html',
                           menu=dbase.get_menu(current_user.is_authenticated, current_user.get_id()),
                           flb=100 // len(
                               dbase.get_menu(current_user.is_authenticated, current_user.get_id())),
                           title='Справочник', url=url,
                           id=current_user.get_id(), cars=commands,
                           is_authed=current_user.is_authenticated, user_id=current_user.get_id())

@app.route("/add_post", methods=['POST', 'GET'])
@login_required
def add_post():
    if not dbase.state:
        flash('Произошла ошибка во время добавления записи', category='error')
        return redirect('/db_updating/add_post')
    url = '/add_post'
    if request.method == 'POST':
        if len(request.form['car']) > 0:
            uploaded_files = request.files.getlist("file")
            for uploaded_file in uploaded_files:
                filename = (uploaded_file.filename)
                if filename != '':
                    file_ext = os.path.splitext(filename)[1]
                    if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                        flash(f"Недопустимое разрешение файла {file_ext}",
                              category='error')
                        break
            else:
                uploaded_files = request.files.getlist("file")
                files = []
                r = current_user.get_id()
                for file in uploaded_files:
                    if file.filename != "":
                        files.append(url_for('upload', filename=f'{r}/{file.filename}'))
                url = '>'.join(files)

                car_id = dbase.get_car_id(request.form['car'], current_user.get_id())
                dist = request.form['distance']
                state = False
                try:
                    dist = int(dist)
                    if dist < 0:
                        dist = 0
                    state = dict(request.form).get('update_distance') == 'on'
                except Exception:
                    dist = 0
                    state = False
                res = dbase.add_post(", ".join(request.form.getlist("operation")), car_id,  current_user.get_id(), int(dist),  request.form["note"], url, '>'.join([make_cute_name(i.filename, 11) for i in uploaded_files]), state)
                if not res:
                    flash(f"Ошибка добавления записи",
                          category='error')
                else:
                    uploaded_files = request.files.getlist("file")
                    for uploaded_file in uploaded_files:
                        folder = str(r)
                        filename = (uploaded_file.filename)
                        if filename != '':
                            file_ext = os.path.splitext(filename)[1]
                            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                                flash(
                                    f"Недопустимое разрешение файла {file_ext}",
                                    category='error')

                                if os.path.isdir(folder):
                                    shutil.rmtree(
                                        os.path.join(app.config['UPLOAD_PATH'],
                                                     folder),
                                        ignore_errors=True)
                                break
                            if not os.path.isdir(
                                    os.path.join(app.config['UPLOAD_PATH'],
                                                 folder)):
                                os.mkdir(
                                    os.path.join(app.config['UPLOAD_PATH'],
                                                 folder))
                            uploaded_file.save(
                                os.path.join(app.config['UPLOAD_PATH'], folder,
                                             filename))
                    else:
                        flash("Запись успешно добавлена", category='success')
        else:
            flash("Ошибка добавления ТС: мало символов", category='error')
    return render_template('add_post.html', menu=dbase.get_menu(current_user.is_authenticated, current_user.get_id()),
                           title='Новая запись',flb=100 // len(dbase.get_menu(current_user.is_authenticated, current_user.get_id())),

                           accept=','.join(list(app.config['UPLOAD_EXTENSIONS'])),
                           url=url, operations= [operation["operation"] for operation in dbase.get_operations(current_user.get_id())],
                                                    cars=[car["car_name"] for car in dbase.get_cars(current_user.get_id())], is_authed=current_user.is_authenticated)


@app.route('/post/<int:id_post>')
@login_required
def show_post(id_post):
    if not dbase.state:
        return redirect(f'/db_updating/post/{id_post}')

    url = f'/post/{id_post}'
    if not dbase.get_post(id_post):
        return abort(404)
    if dbase.get_post(id_post)['user_id'] != int(current_user.get_id()):
        return abort(404)
    post = dbase.get_post(id_post)
    if not post:
        return abort(404)
    op = list(set([operation["operation"] for operation in dbase.get_operations(current_user.get_id()) if operation["operation"] != 'не имеет значения']) - set(post['operation'].split(', ')))
    for i in set(post['operation'].split(', ')):
        op.insert(0, i)
    c = dbase.get_car(int(post['car_id']))
    cars = [car for car in dbase.get_cars(current_user.get_id()) if car != c]
    cars.insert(0, c)

    post['file_url'] = ''.join(post['file_url']).split('>')
    post['file_name'] = ''.join(post['file_name']).split('>')

    post['files'] = [{'file_url': post['file_url'][j],
                          'file_name': post['file_name'][j]} for j
                         in range(len(post['file_url']))]
    return render_template('show_post.html',
                           menu=dbase.get_menu(current_user.is_authenticated, current_user.get_id()),
                           flb=100 // len(
                               dbase.get_menu(current_user.is_authenticated, current_user.get_id())),
                           title=f"Запись {post['operation']}",
                           url=url, operations=op,
                           cars=cars,
                           post=post,
                           is_authed=current_user.is_authenticated,
                           distance=int(post['distance']),
                           note=post['note'],
                           id=int(post['post_id']),
                           operations_selected=post['operation'].split(', ')
                           )


@app.route('/update_operation', methods=['POST', 'GET'])
@login_required
def update_operation():
    if not dbase.state:
        flash('Произошла ошибка во время обновления типа работ', category='error')

        return redirect('/db_updating/update_operation')

    if request.method == 'POST':
        user_id = request.form['user_id']
        old_value = request.form['old_value']
        new_value = request.form['new_value']
        is_exist = dbase.get_operation(new_value, int(
                current_user.get_id()))

        if is_exist:
                if is_exist == {"operation": new_value, "user_id": int(current_user.get_id()), "is_deleted": 0}:
                    flash("Такой тип работ уже есть", category='error')
                    return redirect('/operations')
        if (int(user_id) != int(
                current_user.get_id())):
            return abort(404)
        r = dbase.update_operation(int(user_id), old_value, new_value, request.form["period"])
        if r:
            flash('Изменения сохранены', category='success')
        return redirect('/operations')
    return abort(404)


@app.route('/update_car', methods=['POST', 'GET'])
@login_required
def update_car():
    if not dbase.state:
        flash('Произошла ошибка во время обновления ТС', category='error')

        return redirect('/db_updating/update_car')
    if request.method == 'POST':
        car_id = request.form['car_id']
        description = request.form['description']
        number = request.form['number']

        car_name = request.form['car_name'].strip()
        car = dbase.get_car(int(car_id))
        if not car:
            return abort(404)
        if car_name != car['car_name']:

            if [i['car_name'] for i in dbase.get_cars(current_user.get_id()) if int(i['car_id']) != int(car['car_id'])].count(car_name) > 0:
                c = 1
                while dbase.get_car_id(
                        request.form['car_name'].strip() + f" ({c})",
                        current_user.get_id()) != -1 and dbase.get_car_id(
                        request.form['car_name'].strip() + f" ({c})",
                        current_user.get_id()) != int(car['car_id']):
                    c += 1
                car_name = car_name + f" ({c})"
                flash(
                    f"ТС с таки именем уже есть, поэтому название ТС записано с индексом {c}",
                    category='ok')
        if int(car["user_id"]) != int(
                current_user.get_id()):
            return abort(404)
        distance = int(request.form['distance'])
        r = dbase.update_car(int(car_id), car_name, distance, description, number)
        if r:
            flash('Изменения сохранены', category='success')
            return redirect('/profile')
    return abort(404)

@app.route('/update_post', methods=['POST', 'GET'])
@login_required
def update_post():
    if not dbase.state:
        flash('Произошла ошибка во время обновления записи', category='error')

        return redirect('/db_updating/update_post')
    if request.method == 'POST':
        id = request.form['post_id']
        post = dbase.get_post(id)
        if not post:
            return abort(404)
        post = post
        if (int(post['user_id']) != int(
                current_user.get_id())):
            return abort(404)
        car_id = dbase.get_car_id(request.form['car_name'], current_user.get_id())
        operation = ', '.join(request.form.getlist('operation'))
        distance = int(request.form['distance'])
        note = request.form['note']
        r = dbase.update_post(int(id), car_id, operation, distance, note)
        if r:
            flash('Изменения сохранены', category='success')
            return redirect('/')

    return abort(404)

@app.route('/delete_post', methods=['POST', 'GET'])
@login_required
def delete_post():
    if not dbase.state:
        flash('Произошла ошибка во время удаления записи', category='error')
        return redirect('/db_updating/delete_post')
    if request.method == 'POST':

        id = request.form['post_id']
        post = dbase.get_post(id)
        if not post:
            return abort(404)

        if (int(post['user_id']) != int(
                current_user.get_id())):
            return abort(404)
        if dbase.delete_post(id):
            flash('Запись удалена', category='success')
        else:
            flash('Произошла ошибка во время удаления записи', category='error')
        return '200'
    return '404'

@app.route('/delete_car', methods=['POST', 'GET'])
@login_required
def delete_car():
    if not dbase.state:
        flash('Произошла ошибка во время удаления ТС', category='error')
        return redirect('/db_updating/delete_car')

    if request.method == 'POST':
        car_id = int(request.form['car_id'])
        car = dbase.get_car(car_id)
        if not car:
            return abort(404)
        if (int(car["user_id"]) != int(
                current_user.get_id())):
            return abort(404)
        r = dbase.delete_car(car_id)
        if r:
            flash('ТС успешно удалено', category='success')

        else:
            flash('Произошла ошибка в процессе удаления', category='error')
        return '200'
    return '404'

@app.route('/delete_operation', methods=['POST', 'GET'])
@login_required
def delete_operation():
    if not dbase.state:
        flash('Произошла ошибка во время удаления типа работ', category='error')
        return redirect('/db_updating/delete_operation')
    if request.method == 'POST':
        user_id = request.form['user_id']
        name = request.form['operation']
        operation = dbase.get_operation(name, int(user_id))
        if not operation:
            return abort(404)

        if (int(operation["user_id"]) != int(
                current_user.get_id())):
            return abort(404)
        if dbase.delete_operation(operation["operation"], current_user.get_id()):
            flash("Тип работы успешно удален", category='success')
        else:
            flash("Произошла ошибка во время удаления типа работы", category='error')
        return '200'
    return '404'


@app.route('/show_car/<car_id>')
@login_required
def show_car(car_id):
    if not all([i in '1234567890' for i in str(car_id)]):
        return abort(404)
    car_id = int(car_id)
    if not dbase.state:
        return redirect(f'/db_updating/show_car/{car_id}')

    try:
        car = dbase.get_car(car_id)
        if not car:
            return abort(404)
        if (int(car["user_id"]) != int(current_user.get_id())):
            return abort(404)
        name = car['car_name'].strip()
        description = car['description'].strip()
        distance = car['distance']
        number = car['number']

    except Exception as e:
        flash(f"Не удалось отобразить это ТС", category='error')
        return redirect("/profile")

    return render_template('car.html', menu=dbase.get_menu(current_user.is_authenticated, current_user.get_id()), description=description,
                           flb=100 // len(
                               dbase.get_menu(current_user.is_authenticated, current_user.get_id())),
                           name=name, distance=distance, car_id=car_id, is_authed=current_user.is_authenticated, number=number, title=f"ТС {name}")

@app.route('/login', methods=["GET", "POST"])
def login():
    if not dbase.state:
        return redirect('/db_updating/login')
    url = '/login'
    username = ""
    password = ""
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST":

        user = dbase.get_user_by_username(request.form['username'])
        if user:

            if check_password_hash(user[0]['password'], request.form['password']):
                userlogin = UserLogin().create(user)
                login_user(userlogin)
                rm = True if request.form.get('remainme') else False
                login_user(userlogin, remember=rm)
                return redirect(request.args.get('next') or url_for('profile'))
            else:
                flash('Неправильный пароль', category='error')
        else:
            flash('Пользователь не найден', category='error')
    if not AUTOLOGIN:
        flash("Автологин включен", category='success')
    return render_template("login.html", menu=dbase.get_menu(False, None),
                           flb=100 // len(
                               dbase.get_menu(False, None)),
                           title='Авторизация', url=url, username=username,
                           password=password, is_authed=False, autologin=AUTOLOGIN)


@app.route('/registration', methods=["GET", "POST"])
def registration():
    if not dbase.state:
        return redirect('/db_updating/registration')
    if current_user.is_authenticated:
        return redirect("/")
    url = '/registration'
    email = ''
    username = ''
    p1 = ""
    p2 = ""
    if request.method == "POST":
        if (len(request.form['password']) > 7) and (
                request.form['password'] == request.form['password2']):
            hash = generate_password_hash(request.form['password'])
            res = dbase.add_user(request.form['username'],
                                 request.form['email'], hash)
            if not res:
                flash(f"Ошибка регистрации", category='error')
                username = request.form['username']
                email = request.form['email']
                p1 = request.form['password']
                p2 = request.form['password2']

            else:
                flash("Регистрация успешно завершена", category='success')
                return redirect('/login')
        elif (len(request.form['password']) <= 7):
            flash(f"Ошибка регистрации: пароль короче 8 символов",
                  category='error')
        else:
            flash(f"Ошибка регистрации: пароли несовпадают",
                  category='error')

            username = request.form['username']
            email = request.form['email']
            p1 = request.form['password']
            p2 = request.form['password2']
    return render_template('registration.html', menu=dbase.get_menu(current_user.is_authenticated, current_user.get_id()),
                           flb=100 // len(
                               dbase.get_menu(current_user.is_authenticated, current_user.get_id())),
                           title='Регистрация', url=url, username=username,
                           email=email, p1=p1, p2=p2,is_authed=current_user.is_authenticated)


@app.route('/profile')
@login_required
def profile():
    if not dbase.state:
        return redirect('/db_updating/profile')
    url = '/profile'
    if not current_user.get_id():
        return redirect('/login')
    cars = dbase.get_cars(current_user.get_id())
    #flash(f"{current_user.get_id()}", category='ok')
    return render_template('profile.html', menu=dbase.get_menu(current_user.is_authenticated, current_user.get_id()),
                           flb=100 // len(
                               dbase.get_menu(current_user.is_authenticated, current_user.get_id())),

                           title='Доступные ТС', url=url, id=current_user.get_id(), cars=cars, is_authed=current_user.is_authenticated)


@app.route('/test', methods=['GET', 'POST'])
def test():
    return abort(404)

@login_required
@app.route('/upload/<path:filename>')
def upload(filename):
    if not dbase.state:
        return redirect(f'/db_updating/upload/{filename}')
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


@app.route('/logout')
@login_required
def logout():
    if not dbase.state:
        return redirect('/db_updating/logout')
    logout_user()
    if AUTOLOGIN:
        flash('Вы вышли из профиля', 'ok')
    return redirect('/login')


@app.errorhandler(404)
def error_404(error):
    return render_template('error_404.html',
                           title='404'), 404



@app.errorhandler(500)
def e500(e):
    return render_template('error_505.html',
                           title='500'), 500



@app.route('/db_updating/<path:link>')
def db_updating(link):
    if dbase.state:
        return abort(404)
    else:
        try:
            url_for(link)
        except:
            return abort(404)
        return render_template('BD_update.html', title='Обновление БД', url=url_for(link))

@app.route("/update_db/<password>")
def update_bd(password):
    if password == 'zxoiet123':
        dbase.update()
        return redirect('/profile')
    return abort(404)

@app.route('/version')
def vers():
    return str(VERSION)

@app.route('/connection')
def conncetion():
    response = jsonify({'result': 'connected'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    t1 = Thread(target=update_time)
    t1.start()

    app.run(host='0.0.0.0')

from werkzeug.utils import secure_filename
from flask import *
from forms import *
from db import *
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/img/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def cart_len():
    if "username" in session:
        with open('data/shopping_cart.json', "rt", encoding="utf8") as f:
            carts = json.loads(f.read())
        return len(carts[str(session['user_id'])].keys())
    else:
        return None


def search(phrase):
    phrase = phrase.lower()
    gm = GoodsModel(goods_db.get_connection())
    gm.init_table()
    all = gm.get_all()
    c = filter(lambda x: phrase in x[2].lower() or phrase in x[3].lower(), all)
    return list(c)


@app.route('/search/<phrase>', methods=['GET', 'POST'])
def searched(phrase):
    if request.method == 'POST':
        if request.form.get('search'):
            phrase = request.form['search']
            return redirect('/search/{}'.format(phrase))
    with open('data/image_sources.json', "rt", encoding="utf8") as f:
        srcs = json.loads(f.read())
    return render_template('items.html', goods=search(phrase), title=phrase,
                           name='поиск', srcs=srcs, cart_items=cart_len())


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        if request.form.get('search'):
            phrase = request.form['search']
            return redirect('/search/{}'.format(phrase))
    with open('data/categories.json', "rt", encoding="utf8") as f:
        categories = json.loads(f.read())
    return render_template('index.html', title='Главная',
                           categories=categories, cart_items=cart_len())


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        exists = user_model.exists(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
            session['is_admin'] = eval(exists[2])
            with open('data/shopping_cart.json', "rt", encoding="utf8") as f:
                all_carts = json.loads(f.read())
            with open('data/shopping_cart.json', "w", encoding="utf8") as f:
                if str(session['user_id']) not in all_carts:
                    all_carts[session['user_id']] = dict()
                f.write(json.dumps(all_carts))
            return redirect("/index")
        else:
            return render_template('login.html', title='Авторизация',
                                   form=form,
                                   message='Неверный логин или пароль')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    message = 'Длина пароля должна быть не меньше 7 символов'
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        if len(password) < 7:
            return render_template('registration.html', form=form,
                                   message=message)
        um.insert(user_name, password)
        return redirect('/')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    session.pop('is_admin', 0)
    return redirect('/index')


@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        if request.form.get('search'):
            phrase = request.form['search']
            return redirect('/search/{}'.format(phrase))
    if not session['is_admin']:
        return redirect('/')
    return render_template('admin_panel.html', title='Админ-панель',
                           cart_items=cart_len())


@app.route('/all_users', methods=['GET', 'POST'])
def all_users():
    if request.method == 'POST':
        if request.form.get('search'):
            phrase = request.form['search']
            return redirect('/search/{}'.format(phrase))
    if "username" not in session:
        return redirect('/login')
    if not session['is_admin']:
        return redirect('/')
    um = UsersModel(db.get_connection())
    um.init_table()
    all_users = um.get_all()
    return render_template('all_users.html', title='Все пользователи',
                           users=enumerate(all_users, 1),
                           cart_items=cart_len())


@app.route('/add_photo/<id>', methods=['GET', 'POST'])
def add_photo(id):
    if request.method == 'POST':
        if request.form.get('search'):
            phrase = request.form['search']
            return redirect('/search/{}'.format(phrase))
    if "username" not in session:
        return redirect('/login')
    if not session['is_admin']:
        return redirect('/')
    form = AddPhotoForm()
    if form.validate_on_submit():
        myFile = secure_filename(form.photo_upload.data.filename)
        with open('data/image_sources.json', "rt", encoding="utf8") as f:
            srcs = json.loads(f.read())
        with open('data/image_sources.json', "w", encoding="utf8") as f:
            try:
                srcs[id] += ['static/img/{}'.format(myFile)]
            except:
                srcs[id] = ['static/img/{}'.format(myFile)]
            f.write(json.dumps(srcs))
        form.photo_upload.data.save('static/img/{}'.format(myFile))
        return redirect('/add_photo/{}'.format(id))
    return render_template('add_photo.html', form=form,
                           title='Добавление фото', cart_items=cart_len())


@app.route('/add_goods', methods=['GET', 'POST'])
def add_goods():
    if request.method == 'POST':
        if request.form.get('search'):
            phrase = request.form['search']
            return redirect('/search/{}'.format(phrase))
    if "username" not in session:
        return redirect('/login')
    if not session['is_admin']:
        return redirect('/')
    form = AddGoodsForm()
    if form.validate_on_submit():
        gm = GoodsModel(goods_db.get_connection())
        gm.init_table()
        type = form.type.data
        name = form.name.data
        description = form.description.data
        try:
            price = int(form.price.data)
        except:
            return('Цена должна быть введена в рублях(целым числом)')
        myFile = secure_filename(form.file_upload.data.filename)
        gm.insert(type, name, description, price)
        latest = max(gm.get_all(), key=lambda x: x[5])
        with open('data/image_sources.json', "rt", encoding="utf8") as f:
            srcs = json.loads(f.read())
        with open('data/image_sources.json', "w", encoding="utf8") as f:
            try:
                srcs[latest[0]] += ['static/img/{}'.format(myFile)]
            except:
                srcs[latest[0]] = ['static/img/{}'.format(myFile)]
            f.write(json.dumps(srcs))
        form.file_upload.data.save('static/img/{}'.format(myFile))
        return redirect('/')
    return render_template('add_goods.html', title='Добавление товара',
                           form=form, cart_items=cart_len())


@app.route('/items/<type>', methods=['GET', 'POST'])
def items(type):
    if request.method == 'POST':
        if request.form.get('search'):
            phrase = request.form['search']
            return redirect('/search/{}'.format(phrase))
    with open('data/categories.json', "rt", encoding="utf8") as f:
        categories = json.loads(f.read())
        for d in categories:
            if d['name'] == type:
                name = d['title']
    with open('data/image_sources.json', "rt", encoding="utf8") as f:
        srcs = json.loads(f.read())
    gm = GoodsModel(goods_db.get_connection())
    gm.init_table()
    goods = gm.get_by_type(type)
    return render_template('items.html', goods=goods, title=name,
                           name=name.lower(), srcs=srcs, cart_items=cart_len())


@app.route('/delete/<id>')
def delete(id):
    if "username" not in session:
        return redirect('/login')
    if not session['is_admin']:
        return redirect('/')
    with open('data/image_sources.json', "rt", encoding="utf8") as f:
        srcs = json.loads(f.read())
    for img_path in srcs[id]:
        if os.path.isfile(img_path):
            os.remove(img_path)
        else:
            print('delete_error')
    srcs.pop(id, 0)
    with open('data/image_sources.json', "w", encoding="utf8") as f:
        f.write(json.dumps(srcs))
    gm = GoodsModel(goods_db.get_connection())
    gm.init_table()
    gm.delete(int(id))
    return redirect('/')


@app.route('/item/<id>', methods=['GET', 'POST'])
def item_page(id):
    if request.method == 'POST':
        if request.form.get('search'):
            phrase = request.form['search']
            return redirect('/search/{}'.format(phrase))
    gm = GoodsModel(goods_db.get_connection())
    gm.init_table()
    goods = gm.get(id)
    with open('data/image_sources.json', "rt", encoding="utf8") as f:
        srcs = json.loads(f.read())
    srcs = srcs[id]
    if len(srcs) < 2:
        one_src = srcs[0]
        srcs = srcs[1:]
    else:
        one_src = srcs[1]
        srcs = srcs[2:]
    return render_template('item.html', title=goods[2], item=goods, srcs=srcs,
                           length=len(srcs),
                           one_src=one_src,
                           cart_items=cart_len())


@app.route('/add_to_cart/<int:user_id>/<int:goods_id>')
def cart_adding(user_id, goods_id):
    if "username" not in session:
        return redirect('/login')
    if session['user_id'] != user_id:
        return redirect('/')
    with open('data/shopping_cart.json', "rt", encoding="utf8") as f:
        all_carts = json.loads(f.read())
    with open('data/shopping_cart.json', "w", encoding="utf8") as f:
        try:
            if str(goods_id) not in all_carts[str(user_id)]:
                all_carts[str(user_id)][str(goods_id)] = 1
            else:
                all_carts[str(user_id)][str(goods_id)] += 1
        except:
            all_carts[str(user_id)] = {str(goods_id): 1}
        f.write(json.dumps(all_carts))
    return redirect('/item/{}'.format(str(goods_id)))


@app.route('/cart/<int:id>', methods=['GET', 'POST'])
def user_cart(id):
    if request.method == 'POST':
        if request.form.get('search'):
            phrase = request.form['search']
            return redirect('/search/{}'.format(phrase))
    if "username" not in session:
        return redirect('/login')
    if session['user_id'] != id:
        return redirect('/')
    with open('data/shopping_cart.json', "rt", encoding="utf8") as f:
        all_carts = json.loads(f.read())
        cart = all_carts[str(id)]
    if request.method == 'POST':
        if 'search' not in request.form:
            for good_id in cart.keys():
                all_carts[str(id)][str(good_id)] = int(request.form['count_{}'.format(good_id)])
            with open('data/shopping_cart.json', "w", encoding="utf8") as f:
                f.write(json.dumps(all_carts))
        return redirect('/cart/{}'.format(str(id)))
    all_goods = []
    gm = GoodsModel(goods_db.get_connection())
    gm.init_table()
    for good_id in cart.keys():
        all_goods.append((gm.get(good_id), cart[good_id]))
    sum = 0
    for good in all_goods:
        sum += good[0][4] * good[1]
    return render_template('cart.html', goods=all_goods, title='Корзина',
                           sum=sum, cart_items=cart_len())


@app.route('/delete_from_cart/<int:good_id>')
def delete_from_cart(good_id):
    if "username" not in session:
        return redirect('/login')
    with open('data/shopping_cart.json', "rt", encoding="utf8") as f:
        all_carts = json.loads(f.read())
    with open('data/shopping_cart.json', "w", encoding="utf8") as f:
        all_carts[str(session['user_id'])].pop(str(good_id), 0)
        f.write(json.dumps(all_carts))
    return redirect('cart/{}'.format(session['user_id']))


@app.route('/make_order')
def make_order():
    om = OrdersModel(orders_db.get_connection())
    om.init_table()
    if "username" not in session:
        return redirect('/login')
    with open('data/shopping_cart.json', "rt", encoding="utf8") as f:
        all_carts = json.loads(f.read())
    cart = all_carts[str(session['user_id'])]
    for good_id in cart.keys():
        if cart[good_id] < 1:
            a = 1
        else:
            gm = GoodsModel(goods_db.get_connection())
            gm.init_table()
            good = gm.get(good_id)
            om.insert(good_id, session['user_id'], good[4], cart[good_id])
    all_carts[str(session['user_id'])] = {}
    with open('data/shopping_cart.json', "w", encoding="utf8") as f:
        f.write(json.dumps(all_carts))
    return redirect('/cart/{}'.format(str(session['user_id'])))


@app.route('/my_orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'POST':
        if request.form.get('search'):
            phrase = request.form['search']
            return redirect('/search/{}'.format(phrase))
    if "username" not in session:
        return redirect('/login')
    om = OrdersModel(orders_db.get_connection())
    om.init_table()
    gm = GoodsModel(goods_db.get_connection())
    gm.init_table()
    names = []
    orders = sorted(om.get_by_user(session['user_id']), key=lambda x: x[7],
                    reverse=True)
    for order in orders:
        names.append(gm.get(order[1]))
    return render_template('orders.html', title='Заказы',
                           orders=zip(orders, names), cart_items=cart_len())


@app.route('/order_control', methods=['GET', 'POST'])
def order_control():
    if request.method == 'POST':
        if request.form.get('search'):
            phrase = request.form['search']
            return redirect('/search/{}'.format(phrase))
    if "username" not in session:
        return redirect('/login')
    if not session['is_admin']:
        return redirect('/')
    om = OrdersModel(orders_db.get_connection())
    om.init_table()
    gm = GoodsModel(goods_db.get_connection())
    gm.init_table()
    names = []
    orders = sorted(om.get_all(), key=lambda x: x[7],
                    reverse=True)
    for order in orders:
        names.append(gm.get(order[1]))
    return render_template('order_control.html', title='Изменить статус',
                           orders=zip(orders, names), cart_items=cart_len())


@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    if request.method == 'POST':
        if request.form.get('search'):
            phrase = request.form['search']
            return redirect('/search/{}'.format(phrase))
    if "username" not in session:
        return redirect('/login')
    if not session['is_admin']:
        return redirect('/')
    om = OrdersModel(orders_db.get_connection())
    om.init_table()
    if request.method == 'POST':
        if 'search' not in request.form:
            om.change_status(order_id, request.form['new_status'])
            return redirect('/edit_order/{}'.format(str(order_id)))
    order = om.get(order_id)
    options = (
        'Формируется к отправке',
        'Едет в пункт выдачи',
        'Ждёт в пункте выдачи',
        'Получен'
              )
    return render_template('edit_order.html', title='Изменить статус',
                           order=order, options=options,
                           cart_items=cart_len())


@app.route('/delete_order/<int:order_id>')
def delete_order(order_id):
    if "username" not in session:
        return redirect('/login')
    if not session['is_admin']:
        return redirect('/')
    om = OrdersModel(orders_db.get_connection())
    om.init_table()
    om.delete(order_id)
    return redirect('/')


if __name__ == '__main__':
    db = DB('users')
    goods_db = DB('goods')
    orders_db = DB('orders')
    um = UsersModel(db.get_connection())
    um.init_table()
    app.run(port=8080, host='127.0.0.1', debug=False)

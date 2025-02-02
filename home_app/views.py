import flask
from project.settings import database
from .models import Product
from flask_login import current_user

def get_cart() -> list:
    final_product_list = []
    list_product_cart_id = []
    products_cart = flask.request.cookies.get('product')
    if products_cart != None:
        list_product_cart_id = products_cart.split(',')
    list_product_cart = []
    summary_price = 0
    for id in list_product_cart_id:
        product_cart = Product.query.get(id)
        if product_cart != None:
            product_price_list = product_cart.price.split(' ')
            summary_price += int(product_price_list[0] + product_price_list[1])
            list_product_cart.append(product_cart)
    print(summary_price)
    summary_price = f'{summary_price:,}'.replace(',', ' ')
    print(summary_price)
    for product in list(set(list_product_cart)):
        final_product_list.append([product, list_product_cart.count(product)])
    return final_product_list, summary_price

def get_product(list_all_products: list[Product]) -> list[Product]:
    list_products = list_all_products.copy()
    search = ''
    brand = ''
    min_price_filter = 0
    max_price_filter = 0
    if flask.request.args:
        if 'search' in flask.request.args:
            search = flask.request.args.get('search')
        else:
            if 'brand' in flask.request.args:
                brand = flask.request.args.getlist('brand')
            if 'min-price' in flask.request.args:
                min_price_filter = flask.request.args.get('min-price')
                max_price_filter = flask.request.args.get('max-price')
    print(brand)
    max_price_all = 0
    min_price_all = 100000
    for product in list_products:
        price = int(product.price.replace(' ', '').split('₴')[0])
        if price > max_price_all:
            max_price_all = price
        if price < min_price_all:
            min_price_all = price
    print(list_products, list_all_products)
    for product in list_all_products:
        if search:
            if search.lower() not in product.description.lower():
                if product in list_products:
                    list_products.remove(product)
        if brand:
            print(product.name, product.brand not in brand)
            if product.brand not in brand:
                if product in list_products:
                    list_products.remove(product)
        if min_price_filter and max_price_filter:
            price = int(product.price.replace(' ', '').split('₴')[0])
            if price < int(min_price_filter) or price > int(max_price_filter):
                if product in list_products:
                    list_products.remove(product)
        if not brand and not search and not min_price_filter:
            break
    if not min_price_filter:
        min_price_filter = min_price_all
    if not max_price_filter:
        max_price_filter = max_price_all
    return list_products, search, brand, max_price_filter, min_price_filter, max_price_all, min_price_all

def render_home(error = None):
    list_product_cart, summary_price = get_cart()
    print(list_product_cart)
    list_all_products = Product.query.all()
    list_products, search, brand, max_price, low_price, max_price_all, min_price_all = get_product(list_all_products)
    list_brands = []
    list_search_brand = []
    if not brand:
        for product in list_products:
            if product.brand not in list_brands:
                list_brands.append(product.brand)
    else: 
        list_search_brand = brand
        for product in list_all_products:
            if product.brand not in list_brands:
                list_brands.append(product.brand)
    user_auth = False
    error_reg = None
    error_auth = None
    error_password = None
    if current_user.is_authenticated:
        user_auth = current_user.username
    if error != None:
        if 'reg' in error:
            error_reg = 'Користувач вже існує'
        elif 'password' in error:
            error_password = 'Старий пароль не співпадає'
        else:
            error_auth = 'Невірний логін або пароль'
    return flask.render_template('catalog.html', list_products = list_products, user_auth = user_auth, error_reg = error_reg, error_auth = error_auth, error_password = error_password, list_product_cart = list_product_cart, summary_price = summary_price, search = search, list_brands = list_brands, list_search_brand = list_search_brand, max_price = max_price, low_price = low_price, min_price_all = min_price_all, max_price_all = max_price_all)

def render_product(product_id, product_color, product_memory, error = None):
    list_product_cart, summary_price = get_cart()
    list_colors = ['black', 'violet', 'midnightblue', 'darkblue', 'gold', 'green', 'red']
    list_memory = ['64GB', '128GB', '256GB', '512GB', '1TB']
    product = Product.query.get(product_id)
    color_index = list_colors.index(product_color)
    memory_index = list_memory.index(product_memory)
    list_colors[color_index] += ' active'
    list_memory[memory_index] += ' active'
    if flask.request.method == 'POST' and flask.request.form.get('class') != 'auth-form':
        if flask.request.form.get('class') == 'buy-form':
            # if current_user.is_authenticated:
            #     order = Order(user_id = current_user.id, product_id = product_id, product_color = product_color, product_memory = product_memory)
            #     database.session.add(order)
            #     database.session.commit()
            #     return flask.redirect('/')
            pass
        else:
            if flask.request.form.get('memory_button'):
                product_memory = flask.request.form.get('memory_button')
            if flask.request.form.get('color_button'):
                product_color = flask.request.form.get('color_button')
            return flask.redirect(f'/product/{product_id}&{product_color}&{product_memory}')
    user_auth = False
    if current_user.is_authenticated:
        user_auth = current_user.username
    print(error)
    error_reg = None
    error_auth = None
    error_password = None
    if error != None:
        if 'reg' in error:
            error_reg = 'Користувач вже існує'
        elif 'password' in error:
            error_password = 'Старий пароль не співпадає'
        else:
            error_auth = 'Невірний логін або пароль'
    return flask.render_template('product.html', product = product, colors = list_colors, memories = list_memory, active_color = product_color, active_memory = product_memory, user_auth = user_auth, error = error, error_reg = error_reg, error_auth = error_auth, error_password = error_password, list_product_cart = list_product_cart, summary_price = summary_price)
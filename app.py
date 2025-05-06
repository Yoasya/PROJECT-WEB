from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-please-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///swagcraft.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"]
)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'tshirt' or 'hoodie'
    image = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, default=0)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    shipping_address = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), nullable=False)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

# Admin views
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('login'))
        return super(MyAdminIndexView, self).index()

admin = Admin(app, name='SWAGcraft Admin', template_mode='bootstrap4', index_view=MyAdminIndexView())
admin.add_view(SecureModelView(Product, db.session))
admin.add_view(SecureModelView(Order, db.session))
admin.add_view(SecureModelView(User, db.session))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    featured_products = Product.query.limit(6).all()
    return render_template('index.html', products=featured_products)

@app.route('/catalog')
def catalog():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', 'all')
    
    query = Product.query
    if category != 'all':
        query = query.filter_by(category=category)
    
    products = query.paginate(page=page, per_page=8)
    return render_template('catalog.html', products=products, category=category)

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    products = []
    total = 0
    
    for product_id, quantity in cart_items.items():
        product = Product.query.get(product_id)
        if product:
            products.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': quantity,
                'subtotal': product.price * quantity,
                'image': product.image
            })
            total += product.price * quantity
    
    return render_template('cart.html', products=products, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart', {})
    quantity = int(request.form.get('quantity', 1))
    
    if str(product_id) in cart:
        cart[str(product_id)] += quantity
    else:
        cart[str(product_id)] = quantity
    
    session['cart'] = cart
    flash('Товар добавлен в корзину!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        session['cart'] = cart
        flash('Товар удален из корзины', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        cart_items = session.get('cart', {})
        if not cart_items:
            flash('Корзина пуста', 'error')
            return redirect(url_for('cart'))
        
        total = sum(Product.query.get(int(pid)).price * qty 
                   for pid, qty in cart_items.items())
        
        order = Order(
            user_id=current_user.id,
            total=total,
            shipping_address=request.form['address'],
            email=request.form['email']
        )
        db.session.add(order)
        db.session.commit()
        
        for product_id, quantity in cart_items.items():
            product = Product.query.get(int(product_id))
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price=product.price
            )
            db.session.add(order_item)
        
        db.session.commit()
        session['cart'] = {}
        flash('Заказ успешно оформлен!', 'success')
        return redirect(url_for('index'))
    
    return render_template('checkout.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Неверный email или пароль', 'error')
            return redirect(url_for('login'))
        
        login_user(user, remember=remember)
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Имя пользователя уже занято', 'error')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("\nСайт доступен по адресу: http://127.0.0.1:5000\n")
    app.run(debug=True) 
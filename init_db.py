from app import app, db, User, Product
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Создаем таблицы
        db.create_all()

        # Создаем администратора
        admin = User(
            username='admin',
            email='admin@swagcraft.com',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)

        # Создаем тестовые товары
        products = [
            Product(
                name='Футболка "Creeper Face"',
                description='Классическая футболка с изображением Крипера',
                price=1499.99,
                category='tshirt',
                image='creeper_tshirt.jpg',
                stock=10
            ),
            Product(
                name='Толстовка "Diamond Sword"',
                description='Теплая толстовка с принтом алмазного меча',
                price=2999.99,
                category='hoodie',
                image='diamond_hoodie.jpg',
                stock=5
            ),
            Product(
                name='Футболка "Steve\'s Adventure"',
                description='Футболка с изображением Стива в действии',
                price=1599.99,
                category='tshirt',
                image='steve_tshirt.jpg',
                stock=8
            ),
            Product(
                name='Толстовка "Enderman"',
                description='Черная толстовка с принтом Эндермена',
                price=3299.99,
                category='hoodie',
                image='enderman_hoodie.jpg',
                stock=3
            ),
            Product(
                name='Футболка "Minecraft Logo"',
                description='Футболка с классическим логотипом игры',
                price=1299.99,
                category='tshirt',
                image='logo_tshirt.jpg',
                stock=15
            ),
            Product(
                name='Толстовка "Nether Portal"',
                description='Толстовка с изображением портала в Незер',
                price=2799.99,
                category='hoodie',
                image='nether_hoodie.jpg',
                stock=7
            )
        ]

        for product in products:
            db.session.add(product)

        db.session.commit()

if __name__ == '__main__':
    init_db() 
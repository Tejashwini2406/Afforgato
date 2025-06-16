#!/usr/bin/env python3
"""
Initialize the Afforgato Cafe database with sample data
"""

from app import app
from models import db, User, Category, MenuItem, Address
from werkzeug.security import generate_password_hash

def create_sample_data():
    """Create sample data for the application"""
    
    print("🗄️ Creating database tables...")
    db.create_all()
    
    # Check if data already exists
    if User.query.first():
        print("✅ Database already has data. Skipping initialization.")
        return
    
    print("👥 Creating demo users...")
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@afforgato.com',
        first_name='Admin',
        last_name='User',
        is_admin=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Create demo user
    demo_user = User(
        username='demo',
        email='demo@afforgato.com',
        first_name='Demo',
        last_name='User',
        phone='+91 98765 12345'
    )
    demo_user.set_password('demo123')
    db.session.add(demo_user)

    # Commit users first to get their IDs
    db.session.commit()

    # Create addresses for users
    admin_address = Address(
        user_id=admin.id,
        address_type='home',
        street_address='456 Admin Avenue, Koramangala',
        city='Bengaluru',
        state='Karnataka',
        postal_code='560034',
        country='India',
        is_default=True
    )
    db.session.add(admin_address)

    demo_address = Address(
        user_id=demo_user.id,
        address_type='home',
        street_address='123 Coffee Street, Indiranagar',
        city='Bengaluru',
        state='Karnataka',
        postal_code='560038',
        country='India',
        is_default=True
    )
    db.session.add(demo_address)
    
    print("📂 Creating menu categories...")
    
    # Create categories
    categories_data = [
        {'name': 'Hot Coffee', 'description': 'Freshly brewed hot coffee beverages', 'emoji': '☕'},
        {'name': 'Cold Coffee', 'description': 'Refreshing iced coffee drinks', 'emoji': '🧊'},
        {'name': 'Tea', 'description': 'Premium tea selection', 'emoji': '🍵'},
        {'name': 'Pastries', 'description': 'Fresh baked goods and pastries', 'emoji': '🥐'},
        {'name': 'Sandwiches', 'description': 'Delicious sandwiches and wraps', 'emoji': '🥪'},
        {'name': 'Desserts', 'description': 'Sweet treats and desserts', 'emoji': '🍰'}
    ]
    
    categories = []
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.session.add(category)
        categories.append(category)
    
    # Commit to get category IDs
    db.session.commit()
    
    print("🍽️ Creating menu items...")
    
    # Create menu items (prices in Indian Rupees)
    menu_items_data = [
        # Hot Coffee
        {'name': 'Espresso', 'description': 'Rich and bold single shot', 'price': 120, 'category_id': categories[0].id, 'emoji': '☕'},
        {'name': 'Americano', 'description': 'Espresso with hot water', 'price': 150, 'category_id': categories[0].id, 'emoji': '☕'},
        {'name': 'Cappuccino', 'description': 'Espresso with steamed milk and foam', 'price': 180, 'category_id': categories[0].id, 'emoji': '☕'},
        {'name': 'Latte', 'description': 'Espresso with steamed milk', 'price': 200, 'category_id': categories[0].id, 'emoji': '☕'},
        {'name': 'Mocha', 'description': 'Espresso with chocolate and steamed milk', 'price': 220, 'category_id': categories[0].id, 'emoji': '☕'},

        # Cold Coffee
        {'name': 'Iced Coffee', 'description': 'Cold brew over ice', 'price': 160, 'category_id': categories[1].id, 'emoji': '🧊'},
        {'name': 'Iced Latte', 'description': 'Espresso with cold milk over ice', 'price': 200, 'category_id': categories[1].id, 'emoji': '🧊'},
        {'name': 'Frappuccino', 'description': 'Blended coffee with ice and cream', 'price': 250, 'category_id': categories[1].id, 'emoji': '🧊'},
        {'name': 'Cold Brew', 'description': 'Smooth cold-brewed coffee', 'price': 180, 'category_id': categories[1].id, 'emoji': '🧊'},

        # Tea
        {'name': 'Earl Grey', 'description': 'Classic bergamot-flavored black tea', 'price': 100, 'category_id': categories[2].id, 'emoji': '🍵'},
        {'name': 'Green Tea', 'description': 'Antioxidant-rich green tea', 'price': 90, 'category_id': categories[2].id, 'emoji': '🍵'},
        {'name': 'Chai Latte', 'description': 'Spiced tea with steamed milk', 'price': 140, 'category_id': categories[2].id, 'emoji': '🍵'},

        # Pastries
        {'name': 'Croissant', 'description': 'Buttery, flaky French pastry', 'price': 120, 'category_id': categories[3].id, 'emoji': '🥐'},
        {'name': 'Blueberry Muffin', 'description': 'Fresh blueberry muffin', 'price': 100, 'category_id': categories[3].id, 'emoji': '🧁'},
        {'name': 'Danish', 'description': 'Sweet pastry with fruit filling', 'price': 130, 'category_id': categories[3].id, 'emoji': '🥐'},

        # Sandwiches
        {'name': 'Club Sandwich', 'description': 'Triple-decker with turkey and bacon', 'price': 280, 'category_id': categories[4].id, 'emoji': '🥪'},
        {'name': 'Grilled Cheese', 'description': 'Classic grilled cheese sandwich', 'price': 200, 'category_id': categories[4].id, 'emoji': '🥪'},
        {'name': 'Veggie Wrap', 'description': 'Fresh vegetables in a tortilla wrap', 'price': 240, 'category_id': categories[4].id, 'emoji': '🌯'},

        # Desserts
        {'name': 'Chocolate Cake', 'description': 'Rich chocolate layer cake', 'price': 180, 'category_id': categories[5].id, 'emoji': '🍰'},
        {'name': 'Cheesecake', 'description': 'Creamy New York style cheesecake', 'price': 220, 'category_id': categories[5].id, 'emoji': '🍰'},
        {'name': 'Tiramisu', 'description': 'Italian coffee-flavored dessert', 'price': 250, 'category_id': categories[5].id, 'emoji': '🍰'}
    ]
    
    for item_data in menu_items_data:
        menu_item = MenuItem(**item_data)
        db.session.add(menu_item)
    
    # Commit all changes
    db.session.commit()
    
    print("✅ Database initialized successfully!")
    print("\n🎉 Demo accounts created:")
    print("👨‍💼 Admin: username='admin', password='admin123'")
    print("👤 User: username='demo', password='demo123'")
    print("\n🚀 You can now run: python app.py")

def main():
    """Main function"""
    print("=" * 60)
    print("🍵 AFFORGATO CAFE DATABASE INITIALIZATION 🍵")
    print("=" * 60)
    
    with app.app_context():
        create_sample_data()

if __name__ == "__main__":
    main()

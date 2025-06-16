"""
Database Initialization Script for Normalized Afforgato Cafe Database
Creates tables, triggers, constraints, and sample data with proper normalization
"""

from app import app
from models import db, User, UserProfile, Address, Category, MenuItem, Order, OrderItem, Cart, AuditLog, InventoryLog, OrderStatusHistory
from database_triggers import initialize_database_triggers, DatabaseTransactionManager, with_transaction
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@with_transaction
def create_normalized_database():
    """Create the normalized database with all tables and constraints"""
    try:
        # Drop all tables first (for clean setup)
        logger.info("Dropping existing tables...")
        db.drop_all()
        
        # Create all tables
        logger.info("Creating normalized database tables...")
        db.create_all()
        
        # Initialize triggers
        initialize_database_triggers()
        
        logger.info("✅ Normalized database created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database: {str(e)}")
        raise e

@with_transaction
def create_sample_data():
    """Create sample data for testing the normalized database"""
    try:
        logger.info("Creating sample data...")
        
        # 1. Create Admin User
        admin_user = User(
            username='admin',
            email='admin@afforgato.com',
            first_name='Tejashwini',
            last_name='Admin',
            phone='+91 98765 43210',
            is_admin=True,
            email_verified=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.flush()  # Get the ID
        
        # Create admin address
        admin_address = Address(
            user_id=admin_user.id,
            address_type='work',
            street_address='123 Coffee Street, MG Road',
            city='Bengaluru',
            state='Karnataka',
            postal_code='560001',
            country='India',
            is_default=True
        )
        db.session.add(admin_address)
        
        # 2. Create Sample Customers
        customers_data = [
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+91 98765 43211',
                'address': '456 Tech Park, Electronic City'
            },
            {
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone': '+91 98765 43212',
                'address': '789 Business District, Koramangala'
            },
            {
                'username': 'coffee_lover',
                'email': 'coffee@example.com',
                'first_name': 'Coffee',
                'last_name': 'Lover',
                'phone': '+91 98765 43213',
                'address': '321 Cafe Street, Indiranagar'
            }
        ]
        
        for customer_data in customers_data:
            user = User(
                username=customer_data['username'],
                email=customer_data['email'],
                first_name=customer_data['first_name'],
                last_name=customer_data['last_name'],
                phone=customer_data['phone'],
                is_admin=False,
                email_verified=True
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.flush()
            
            # Create address for each customer
            address = Address(
                user_id=user.id,
                address_type='home',
                street_address=customer_data['address'],
                city='Bengaluru',
                state='Karnataka',
                postal_code='560001',
                country='India',
                is_default=True
            )
            db.session.add(address)
        
        # 3. Create Categories
        categories_data = [
            {'name': 'Hot Beverages', 'description': 'Steaming hot coffee and tea', 'emoji': '☕', 'sort_order': 1},
            {'name': 'Cold Beverages', 'description': 'Refreshing iced drinks', 'emoji': '🧊', 'sort_order': 2},
            {'name': 'Pastries', 'description': 'Fresh baked goods', 'emoji': '🥐', 'sort_order': 3},
            {'name': 'Sandwiches', 'description': 'Hearty sandwiches and wraps', 'emoji': '🥪', 'sort_order': 4},
            {'name': 'Desserts', 'description': 'Sweet treats and cakes', 'emoji': '🍰', 'sort_order': 5},
            {'name': 'Snacks', 'description': 'Light bites and appetizers', 'emoji': '🍿', 'sort_order': 6}
        ]
        
        for cat_data in categories_data:
            category = Category(**cat_data)
            db.session.add(category)
        
        db.session.flush()  # Get category IDs
        
        # 4. Create Menu Items with Enhanced Data
        menu_items_data = [
            # Hot Beverages
            {
                'name': 'Espresso',
                'description': 'Rich and bold single shot of espresso',
                'price': 120.00,
                'category_id': 1,
                'emoji': '☕',
                'preparation_time': 5,
                'calories': 5,
                'ingredients': ['Espresso beans', 'Water'],
                'allergens': [],
                'inventory_count': 100,
                'is_featured': True
            },
            {
                'name': 'Cappuccino',
                'description': 'Perfect blend of espresso, steamed milk, and foam',
                'price': 180.00,
                'category_id': 1,
                'emoji': '☕',
                'preparation_time': 8,
                'calories': 120,
                'ingredients': ['Espresso beans', 'Milk', 'Milk foam'],
                'allergens': ['Dairy'],
                'inventory_count': 100,
                'is_featured': True
            },
            {
                'name': 'Latte',
                'description': 'Smooth espresso with steamed milk and light foam',
                'price': 200.00,
                'category_id': 1,
                'emoji': '☕',
                'preparation_time': 10,
                'calories': 150,
                'ingredients': ['Espresso beans', 'Steamed milk'],
                'allergens': ['Dairy'],
                'inventory_count': 100
            },
            {
                'name': 'Americano',
                'description': 'Espresso shots with hot water',
                'price': 150.00,
                'category_id': 1,
                'emoji': '☕',
                'preparation_time': 5,
                'calories': 10,
                'ingredients': ['Espresso beans', 'Hot water'],
                'allergens': [],
                'inventory_count': 100
            },
            
            # Cold Beverages
            {
                'name': 'Iced Coffee',
                'description': 'Refreshing cold brew coffee over ice',
                'price': 170.00,
                'category_id': 2,
                'emoji': '🧊',
                'preparation_time': 5,
                'calories': 15,
                'ingredients': ['Cold brew coffee', 'Ice'],
                'allergens': [],
                'inventory_count': 100,
                'is_featured': True
            },
            {
                'name': 'Iced Latte',
                'description': 'Espresso with cold milk over ice',
                'price': 220.00,
                'category_id': 2,
                'emoji': '🧊',
                'preparation_time': 8,
                'calories': 140,
                'ingredients': ['Espresso beans', 'Cold milk', 'Ice'],
                'allergens': ['Dairy'],
                'inventory_count': 100
            },
            {
                'name': 'Frappuccino',
                'description': 'Blended coffee drink with whipped cream',
                'price': 280.00,
                'category_id': 2,
                'emoji': '🥤',
                'preparation_time': 12,
                'calories': 250,
                'ingredients': ['Coffee', 'Milk', 'Ice', 'Whipped cream', 'Sugar'],
                'allergens': ['Dairy'],
                'inventory_count': 100
            },
            
            # Pastries
            {
                'name': 'Croissant',
                'description': 'Buttery, flaky French pastry',
                'price': 120.00,
                'category_id': 3,
                'emoji': '🥐',
                'preparation_time': 2,
                'calories': 230,
                'ingredients': ['Flour', 'Butter', 'Yeast', 'Salt'],
                'allergens': ['Gluten', 'Dairy'],
                'inventory_count': 50,
                'is_featured': True
            },
            {
                'name': 'Chocolate Muffin',
                'description': 'Rich chocolate muffin with chocolate chips',
                'price': 150.00,
                'category_id': 3,
                'emoji': '🧁',
                'preparation_time': 2,
                'calories': 320,
                'ingredients': ['Flour', 'Chocolate', 'Eggs', 'Butter', 'Sugar'],
                'allergens': ['Gluten', 'Dairy', 'Eggs'],
                'inventory_count': 30
            },
            {
                'name': 'Blueberry Scone',
                'description': 'Traditional scone with fresh blueberries',
                'price': 140.00,
                'category_id': 3,
                'emoji': '🫐',
                'preparation_time': 2,
                'calories': 280,
                'ingredients': ['Flour', 'Blueberries', 'Butter', 'Sugar', 'Cream'],
                'allergens': ['Gluten', 'Dairy'],
                'inventory_count': 25
            },
            
            # Sandwiches
            {
                'name': 'Club Sandwich',
                'description': 'Triple-decker with chicken, bacon, lettuce, tomato',
                'price': 320.00,
                'category_id': 4,
                'emoji': '🥪',
                'preparation_time': 15,
                'calories': 450,
                'ingredients': ['Bread', 'Chicken', 'Bacon', 'Lettuce', 'Tomato', 'Mayo'],
                'allergens': ['Gluten'],
                'inventory_count': 20
            },
            {
                'name': 'Grilled Cheese',
                'description': 'Classic grilled cheese sandwich',
                'price': 180.00,
                'category_id': 4,
                'emoji': '🧀',
                'preparation_time': 10,
                'calories': 350,
                'ingredients': ['Bread', 'Cheese', 'Butter'],
                'allergens': ['Gluten', 'Dairy'],
                'inventory_count': 25
            },
            
            # Desserts
            {
                'name': 'Tiramisu',
                'description': 'Classic Italian coffee-flavored dessert',
                'price': 250.00,
                'category_id': 5,
                'emoji': '🍰',
                'preparation_time': 5,
                'calories': 400,
                'ingredients': ['Mascarpone', 'Coffee', 'Ladyfingers', 'Cocoa'],
                'allergens': ['Dairy', 'Eggs', 'Gluten'],
                'inventory_count': 15,
                'is_featured': True
            },
            {
                'name': 'Cheesecake',
                'description': 'Creamy New York style cheesecake',
                'price': 220.00,
                'category_id': 5,
                'emoji': '🍰',
                'preparation_time': 5,
                'calories': 380,
                'ingredients': ['Cream cheese', 'Graham crackers', 'Sugar', 'Eggs'],
                'allergens': ['Dairy', 'Eggs', 'Gluten'],
                'inventory_count': 12
            }
        ]
        
        for item_data in menu_items_data:
            menu_item = MenuItem(**item_data)
            db.session.add(menu_item)
        
        logger.info("✅ Sample data created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create sample data: {str(e)}")
        raise e

@with_transaction
def create_sample_orders():
    """Create sample orders to test the system"""
    try:
        logger.info("Creating sample orders...")
        
        # Get users and menu items
        users = User.query.filter_by(is_admin=False).all()
        menu_items = MenuItem.query.all()
        
        if not users or not menu_items:
            logger.warning("No users or menu items found, skipping order creation")
            return
        
        # Create sample orders
        import random
        from decimal import Decimal
        
        for i, user in enumerate(users[:2]):  # Create orders for first 2 users
            # Add order items first to calculate totals
            selected_items = random.sample(menu_items, min(3, len(menu_items)))
            subtotal = Decimal('0.00')

            # Calculate totals first
            for menu_item in selected_items:
                quantity = random.randint(1, 2)
                subtotal += menu_item.price * quantity

            tax_amount = subtotal * Decimal('0.18')  # 18% GST
            total_amount = subtotal + tax_amount

            # Create order with proper totals
            order = Order(
                user_id=user.id,
                order_number=f'AF{100000 + i + 1}',
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                status='delivered' if i == 0 else 'pending',
                payment_method='upi',
                payment_status='paid' if i == 0 else 'pending',
                delivery_type='delivery',
                delivery_address=user.address
            )
            db.session.add(order)
            db.session.flush()

            # Add order items
            for menu_item in selected_items:
                quantity = random.randint(1, 2)
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=menu_item.id,
                    quantity=quantity,
                    price=menu_item.price
                )
                db.session.add(order_item)
        
        logger.info("✅ Sample orders created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create sample orders: {str(e)}")
        raise e

def main():
    """Main function to initialize the normalized database"""
    with app.app_context():
        try:
            logger.info("🚀 Starting normalized database initialization...")
            
            # Step 1: Create database structure
            create_normalized_database()
            
            # Step 2: Create sample data
            create_sample_data()
            
            # Step 3: Create sample orders
            create_sample_orders()
            
            logger.info("🎉 Normalized database initialization completed successfully!")
            logger.info("📊 Database features:")
            logger.info("  ✅ Normalized tables with proper relationships")
            logger.info("  ✅ Database triggers for audit logging")
            logger.info("  ✅ Inventory management with automatic updates")
            logger.info("  ✅ Order status history tracking")
            logger.info("  ✅ User profile management")
            logger.info("  ✅ Address normalization")
            logger.info("  ✅ Transaction management")
            logger.info("  ✅ Constraints and validations")
            logger.info("  ✅ Indexes for performance")
            
        except Exception as e:
            logger.error(f"💥 Database initialization failed: {str(e)}")
            raise e

if __name__ == '__main__':
    main()

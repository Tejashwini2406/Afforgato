from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from sqlalchemy import event, text, Index, func, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
from decimal import Decimal
import logging

db = SQLAlchemy()

# Configure logging for database operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Utility function for timezone-aware datetime
def utc_now():
    return datetime.now(timezone.utc)

# Normalized Address Table
class Address(db.Model):
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address_type = db.Column(db.Enum('home', 'work', 'other'), default='home')
    street_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False, default='Bengaluru')
    state = db.Column(db.String(100), nullable=False, default='Karnataka')
    postal_code = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(100), nullable=False, default='India')
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Constraints (SQLite compatible)
    __table_args__ = (
        CheckConstraint('length(postal_code) = 6', name='valid_postal_code_length'),
        Index('idx_user_default_address', 'user_id', 'is_default'),
    )

    @property
    def full_address(self):
        return f"{self.street_address}, {self.city}, {self.state} {self.postal_code}, {self.country}"

    def __repr__(self):
        return f'<Address {self.id}: {self.address_type}>'

# User Profile Table (Normalized)
class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum('male', 'female', 'other', 'prefer_not_to_say'))
    preferences = db.Column(db.JSON)  # Store user preferences as JSON
    loyalty_points = db.Column(db.Integer, default=0)
    total_orders = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Numeric(12, 2), default=0.00)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Constraints
    __table_args__ = (
        CheckConstraint('loyalty_points >= 0', name='positive_loyalty_points'),
        CheckConstraint('total_orders >= 0', name='positive_total_orders'),
        CheckConstraint('total_spent >= 0', name='positive_total_spent'),
    )

    def __repr__(self):
        return f'<UserProfile {self.user_id}>'

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    addresses = db.relationship('Address', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', foreign_keys='Order.user_id', backref='user', lazy=True, cascade='all, delete-orphan')
    cancelled_orders = db.relationship('Order', foreign_keys='Order.cancelled_by', backref='cancelled_by_user', lazy=True)
    cart_items = db.relationship('Cart', backref='user', lazy=True, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

    # Constraints (SQLite compatible)
    __table_args__ = (
        CheckConstraint('length(username) >= 3', name='username_min_length'),
        CheckConstraint('length(email) >= 5', name='valid_email_length'),
        CheckConstraint('length(phone) >= 10', name='valid_phone_length'),
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
        Index('idx_user_active', 'is_active'),
    )
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def address(self):
        """Get default address for backward compatibility"""
        default_addr = Address.query.filter_by(user_id=self.id, is_default=True).first()
        return default_addr.full_address if default_addr else None

    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError('Invalid email address')
        return email.lower()

    @validates('username')
    def validate_username(self, key, username):
        if len(username) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return username.lower()

    def __repr__(self):
        return f'<User {self.username}>'

# Audit Log Table for tracking changes
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=utc_now)

    # Indexes for performance
    __table_args__ = (
        Index('idx_audit_table_record', 'table_name', 'record_id'),
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_created_at', 'created_at'),
    )

    def __repr__(self):
        return f'<AuditLog {self.action} on {self.table_name}:{self.record_id}>'

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    emoji = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    menu_items = db.relationship('MenuItem', backref='category', lazy=True)

    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint('length(name) >= 2', name='category_name_min_length'),
        Index('idx_category_active', 'is_active'),
        Index('idx_category_sort', 'sort_order'),
    )

    @validates('name')
    def validate_name(self, key, name):
        if len(name.strip()) < 2:
            raise ValueError('Category name must be at least 2 characters long')
        return name.strip().title()

    def __repr__(self):
        return f'<Category {self.name}>'

class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    image_url = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    emoji = db.Column(db.String(10))
    preparation_time = db.Column(db.Integer, default=15)  # in minutes
    calories = db.Column(db.Integer)
    ingredients = db.Column(db.JSON)  # Store ingredients as JSON array
    allergens = db.Column(db.JSON)    # Store allergens as JSON array
    nutritional_info = db.Column(db.JSON)  # Store nutrition facts as JSON
    inventory_count = db.Column(db.Integer, default=100)
    min_stock_level = db.Column(db.Integer, default=10)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    order_items = db.relationship('OrderItem', backref='menu_item', lazy=True)
    cart_items = db.relationship('Cart', backref='menu_item', lazy=True)

    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint('price > 0', name='positive_price'),
        CheckConstraint('preparation_time > 0', name='positive_prep_time'),
        CheckConstraint('inventory_count >= 0', name='non_negative_inventory'),
        CheckConstraint('min_stock_level >= 0', name='non_negative_min_stock'),
        CheckConstraint('calories >= 0', name='non_negative_calories'),
        Index('idx_menu_item_category', 'category_id'),
        Index('idx_menu_item_available', 'is_available'),
        Index('idx_menu_item_featured', 'is_featured'),
        Index('idx_menu_item_price', 'price'),
    )

    @validates('price')
    def validate_price(self, key, price):
        if price <= 0:
            raise ValueError('Price must be greater than 0')
        return price

    @validates('name')
    def validate_name(self, key, name):
        if len(name.strip()) < 2:
            raise ValueError('Menu item name must be at least 2 characters long')
        return name.strip().title()

    @property
    def is_low_stock(self):
        return self.inventory_count <= self.min_stock_level

    @property
    def is_out_of_stock(self):
        return self.inventory_count <= 0

    def __repr__(self):
        return f'<MenuItem {self.name}>'

# Inventory Log Table for tracking stock changes
class InventoryLog(db.Model):
    __tablename__ = 'inventory_logs'

    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    old_quantity = db.Column(db.Integer, nullable=False)
    new_quantity = db.Column(db.Integer, nullable=False)
    change_quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Enum('sale', 'restock', 'waste', 'adjustment', 'manual'), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Indexes for performance
    __table_args__ = (
        Index('idx_inventory_menu_item', 'menu_item_id'),
        Index('idx_inventory_created_at', 'created_at'),
        Index('idx_inventory_reason', 'reason'),
    )

    def __repr__(self):
        return f'<InventoryLog {self.menu_item_id}: {self.change_quantity}>'

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(20), unique=True)  # Human-readable order number
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), default=0.00)
    tax_amount = db.Column(db.Numeric(12, 2), default=0.00)
    discount_amount = db.Column(db.Numeric(12, 2), default=0.00)
    delivery_fee = db.Column(db.Numeric(12, 2), default=0.00)
    status = db.Column(db.Enum('pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled'), default='pending')
    payment_status = db.Column(db.Enum('pending', 'paid', 'failed', 'refunded'), default='pending')
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(100))  # Payment gateway reference
    delivery_address = db.Column(db.Text)
    delivery_type = db.Column(db.Enum('delivery', 'pickup'), default='delivery')
    estimated_delivery_time = db.Column(db.DateTime)
    actual_delivery_time = db.Column(db.DateTime)
    special_instructions = db.Column(db.Text)
    notes = db.Column(db.Text)  # Admin notes
    cancelled_reason = db.Column(db.Text)
    cancelled_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint('total_amount > 0', name='positive_total_amount'),
        CheckConstraint('subtotal >= 0', name='non_negative_subtotal'),
        CheckConstraint('tax_amount >= 0', name='non_negative_tax'),
        CheckConstraint('discount_amount >= 0', name='non_negative_discount'),
        CheckConstraint('delivery_fee >= 0', name='non_negative_delivery_fee'),
        Index('idx_order_user', 'user_id'),
        Index('idx_order_status', 'status'),
        Index('idx_order_payment_status', 'payment_status'),
        Index('idx_order_created_at', 'created_at'),
        Index('idx_order_number', 'order_number'),
    )

    def generate_order_number(self):
        """Generate a unique order number"""
        import random
        import string
        while True:
            order_number = 'AF' + ''.join(random.choices(string.digits, k=6))
            if not Order.query.filter_by(order_number=order_number).first():
                return order_number

    def calculate_totals(self):
        """Calculate order totals based on items"""
        self.subtotal = sum(item.subtotal for item in self.order_items)
        self.tax_amount = self.subtotal * 0.18  # 18% GST
        self.total_amount = self.subtotal + self.tax_amount + self.delivery_fee - self.discount_amount
    
    @property
    def status_emoji(self):
        status_emojis = {
            'pending': '⏳',
            'confirmed': '✅',
            'preparing': '👨‍🍳',
            'ready': '🔔',
            'delivered': '📦',
            'cancelled': '❌'
        }
        return status_emojis.get(self.status, '❓')
    
    def __repr__(self):
        return f'<Order {self.id}>'

# Order Status History Table for tracking status changes
class OrderStatusHistory(db.Model):
    __tablename__ = 'order_status_history'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    old_status = db.Column(db.Enum('pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled'))
    new_status = db.Column(db.Enum('pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled'), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Indexes for performance
    __table_args__ = (
        Index('idx_status_history_order', 'order_id'),
        Index('idx_status_history_created_at', 'created_at'),
    )

    def __repr__(self):
        return f'<OrderStatusHistory {self.order_id}: {self.old_status} -> {self.new_status}>'

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    notes = db.Column(db.Text)
    
    @property
    def subtotal(self):
        return self.quantity * self.price
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'

class Cart(db.Model):
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=utc_now)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'menu_item_id', name='unique_user_item'),)
    
    @property
    def subtotal(self):
        return self.quantity * self.menu_item.price
    
    def __repr__(self):
        return f'<Cart {self.id}>'

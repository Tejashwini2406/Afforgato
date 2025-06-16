from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from config import Config
from models import db, User, Address, Category, MenuItem, Order, OrderItem, Cart
from database_triggers import DatabaseTransactionManager, DatabaseCursor, with_transaction, with_rollback_on_error
import os
from decimal import Decimal
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Add custom filters
@app.template_filter('timestamp_to_time')
def timestamp_to_time(timestamp):
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).strftime('%I:%M %p')

@app.template_filter('to_float')
def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0
login_manager.login_message = '☕ Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    featured_items = MenuItem.query.filter_by(is_available=True).limit(6).all()
    categories = Category.query.all()
    return render_template('index.html', featured_items=featured_items, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.first_name}! ☕', 'success')
            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
            return redirect(next_page) if next_page else redirect(url_for('menu'))

        flash('Invalid username or password! ❌', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("Registration form submitted!")
        print(f"Form data: {request.form}")

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')

        print(f"Attempting to register user: {username}, {email}")

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists! 😔', 'error')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered! 📧', 'error')
            return render_template('register.html')

        # Create new user
        try:
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            user.set_password(password)

            db.session.add(user)
            db.session.commit()  # Commit to get user ID

            # Create address if provided
            if address and address.strip():
                user_address = Address(
                    user_id=user.id,
                    address_type='home',
                    street_address=address,
                    city='Bengaluru',
                    state='Karnataka',
                    postal_code='560001',
                    country='India',
                    is_default=True
                )
                db.session.add(user_address)
                db.session.commit()

            print(f"User {username} created successfully!")
            flash('Registration successful! Welcome to Afforgato! 🎉', 'success')
            login_user(user)
            return redirect(url_for('registration_success'))
        except Exception as e:
            print(f"Error creating user: {e}")
            db.session.rollback()
            flash('Registration failed. Please try again! ❌', 'error')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/registration_success')
@login_required
def registration_success():
    return render_template('registration_success.html')

@app.route('/register_simple')
def register_simple():
    return render_template('register_simple.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out. See you soon! 👋', 'info')
    return redirect(url_for('index'))

@app.route('/menu')
def menu():
    categories = Category.query.all()
    category_id = request.args.get('category', type=int)
    
    if category_id:
        menu_items = MenuItem.query.filter_by(category_id=category_id, is_available=True).all()
        selected_category = Category.query.get(category_id)
    else:
        menu_items = MenuItem.query.filter_by(is_available=True).all()
        selected_category = None
    
    return render_template('menu.html', 
                         categories=categories, 
                         menu_items=menu_items, 
                         selected_category=selected_category)

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    menu_item_id = request.form.get('menu_item_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    menu_item = MenuItem.query.get_or_404(menu_item_id)
    
    # Check if item already in cart
    cart_item = Cart.query.filter_by(user_id=current_user.id, menu_item_id=menu_item_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=current_user.id, menu_item_id=menu_item_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'{menu_item.name} added to cart! 🛒', 'success')

    # Get updated cart count
    cart_count = db.session.query(db.func.sum(Cart.quantity)).filter_by(user_id=current_user.id).scalar() or 0

    if request.form.get('ajax'):
        return jsonify({'success': True, 'message': 'Item added to cart!', 'cart_count': cart_count})

    return redirect(url_for('menu'))

@app.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total = sum(item.subtotal for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart', methods=['POST'])
@login_required
def update_cart():
    cart_id = request.form.get('cart_id', type=int)
    quantity = request.form.get('quantity', type=int)
    
    cart_item = Cart.query.filter_by(id=cart_id, user_id=current_user.id).first_or_404()
    
    if quantity <= 0:
        db.session.delete(cart_item)
        flash('Item removed from cart! 🗑️', 'info')
    else:
        cart_item.quantity = quantity
        flash('Cart updated! ✅', 'success')
    
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash('Your cart is empty! 🛒', 'warning')
        return redirect(url_for('menu'))

    # Calculate totals with tax
    subtotal = sum(item.subtotal for item in cart_items)
    tax_amount = subtotal * Decimal('0.18')  # 18% GST
    total = subtotal + tax_amount

    if request.method == 'POST':
        try:
            payment_method = request.form.get('payment_method')
            delivery_address = request.form.get('delivery_address', current_user.address)
            special_instructions = request.form.get('special_instructions', '')
            notes = request.form.get('notes', '')

            # Create order with enhanced data
            order = Order(
                user_id=current_user.id,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total,
                payment_method=payment_method,
                delivery_address=delivery_address,
                special_instructions=special_instructions,
                notes=notes
            )

            # Generate order number
            order.order_number = order.generate_order_number()
            db.session.add(order)
            db.session.flush()  # Get order ID

            # Create order items (triggers will handle inventory updates)
            for cart_item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=cart_item.menu_item_id,
                    quantity=cart_item.quantity,
                    price=cart_item.menu_item.price
                )
                db.session.add(order_item)

            # Clear cart
            Cart.query.filter_by(user_id=current_user.id).delete()

            # Commit transaction
            db.session.commit()

            flash(f'Order placed successfully! Order #{order.order_number} 🎉', 'success')
            return redirect(url_for('payment', order_id=order.id))

        except Exception as e:
            db.session.rollback()
            flash('Error placing order. Please try again! ❌', 'error')
            return redirect(url_for('cart'))

    return render_template('checkout.html', cart_items=cart_items, subtotal=subtotal, tax_amount=tax_amount, total=total)

@app.route('/payment/<int:order_id>')
@login_required
def payment(order_id):
    try:
        order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()

        # Ensure order has required fields
        if not order.order_number:
            order.order_number = order.generate_order_number()
            db.session.commit()

        return render_template('payment.html', order=order)
    except Exception as e:
        flash('Error loading payment page. Please try again! ❌', 'error')
        return redirect(url_for('cart'))

@app.route('/process_payment/<int:order_id>', methods=['POST'])
@login_required
def process_payment(order_id):
    try:
        order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()

        # Simulate payment processing
        order.payment_status = 'paid'
        order.status = 'confirmed'
        order.updated_at = datetime.now()

        db.session.commit()

        flash(f'Payment successful! Your order #{order.order_number or order.id} is confirmed! 💳✅', 'success')
        return redirect(url_for('orders'))

    except Exception as e:
        db.session.rollback()
        flash('Payment processing failed. Please try again! ❌', 'error')
        return redirect(url_for('payment', order_id=order_id))

@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)

# Admin routes
@app.route('/clear_cart', methods=['POST'])
@login_required
def clear_cart():
    Cart.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Cart cleared successfully!'})

@app.route('/get_cart_count')
@login_required
def get_cart_count():
    cart_count = db.session.query(db.func.sum(Cart.quantity)).filter_by(user_id=current_user.id).scalar() or 0
    return jsonify({'cart_count': cart_count})

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied! Admin privileges required! 🚫', 'error')
        return redirect(url_for('index'))

    total_users = User.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter_by(payment_status='paid').scalar() or 0

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()

    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders)

# Admin - Update Order Status
@app.route('/admin/update_order_status', methods=['POST'])
@login_required
def update_order_status():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'})

    data = request.get_json()
    order_id = data.get('order_id')
    new_status = data.get('status')

    order = Order.query.get_or_404(order_id)
    order.status = new_status
    db.session.commit()

    return jsonify({'success': True, 'message': 'Order status updated'})

# Admin - Manage Users
@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied! 🚫', 'error')
        return redirect(url_for('index'))

    search = request.args.get('search', '')
    role_filter = request.args.get('role', 'all')

    query = User.query

    if search:
        query = query.filter(
            db.or_(
                User.first_name.contains(search),
                User.last_name.contains(search),
                User.username.contains(search),
                User.email.contains(search)
            )
        )

    if role_filter == 'admin':
        query = query.filter(User.is_admin == True)
    elif role_filter == 'customer':
        query = query.filter(User.is_admin == False)

    users = query.order_by(User.created_at.desc()).all()

    # Get user statistics
    total_users = User.query.count()
    admin_users = User.query.filter_by(is_admin=True).count()
    customer_users = total_users - admin_users

    return render_template('admin_users.html',
                         users=users,
                         search=search,
                         role_filter=role_filter,
                         total_users=total_users,
                         admin_users=admin_users,
                         customer_users=customer_users)

# Admin - Manage Menu
@app.route('/admin/menu')
@login_required
def admin_menu():
    if not current_user.is_admin:
        flash('Access denied! 🚫', 'error')
        return redirect(url_for('index'))

    categories = Category.query.all()
    menu_items = MenuItem.query.all()
    return render_template('admin_menu.html', categories=categories, menu_items=menu_items)

# Admin - Add Menu Item
@app.route('/admin/menu/add', methods=['GET', 'POST'])
@login_required
def admin_add_menu_item():
    if not current_user.is_admin:
        flash('Access denied! 🚫', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        category_id = int(request.form['category_id'])
        emoji = request.form.get('emoji', '☕')

        menu_item = MenuItem(
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            emoji=emoji
        )

        db.session.add(menu_item)
        db.session.commit()

        flash(f'Menu item "{name}" added successfully! ✅', 'success')
        return redirect(url_for('admin_menu'))

    categories = Category.query.all()
    return render_template('admin_add_menu_item.html', categories=categories)

# Admin - Edit Menu Item
@app.route('/admin/menu/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_menu_item(item_id):
    if not current_user.is_admin:
        flash('Access denied! 🚫', 'error')
        return redirect(url_for('index'))

    menu_item = MenuItem.query.get_or_404(item_id)

    if request.method == 'POST':
        menu_item.name = request.form['name']
        menu_item.description = request.form['description']
        menu_item.price = float(request.form['price'])
        menu_item.category_id = int(request.form['category_id'])
        menu_item.emoji = request.form.get('emoji', '☕')
        menu_item.is_available = 'is_available' in request.form

        db.session.commit()

        flash(f'Menu item "{menu_item.name}" updated successfully! ✅', 'success')
        return redirect(url_for('admin_menu'))

    categories = Category.query.all()
    return render_template('admin_edit_menu_item.html', menu_item=menu_item, categories=categories)

# Admin - Delete Menu Item
@app.route('/admin/menu/delete/<int:item_id>', methods=['POST'])
@login_required
def admin_delete_menu_item(item_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'})

    menu_item = MenuItem.query.get_or_404(item_id)
    db.session.delete(menu_item)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Menu item deleted successfully'})

# Admin - Orders Management
@app.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.is_admin:
        flash('Access denied! 🚫', 'error')
        return redirect(url_for('index'))

    status_filter = request.args.get('status', 'all')

    if status_filter == 'all':
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(status=status_filter).order_by(Order.created_at.desc()).all()

    return render_template('admin_orders.html', orders=orders, status_filter=status_filter)

# Admin - View User Details
@app.route('/admin/users/<int:user_id>')
@login_required
def admin_view_user(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'})

    user = User.query.get_or_404(user_id)
    user_orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

    # Calculate user statistics
    total_orders = len(user_orders)
    total_spent = sum(order.total_amount for order in user_orders if order.payment_status == 'paid')
    avg_order_value = total_spent / total_orders if total_orders > 0 else 0

    return render_template('admin_user_details.html',
                         user=user,
                         orders=user_orders,
                         total_orders=total_orders,
                         total_spent=total_spent,
                         avg_order_value=avg_order_value)

# Admin - Edit User
@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if not current_user.is_admin:
        flash('Access denied! 🚫', 'error')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        user.phone = request.form.get('phone')
        user.address = request.form.get('address')

        # Handle admin status change
        if user.id != current_user.id:  # Can't change own admin status
            user.is_admin = 'is_admin' in request.form

        db.session.commit()
        flash(f'User {user.full_name} updated successfully! ✅', 'success')
        return redirect(url_for('admin_users'))

    return render_template('admin_edit_user.html', user=user)

# Admin - Delete User
@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'})

    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot delete your own account'})

    user = User.query.get_or_404(user_id)

    # Check if user has orders
    user_orders = Order.query.filter_by(user_id=user_id).count()
    if user_orders > 0:
        return jsonify({'success': False, 'message': 'Cannot delete user with existing orders'})

    # Delete user's cart items first
    Cart.query.filter_by(user_id=user_id).delete()

    db.session.delete(user)
    db.session.commit()

    return jsonify({'success': True, 'message': f'User {user.full_name} deleted successfully'})

# Admin - Toggle User Admin Status
@app.route('/admin/users/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
def admin_toggle_user_admin(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'})

    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot change your own admin status'})

    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()

    status = 'Admin' if user.is_admin else 'Customer'
    return jsonify({'success': True, 'message': f'{user.full_name} is now a {status}'})

# Admin - View Order Details
@app.route('/admin/orders/<int:order_id>')
@login_required
def admin_view_order(order_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'})

    order = Order.query.get_or_404(order_id)
    return render_template('admin_order_details.html', order=order)

# Admin - Update Order
@app.route('/admin/orders/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_order(order_id):
    if not current_user.is_admin:
        flash('Access denied! 🚫', 'error')
        return redirect(url_for('index'))

    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        order.status = request.form['status']
        order.payment_status = request.form['payment_status']
        order.delivery_address = request.form['delivery_address']
        order.special_instructions = request.form.get('special_instructions')
        order.notes = request.form.get('notes')

        db.session.commit()
        flash(f'Order #{order.id} updated successfully! ✅', 'success')
        return redirect(url_for('admin_orders'))

    return render_template('admin_edit_order.html', order=order)

# Admin - Delete Order
@app.route('/admin/orders/<int:order_id>/delete', methods=['POST'])
@login_required
def admin_delete_order(order_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'})

    order = Order.query.get_or_404(order_id)

    # Delete order items first
    OrderItem.query.filter_by(order_id=order_id).delete()

    db.session.delete(order)
    db.session.commit()

    return jsonify({'success': True, 'message': f'Order #{order.id} deleted successfully'})

# Admin - Update Order Status (AJAX)
@app.route('/admin/update_order_status', methods=['POST'])
@login_required
def admin_update_order_status():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'})

    data = request.get_json()
    order_id = data.get('order_id')
    new_status = data.get('status')

    if not order_id or not new_status:
        return jsonify({'success': False, 'message': 'Missing order ID or status'})

    order = Order.query.get_or_404(order_id)
    order.status = new_status
    order.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True, 'message': f'Order status updated to {new_status}'})

# Admin - Analytics Dashboard with Enhanced Database Cursors
@app.route('/admin/analytics')
@login_required
def admin_analytics():
    if not current_user.is_admin:
        flash('Access denied! 🚫', 'error')
        return redirect(url_for('index'))

    try:
        # Use database cursor for complex analytics
        revenue_data = DatabaseCursor.get_revenue_analytics()

        # Calculate totals from revenue data
        total_revenue = sum(day['total_revenue'] for day in revenue_data) if revenue_data else 0
        monthly_revenue = sum(day['total_revenue'] for day in revenue_data[-30:]) if revenue_data else 0

        # Order analytics
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        completed_orders = Order.query.filter_by(status='delivered').count()

        # User analytics
        total_users = User.query.count()
        new_users_this_month = User.query.filter(
            db.func.strftime('%Y-%m', User.created_at) == db.func.strftime('%Y-%m', db.func.now())
        ).count()

        # Popular items using cursor
        popular_items = DatabaseCursor.get_popular_menu_items(limit=5)

        return render_template('admin_analytics.html',
                             total_revenue=total_revenue,
                             monthly_revenue=monthly_revenue,
                             total_orders=total_orders,
                             pending_orders=pending_orders,
                             completed_orders=completed_orders,
                             total_users=total_users,
                             new_users_this_month=new_users_this_month,
                             popular_items=popular_items,
                             revenue_data=revenue_data)

    except Exception as e:
        flash('Error loading analytics data! 📊❌', 'error')
        return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

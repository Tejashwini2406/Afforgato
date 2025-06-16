"""
Database Triggers and Transactions for Afforgato Cafe
Implements cursor-based triggers, normalization, and transaction management
"""

from sqlalchemy import event, text, func
from sqlalchemy.orm import Session
from models import db, User, UserProfile, Order, OrderItem, MenuItem, AuditLog, InventoryLog, OrderStatusHistory
from datetime import datetime, timezone
import logging
import json

logger = logging.getLogger(__name__)

class DatabaseTransactionManager:
    """Manages database transactions with proper rollback and commit handling"""
    
    @staticmethod
    def execute_with_transaction(func, *args, **kwargs):
        """Execute a function within a database transaction"""
        try:
            result = func(*args, **kwargs)
            db.session.commit()
            logger.info(f"Transaction completed successfully: {func.__name__}")
            return result
        except Exception as e:
            db.session.rollback()
            logger.error(f"Transaction failed, rolled back: {func.__name__} - {str(e)}")
            raise e

    @staticmethod
    def bulk_insert_with_transaction(model_class, data_list):
        """Bulk insert with transaction management"""
        try:
            db.session.bulk_insert_mappings(model_class, data_list)
            db.session.commit()
            logger.info(f"Bulk insert completed: {len(data_list)} records of {model_class.__name__}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Bulk insert failed: {str(e)}")
            raise e

    @staticmethod
    def execute_raw_sql_with_transaction(sql_query, params=None):
        """Execute raw SQL with transaction management"""
        try:
            result = db.session.execute(text(sql_query), params or {})
            db.session.commit()
            logger.info(f"Raw SQL executed successfully")
            return result
        except Exception as e:
            db.session.rollback()
            logger.error(f"Raw SQL execution failed: {str(e)}")
            raise e

# Audit Logging Functions
def create_audit_log(table_name, record_id, action, old_values=None, new_values=None, user_id=None):
    """Create an audit log entry"""
    try:
        audit_log = AuditLog(
            table_name=table_name,
            record_id=record_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            user_id=user_id
        )
        db.session.add(audit_log)
        db.session.flush()  # Flush to get the ID without committing
        logger.info(f"Audit log created: {action} on {table_name}:{record_id}")
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")

# User-related Triggers
@event.listens_for(User, 'after_insert')
def create_user_profile_trigger(mapper, connection, target):
    """Automatically create user profile when user is created"""
    try:
        # Create user profile
        profile = UserProfile(user_id=target.id)
        db.session.add(profile)
        
        # Create audit log
        create_audit_log('users', target.id, 'INSERT', 
                        new_values={'username': target.username, 'email': target.email})
        
        logger.info(f"User profile created for user {target.id}")
    except Exception as e:
        logger.error(f"Failed to create user profile: {str(e)}")

@event.listens_for(User, 'after_update')
def user_update_trigger(mapper, connection, target):
    """Trigger after user update"""
    try:
        # Get the session to access the original values
        session = Session.object_session(target)
        if session:
            # Create audit log for user updates
            create_audit_log('users', target.id, 'UPDATE', user_id=target.id)
            logger.info(f"User {target.id} updated")
    except Exception as e:
        logger.error(f"User update trigger failed: {str(e)}")

@event.listens_for(User, 'after_delete')
def user_delete_trigger(mapper, connection, target):
    """Trigger after user deletion"""
    try:
        create_audit_log('users', target.id, 'DELETE', 
                        old_values={'username': target.username, 'email': target.email})
        logger.info(f"User {target.id} deleted")
    except Exception as e:
        logger.error(f"User delete trigger failed: {str(e)}")

# Order-related Triggers
@event.listens_for(Order, 'after_insert')
def order_insert_trigger(mapper, connection, target):
    """Trigger after order creation"""
    try:
        # Generate order number if not set
        if not target.order_number:
            target.order_number = target.generate_order_number()
        
        # Create initial status history
        status_history = OrderStatusHistory(
            order_id=target.id,
            old_status=None,
            new_status=target.status,
            changed_by=target.user_id
        )
        db.session.add(status_history)
        
        # Update user profile statistics
        profile = UserProfile.query.filter_by(user_id=target.user_id).first()
        if profile:
            profile.total_orders += 1
            profile.total_spent += float(target.total_amount)
        
        # Create audit log
        create_audit_log('orders', target.id, 'INSERT', 
                        new_values={'user_id': target.user_id, 'total_amount': str(target.total_amount)},
                        user_id=target.user_id)
        
        logger.info(f"Order {target.id} created with number {target.order_number}")
    except Exception as e:
        logger.error(f"Order insert trigger failed: {str(e)}")

@event.listens_for(Order, 'after_update')
def order_update_trigger(mapper, connection, target):
    """Trigger after order update"""
    try:
        # Check if status changed
        session = Session.object_session(target)
        if session and hasattr(target, '_sa_instance_state'):
            # Get the original status from the session
            original_status = session.identity_map.get((Order, target.id))
            if original_status and hasattr(original_status, 'status'):
                if original_status.status != target.status:
                    # Create status history entry
                    status_history = OrderStatusHistory(
                        order_id=target.id,
                        old_status=original_status.status,
                        new_status=target.status
                    )
                    db.session.add(status_history)
        
        # Create audit log
        create_audit_log('orders', target.id, 'UPDATE', user_id=target.user_id)
        
        logger.info(f"Order {target.id} updated")
    except Exception as e:
        logger.error(f"Order update trigger failed: {str(e)}")

# OrderItem-related Triggers
@event.listens_for(OrderItem, 'after_insert')
def order_item_insert_trigger(mapper, connection, target):
    """Trigger after order item creation - update inventory"""
    try:
        # Update menu item inventory
        menu_item = MenuItem.query.get(target.menu_item_id)
        if menu_item:
            old_inventory = menu_item.inventory_count
            menu_item.inventory_count -= target.quantity
            
            # Create inventory log
            inventory_log = InventoryLog(
                menu_item_id=target.menu_item_id,
                old_quantity=old_inventory,
                new_quantity=menu_item.inventory_count,
                change_quantity=-target.quantity,
                reason='sale',
                notes=f'Order #{target.order_id}'
            )
            db.session.add(inventory_log)
            
            # Update availability if out of stock
            if menu_item.inventory_count <= 0:
                menu_item.is_available = False
        
        # Create audit log
        create_audit_log('order_items', target.id, 'INSERT',
                        new_values={'order_id': target.order_id, 'menu_item_id': target.menu_item_id, 'quantity': target.quantity})
        
        logger.info(f"Order item {target.id} created, inventory updated")
    except Exception as e:
        logger.error(f"Order item insert trigger failed: {str(e)}")

@event.listens_for(OrderItem, 'after_delete')
def order_item_delete_trigger(mapper, connection, target):
    """Trigger after order item deletion - restore inventory"""
    try:
        # Restore menu item inventory
        menu_item = MenuItem.query.get(target.menu_item_id)
        if menu_item:
            old_inventory = menu_item.inventory_count
            menu_item.inventory_count += target.quantity
            
            # Create inventory log
            inventory_log = InventoryLog(
                menu_item_id=target.menu_item_id,
                old_quantity=old_inventory,
                new_quantity=menu_item.inventory_count,
                change_quantity=target.quantity,
                reason='adjustment',
                notes=f'Order item deleted from Order #{target.order_id}'
            )
            db.session.add(inventory_log)
            
            # Update availability if back in stock
            if menu_item.inventory_count > 0 and not menu_item.is_available:
                menu_item.is_available = True
        
        # Create audit log
        create_audit_log('order_items', target.id, 'DELETE',
                        old_values={'order_id': target.order_id, 'menu_item_id': target.menu_item_id, 'quantity': target.quantity})
        
        logger.info(f"Order item {target.id} deleted, inventory restored")
    except Exception as e:
        logger.error(f"Order item delete trigger failed: {str(e)}")

# MenuItem-related Triggers
@event.listens_for(MenuItem, 'after_update')
def menu_item_update_trigger(mapper, connection, target):
    """Trigger after menu item update"""
    try:
        # Create audit log
        create_audit_log('menu_items', target.id, 'UPDATE',
                        new_values={'name': target.name, 'price': str(target.price), 'is_available': target.is_available})
        
        logger.info(f"Menu item {target.id} updated")
    except Exception as e:
        logger.error(f"Menu item update trigger failed: {str(e)}")

# Database Cursor Functions for Complex Queries
class DatabaseCursor:
    """Provides cursor-like functionality for complex database operations"""
    
    @staticmethod
    def get_user_order_statistics(user_id):
        """Get comprehensive user order statistics using cursor-like approach"""
        try:
            query = text("""
                SELECT 
                    u.id,
                    u.username,
                    u.email,
                    COUNT(o.id) as total_orders,
                    COALESCE(SUM(o.total_amount), 0) as total_spent,
                    COALESCE(AVG(o.total_amount), 0) as avg_order_value,
                    MAX(o.created_at) as last_order_date,
                    COUNT(CASE WHEN o.status = 'delivered' THEN 1 END) as completed_orders
                FROM users u
                LEFT JOIN orders o ON u.id = o.user_id
                WHERE u.id = :user_id
                GROUP BY u.id, u.username, u.email
            """)
            
            result = db.session.execute(query, {'user_id': user_id}).fetchone()
            return dict(result._mapping) if result else None
        except Exception as e:
            logger.error(f"Failed to get user statistics: {str(e)}")
            return None
    
    @staticmethod
    def get_popular_menu_items(limit=10):
        """Get popular menu items using cursor-like approach"""
        try:
            query = text("""
                SELECT 
                    mi.id,
                    mi.name,
                    mi.emoji,
                    mi.price,
                    COUNT(oi.id) as order_count,
                    SUM(oi.quantity) as total_quantity,
                    SUM(oi.quantity * oi.price) as total_revenue
                FROM menu_items mi
                LEFT JOIN order_items oi ON mi.id = oi.menu_item_id
                LEFT JOIN orders o ON oi.order_id = o.id
                WHERE o.status != 'cancelled'
                GROUP BY mi.id, mi.name, mi.emoji, mi.price
                ORDER BY total_quantity DESC
                LIMIT :limit
            """)
            
            result = db.session.execute(query, {'limit': limit}).fetchall()
            return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Failed to get popular menu items: {str(e)}")
            return []
    
    @staticmethod
    def get_revenue_analytics(start_date=None, end_date=None):
        """Get revenue analytics using cursor-like approach"""
        try:
            query = text("""
                SELECT 
                    DATE(o.created_at) as order_date,
                    COUNT(o.id) as total_orders,
                    SUM(o.total_amount) as total_revenue,
                    AVG(o.total_amount) as avg_order_value,
                    COUNT(DISTINCT o.user_id) as unique_customers
                FROM orders o
                WHERE o.payment_status = 'paid'
                AND (:start_date IS NULL OR o.created_at >= :start_date)
                AND (:end_date IS NULL OR o.created_at <= :end_date)
                GROUP BY DATE(o.created_at)
                ORDER BY order_date DESC
            """)
            
            result = db.session.execute(query, {
                'start_date': start_date,
                'end_date': end_date
            }).fetchall()
            
            return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Failed to get revenue analytics: {str(e)}")
            return []

# Initialize all triggers
def initialize_database_triggers():
    """Initialize all database triggers and constraints"""
    logger.info("Database triggers and constraints initialized")
    
    # Create any additional database constraints or indexes here
    try:
        # Example: Create a function to automatically update timestamps
        db.session.execute(text("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """))
        
        logger.info("Database functions created successfully")
    except Exception as e:
        logger.warning(f"Could not create database functions (may not be PostgreSQL): {str(e)}")

# Transaction Decorators
def with_transaction(func):
    """Decorator to wrap function in database transaction"""
    def wrapper(*args, **kwargs):
        return DatabaseTransactionManager.execute_with_transaction(func, *args, **kwargs)
    return wrapper

def with_rollback_on_error(func):
    """Decorator to rollback on any error"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Function {func.__name__} failed, rolled back: {str(e)}")
            raise e
    return wrapper

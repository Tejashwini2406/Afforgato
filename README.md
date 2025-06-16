# ☕ Afforgato Cafe - Order Management System

A modern, full-featured cafe order management system built with Python Flask, MariaDB, and glassmorphism design.

## 🌟 Features

### 🎨 Design
- **Glassmorphism UI** with brown/black/white color scheme
- **Responsive design** that works on all devices
- **Smooth animations** and interactive effects
- **Coffee-themed emojis** throughout the interface

### 👥 User Management
- **User Registration & Login** with secure authentication
- **Admin Dashboard** for management
- **Profile management** with order history
- **Role-based access control**

### 🛒 Order System
- **Dynamic menu** with categories and items
- **Shopping cart** with quantity controls
- **Checkout process** with multiple payment options
- **Order tracking** with real-time status updates
- **Order history** and reordering functionality

### 💳 Payment System
- **Multiple payment methods** (Credit Card, PayPal, Apple Pay, Cash)
- **Secure payment processing** simulation
- **Payment status tracking**
- **Receipt generation**

### 👨‍💼 Admin Features
- **Dashboard** with analytics and statistics
- **Order management** with status updates
- **User management**
- **Menu item management**
- **Real-time order monitoring**

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MariaDB 10.4+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Afforgato
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup MariaDB**
   - Install MariaDB from [https://mariadb.org/download/](https://mariadb.org/download/)
   - Start MariaDB service
   - Ensure root user access (default: no password)

4. **Run setup script**
   ```bash
   python setup.py
   ```

5. **Start the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Use demo accounts to explore features

## 🔐 Demo Accounts

### Admin Account
- **Username:** `admin`
- **Password:** `admin123`
- **Access:** Full admin dashboard and management features

### User Account
- **Username:** `demo`
- **Password:** `demo123`
- **Access:** Customer features (ordering, cart, profile)

## 📁 Project Structure

```
Afforgato/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── config.py              # Configuration settings
├── setup.py               # Setup script
├── requirements.txt       # Python dependencies
├── database.sql           # Database schema and sample data
├── templates/             # HTML templates
│   ├── base.html         # Base template with glassmorphism
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── menu.html         # Menu display
│   ├── cart.html         # Shopping cart
│   ├── checkout.html     # Checkout process
│   ├── payment.html      # Payment processing
│   ├── orders.html       # Order history
│   └── admin_dashboard.html # Admin dashboard
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Glassmorphism styles
│   ├── js/
│   │   └── main.js       # JavaScript functionality
│   ├── images/           # Image assets
│   └── uploads/          # File uploads
└── README.md             # This file
```

## 🎨 Design Features

### Glassmorphism Effects
- **Backdrop blur** for glass-like appearance
- **Transparent backgrounds** with subtle borders
- **Layered depth** with shadows and highlights
- **Smooth transitions** and hover effects

### Color Scheme
- **Primary Brown:** `#8B4513` (Saddle Brown)
- **Secondary Brown:** `#A0522D` (Sienna)
- **Black Primary:** `#1a1a1a` (Rich Black)
- **White Primary:** `#ffffff` (Pure White)

### Interactive Elements
- **Animated buttons** with hover effects
- **Floating animations** for background elements
- **Smooth page transitions**
- **Real-time form validation**

## 🗄️ Database Schema

### Tables
- **users** - User accounts and profiles
- **categories** - Menu categories
- **menu_items** - Food and drink items
- **orders** - Customer orders
- **order_items** - Individual order items
- **cart** - Shopping cart items

### Sample Data
- Pre-loaded menu categories (Hot Coffee, Cold Coffee, Tea, Pastries, etc.)
- Sample menu items with prices and descriptions
- Demo user accounts for testing

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```env
SECRET_KEY=your-secret-key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DB=afforgato_cafe
```

### Database Configuration
- **Host:** localhost (default)
- **Database:** afforgato_cafe
- **User:** root (default)
- **Password:** empty (default)

## 🚀 Deployment

### Development
```bash
python app.py
```
Access at `http://localhost:5000`

### Production
1. Set `FLASK_ENV=production` in `.env`
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure reverse proxy (e.g., Nginx)
4. Set up SSL certificates
5. Use production database credentials

## 🛠️ Customization

### Adding Menu Items
1. Access admin dashboard
2. Navigate to menu management
3. Add categories and items
4. Set prices and availability

### Styling Changes
- Edit `static/css/style.css` for design changes
- Modify color variables in CSS root
- Update glassmorphism effects

### Adding Features
- Extend models in `models.py`
- Add routes in `app.py`
- Create templates in `templates/`
- Add JavaScript in `static/js/main.js`

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
- Ensure MariaDB is running
- Check credentials in `.env` file
- Verify database exists

**Import Errors**
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)

**Port Already in Use**
- Change port in `app.py`: `app.run(port=5001)`
- Or kill process using port 5000

**Static Files Not Loading**
- Check file paths in templates
- Ensure static folder structure is correct
- Clear browser cache

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

## 🎉 Acknowledgments

- **Flask** - Web framework
- **Bootstrap** - UI components
- **Font Awesome** - Icons
- **Google Fonts** - Typography
- **MariaDB** - Database system

---

**Enjoy your coffee and happy coding! ☕✨**

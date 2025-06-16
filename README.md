# ☕ Afforgato Coffee Shop Database Management System

A comprehensive database management system for coffee shop operations built with MariaDB, Flask, HTML, CSS, and JavaScript.

## 🏪 About Afforgato

**Afforgato** is a modern coffee shop management system designed to streamline operations, enhance customer experience, and provide comprehensive business analytics. The system manages customer registration, menu catalog, order processing, inventory tracking, and administrative functions through a user-friendly web interface.

*Owned by Tejashwini, Srujana* | 📍 Bengaluru, Karnataka, India

## ✨ Features

### 👥 Customer Features
- **User Registration & Authentication** - Secure account creation and login
- **Menu Browsing** - Browse coffee items by categories with detailed descriptions
- **Shopping Cart** - Add items to cart with quantity management
- **Order Placement** - Seamless checkout and order processing
- **Order Tracking** - Real-time order status updates
- **Profile Management** - Manage personal information and addresses

### 🔧 Admin Features
- **Dashboard Analytics** - Comprehensive business insights and statistics
- **Menu Management** - Add, update, and remove menu items
- **Category Management** - Organize menu items by categories
- **Order Management** - Track and update order status
- **Inventory Control** - Real-time stock management and alerts
- **User Management** - Manage customer accounts and staff
- **Audit Logs** - Complete activity tracking and reporting

### 🎨 Design Features
- **Glassmorphism UI** - Modern design with brown/black/white color scheme
- **Coffee Bean Background** - Attractive coffee-themed aesthetics
- **Responsive Design** - Desktop-first approach with mobile compatibility
- **Interactive Elements** - Smooth animations and user feedback

## 🛠️ Technology Stack

### Backend
- **Database**: MariaDB (Enhanced MySQL compatibility)
- **Framework**: Flask (Python web framework)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login with password hashing

### Frontend
- **Markup**: HTML5 with semantic elements
- **Styling**: CSS3 with Flexbox and Grid
- **Scripting**: JavaScript (ES6+)
- **Design**: Custom glassmorphism theme

### Development Tools
- **IDE**: Visual Studio Code
- **Version Control**: Git
- **Database Tools**: MariaDB Workbench

## 📊 Database Schema

The system uses a normalized database design (3NF) with 11 core tables:

- **users** - Customer and admin authentication
- **user_profiles** - Extended user information
- **addresses** - Multiple addresses per user
- **categories** - Menu item categories
- **menu_items** - Product catalog with inventory
- **orders** - Order management and tracking
- **order_items** - Individual order line items
- **cart** - Shopping cart functionality
- **audit_log** - System activity tracking
- **inventory_log** - Stock movement tracking
- **order_status_history** - Order status changes

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- MariaDB 10.5+
- Git

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/Tejashwini2406/Afforgato.git
cd Afforgato
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup MariaDB database**
```bash
# Create database
mysql -u root -p
CREATE DATABASE afforgato_cafe;
exit

# Import schema
mysql -u root -p afforgato_cafe < database.sql
```

5. **Configure environment variables**
```bash
# Create .env file
cp .env.example .env
# Edit .env with your database credentials
```

6. **Run the application**
```bash
flask run
```

Visit `http://localhost:5000` to access the application.

## 📁 Project Structure

```
Afforgato/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── config.py              # Configuration settings
├── setup.py               # Setup script
├── requirements.txt       # Python dependencies
├── database.sql           # Database schema and sample data
├── PROJECT_ABSTRACT.txt   # Complete project documentation
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS, images)
└── README.md             # This file
```

## 🧪 Testing

The system has been thoroughly tested with:
- **Component Testing** - Individual module testing
- **Integration Testing** - Module interaction testing
- **System Testing** - End-to-end functionality testing
- **User Acceptance Testing** - Real-world scenario testing

## 📈 Business Impact

- **Operational Efficiency** - Streamlined order processing and inventory management
- **Customer Experience** - User-friendly interface and real-time order tracking
- **Data Integrity** - Normalized database design with comprehensive audit trails
- **Scalability** - Designed to handle growing business requirements
- **Analytics** - Business insights for informed decision making

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Tejashwini** - *Project Lead & Database Design*
- **Srujana** - *Frontend Development & UI/UX*

## 🙏 Acknowledgments

- Flask community for excellent documentation
- MariaDB team for robust database engine
- Coffee shop industry for inspiration
- BMSIT College for academic support

## 📞 Contact

For questions or support, please contact:
- 📧 Email: contact@afforgato.com
- 🌐 Website: [Coming Soon]
- 📍 Location: Bengaluru, Karnataka, India

---

*Made with ☕ and ❤️ in Bengaluru*

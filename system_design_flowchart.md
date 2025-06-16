# Afforgato Coffee Shop System Design Flowchart

```mermaid
flowchart TD
    A[Registration/Login] --> B[Admin Login]
    A --> C[Customer Login]
    
    B --> D{Login Success}
    C --> E{Login Success}
    
    D --> F[Admin Dashboard]
    E --> G[Customer Dashboard]
    
    F --> H[Add Menu Items]
    F --> I[Manage Orders]
    F --> J[View Analytics]
    F --> K[Manage Users]
    
    G --> L[Browse Menu]
    G --> M[Place Order]
    G --> N[Track Orders]
    G --> O[View Order History]
    
    H --> P[(Database Operations)]
    I --> P
    J --> P
    K --> P
    L --> P
    M --> P
    N --> P
    O --> P
    
    M --> Q[Add to Cart]
    Q --> R[Checkout Process]
    R --> S[Payment Processing]
    S --> T[Order Confirmation]
    
    I --> U[Update Order Status]
    I --> V[View All Orders]
    U --> W[Order Fulfillment]
    
    style A fill:#8B4513,stroke:#333,stroke-width:2px,color:#fff
    style F fill:#D2691E,stroke:#333,stroke-width:2px,color:#fff
    style G fill:#CD853F,stroke:#333,stroke-width:2px,color:#fff
    style P fill:#A0522D,stroke:#333,stroke-width:2px,color:#fff
```

## System Components

### Entry Point
- **Registration/Login**: Main entry point for all users

### User Authentication
- **Admin Login**: Administrative access with elevated privileges
- **Customer Login**: Standard customer access for ordering

### Admin Dashboard Features
- **Add Menu Items**: Create and manage coffee shop menu
- **Manage Orders**: View, update, and process customer orders
- **View Analytics**: Business intelligence and reporting
- **Manage Users**: User account administration

### Customer Dashboard Features
- **Browse Menu**: View available coffee items and prices
- **Place Order**: Add items to cart and checkout
- **Track Orders**: Monitor order status and delivery
- **View Order History**: Access past order records

### Core Processes
- **Order Workflow**: Cart → Checkout → Payment → Confirmation
- **Order Management**: Status updates and fulfillment tracking
- **Database Operations**: Centralized data management for all functions

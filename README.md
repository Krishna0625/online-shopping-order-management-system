# Project 5: Professional Online Shopping and Order Management System

A complete, beginner-friendly web application built with **Python**, **Flask**, **SQLite**, **HTML**, **CSS**, **Jinja2**, and **Vanilla JavaScript**. Designed for college practical examinations and viva demonstrations, matching the visual design identity of Project 3.

---

## 1. Key Features

### Customer Functionality
- **Customer Registration (`/register`)**:
  - Registers customer **Name**, **Email**, and **Password**.
  - Prevents duplicate email registration (`UNIQUE` constraint + friendly error handling).
  - Hashes passwords securely using Python's `werkzeug.security.generate_password_hash`.
- **Customer Login & Session Security (`/login`, `/logout`)**:
  - Authenticates customers via email and password hash verification.
  - Protects customer routes (`@customer_login_required`) from unauthorized access.
- **Product Catalogue (`/` and `/products`)**:
  - Displays products as responsive cards with **Name**, **Description**, **Price**, **Available Stock**, and **Add to Cart** controls.
  - Supports both server-side search by product name (`?q=`) and instant client-side search filtering.
- **Shopping Cart (`/cart`)**:
  - Add products, view cart items, increase or decrease quantities, and remove products.
  - Displays individual item subtotals and total cart amount.
  - Enforces stock limits so customers cannot select quantities greater than available stock.
- **Checkout & Order Confirmation (`/checkout`, `/order-confirmation/<id>`)**:
  - Displays itemized order summary, total payable amount, and a **Confirm Order** button.
  - Verifies live stock availability before saving the order in SQLite and automatically reduces product stock.
  - Displays a digital receipt on the Order Confirmation page.
- **Order History (`/orders`)**:
  - Displays **Order ID**, **Order Date**, **Total Amount**, **Ordered Products**, and **Quantities**.
  - Strictly scoped to the logged-in customer (`WHERE user_id = ?`) so customers can only view their own orders.

### Admin Functionality
- **Separate Admin Login (`/admin/login`)**:
  - Demonstration Credentials:
    - **Username:** `admin`
    - **Password:** `admin123`
  - Protected by `@admin_login_required` so customers or unauthenticated visitors cannot access admin pages.
- **Admin Dashboard (`/admin/dashboard`)**:
  - Displays live SQLite statistics: **Total Products**, **Total Customers**, **Total Orders**, and **Total Sales**.
  - Includes live digital clock, searchable product inventory table, recent customer orders, and quick actions.
- **Product Management (`/admin/add-product`, `/admin/edit-product/<id>`, `/admin/delete-product/<id>`)**:
  - Add, edit, and delete products with validation for prices (`> 0`) and stock quantities (`>= 0`).
- **Admin Order Management (`/admin/orders`)**:
  - Displays **Order ID**, **Customer Name & Email**, **Order Date**, **Ordered Products & Quantities**, **Amount**, and **Order Status** in a searchable table.

---

## 2. Project Folder Structure

```text
Project-5-Online-Shopping/
├── app.py                      # Main Flask backend application and SQLite database logic
├── requirements.txt            # Python package dependencies
├── README.md                   # Project documentation and run instructions
├── database.db                 # SQLite database (automatically created on startup)
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Shared layout (Navy-blue sidebar, top navbar, live clock)
│   ├── home.html               # Customer shopping homepage and catalogue
│   ├── register.html           # Split-screen customer registration page
│   ├── login.html              # Split-screen customer login page
│   ├── products.html           # Full product catalogue with search by name
│   ├── cart.html               # Shopping cart with quantity controls and subtotals
│   ├── checkout.html           # Order summary and Confirm Order page
│   ├── order_confirmation.html # Order confirmation receipt page
│   ├── order_history.html      # Customer personal order history page
│   ├── admin_login.html        # Split-screen administrator login page
│   ├── admin_dashboard.html    # Admin dashboard with real SQLite stats and product table
│   ├── add_product.html        # Admin form to add new products
│   ├── edit_product.html       # Admin form to edit existing products
│   └── admin_orders.html       # Admin customer orders management page
└── static/
    ├── style.css               # Professional Navy-Blue & White portal stylesheet
    └── script.js               # Vanilla JS for live clock, search filtering, password toggle, and alerts
```

---

## 3. How to Run the Application (Windows PowerShell)

Open Windows PowerShell inside the `Project-5-Online-Shopping` folder and run:

1. **Create environment:**
   ```powershell
   py -3.13 -m venv venv
   ```

2. **Activate:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run:**
   ```powershell
   python app.py
   ```

5. **Application URL:**
   ```text
   http://127.0.0.1:5000
   ```

---

## 4. Database Schema (SQLite)

The database (`database.db`) is automatically created when `app.py` starts, with four tables:

1. **`users`**:
   - `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`)
   - `name` (`TEXT NOT NULL`)
   - `email` (`TEXT UNIQUE NOT NULL`)
   - `password` (`TEXT NOT NULL` — hashed password)
2. **`products`**:
   - `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`)
   - `name` (`TEXT NOT NULL`)
   - `description` (`TEXT NOT NULL`)
   - `price` (`REAL NOT NULL`)
   - `stock` (`INTEGER NOT NULL`)
3. **`orders`**:
   - `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`)
   - `user_id` (`INTEGER NOT NULL`, Foreign Key -> `users(id)`)
   - `total_amount` (`REAL NOT NULL`)
   - `order_date` (`TEXT NOT NULL`)
   - `status` (`TEXT NOT NULL DEFAULT 'Confirmed'`)
4. **`order_items`**:
   - `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`)
   - `order_id` (`INTEGER NOT NULL`, Foreign Key -> `orders(id)`)
   - `product_id` (`INTEGER`, Foreign Key -> `products(id) ON DELETE SET NULL`)
   - `product_name` (`TEXT NOT NULL`)
   - `price` (`REAL NOT NULL`)
   - `quantity` (`INTEGER NOT NULL`)

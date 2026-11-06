from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from functools import wraps
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "online_shopping_secret_key"

DATABASE = "database.db"


# Helper function to connect to the SQLite database
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Create database tables automatically when the application starts
def init_db():
    conn = get_db()

    # 1. Users table (email is UNIQUE to prevent duplicate registrations)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # 2. Products table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    # 3. Orders table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Confirmed',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # 4. Order Items table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE SET NULL
        )
    """)

    # Insert sample products if the products table is empty
    existing_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if existing_count == 0:
        sample_products = [
            (
                "Wireless Noise-Cancelling Headphones",
                "Over-ear Bluetooth 5.3 headphones with 35-hour battery life and crystal-clear studio audio.",
                2499.00,
                15
            ),
            (
                "Mechanical Backlit Keyboard",
                "Compact 87-key tactile mechanical keyboard with aluminum top plate and customizable white LED backlight.",
                1899.00,
                20
            ),
            (
                "Ergonomic Wireless Mouse",
                "Precision optical sensor mouse with silent clicks, adjustable DPI, and comfortable contoured grip.",
                799.00,
                30
            ),
            (
                "USB-C 7-in-1 Multiport Hub",
                "High-speed aluminum adapter with 4K HDMI, 100W Power Delivery, USB 3.0 ports, and SD card reader.",
                1299.00,
                18
            ),
            (
                "1080p Full HD Webcam",
                "Widescreen Conference & Streaming webcam with dual noise-reducing microphones and privacy shutter.",
                1599.00,
                12
            ),
            (
                "Portable 1TB External SSD",
                "Shock-resistant pocket solid-state drive with ultra-fast 1050 MB/s read speeds via USB 3.2 Gen 2.",
                5499.00,
                10
            )
        ]
        conn.executemany(
            "INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)",
            sample_products
        )

    conn.commit()
    conn.close()


# Initialize database tables on startup
init_db()


# Helper to pop one-time notification messages from session
def pop_flash_messages():
    message = session.pop("flash_message", None)
    error = session.pop("flash_error", None)
    return message, error


# Inject cart item count into all templates automatically
@app.context_processor
def inject_globals():
    cart = session.get("cart", {})
    cart_count = sum(cart.values())
    return {
        "cart_count": cart_count
    }


# Decorator to protect customer routes
def customer_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            session["flash_error"] = "Please sign in to your customer account to continue."
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# Decorator to protect admin routes
def admin_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin" not in session:
            session["flash_error"] = "Admin authentication is required to access that page."
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


# ==============================================================================
# CUSTOMER ROUTES
# ==============================================================================

# 1. Customer Homepage
@app.route("/")
def home():
    conn = get_db()
    search_query = request.args.get("q", "").strip()

    if search_query:
        products_list = conn.execute(
            "SELECT * FROM products WHERE name LIKE ? OR description LIKE ? ORDER BY id ASC",
            (f"%{search_query}%", f"%{search_query}%")
        ).fetchall()
    else:
        products_list = conn.execute("SELECT * FROM products ORDER BY id ASC").fetchall()

    conn.close()
    message, error = pop_flash_messages()

    return render_template(
        "home.html",
        products=products_list,
        search_query=search_query,
        message=message,
        error=error
    )


# 2. Product Catalogue Page (with search by product name)
@app.route("/products")
def products():
    conn = get_db()
    search_query = request.args.get("q", "").strip()

    if search_query:
        products_list = conn.execute(
            "SELECT * FROM products WHERE name LIKE ? OR description LIKE ? ORDER BY id ASC",
            (f"%{search_query}%", f"%{search_query}%")
        ).fetchall()
    else:
        products_list = conn.execute("SELECT * FROM products ORDER BY id ASC").fetchall()

    conn.close()
    message, error = pop_flash_messages()

    return render_template(
        "products.html",
        products=products_list,
        search_query=search_query,
        message=message,
        error=error
    )


# 3. Customer Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    message, error = pop_flash_messages()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not name or not email or not password:
            error = "All fields (Full Name, Email Address, and Password) are required."
        elif "@" not in email or "." not in email:
            error = "Please enter a valid email address."
        elif len(password) < 4:
            error = "Password must be at least 4 characters long."
        else:
            conn = get_db()
            try:
                hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
                conn.execute(
                    "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                    (name, email, hashed_password)
                )
                conn.commit()
                conn.close()

                session["flash_message"] = "Registration successful! Please sign in with your email and password."
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                conn.close()
                error = f"An account with email '{email}' already exists. Please use a different email or sign in."

    return render_template("register.html", message=message, error=error)


# 4. Customer Login
@app.route("/login", methods=["GET", "POST"])
def login():
    message, error = pop_flash_messages()

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            error = "Please enter both your email address and password."
        else:
            conn = get_db()
            user = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()
            conn.close()

            if user and check_password_hash(user["password"], password):
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                session["user_email"] = user["email"]
                if "cart" not in session:
                    session["cart"] = {}
                session["flash_message"] = f"Welcome back, {user['name']}!"
                return redirect(url_for("home"))
            else:
                error = "Invalid email or password. Please try again."

    return render_template("login.html", message=message, error=error)


# 5. Customer Logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("user_email", None)
    session.pop("cart", None)
    session["flash_message"] = "You have been logged out successfully."
    return redirect(url_for("login"))


# 6. Add Product to Shopping Cart
@app.route("/cart/add/<int:product_id>", methods=["POST"])
@customer_login_required
def add_to_cart(product_id):
    conn = get_db()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()
    conn.close()

    if not product:
        session["flash_error"] = "Selected product was not found."
        return redirect(url_for("products"))

    if product["stock"] <= 0:
        session["flash_error"] = f"Sorry, '{product['name']}' is currently out of stock."
        return redirect(request.referrer or url_for("products"))

    try:
        requested_qty = int(request.form.get("quantity", 1))
    except ValueError:
        requested_qty = 1

    if requested_qty < 1:
        requested_qty = 1

    cart = session.get("cart", {})
    pid_key = str(product_id)
    current_qty = cart.get(pid_key, 0)
    new_qty = current_qty + requested_qty

    # Do not allow quantities greater than available stock
    if new_qty > product["stock"]:
        cart[pid_key] = product["stock"]
        session["cart"] = cart
        session["flash_error"] = (
            f"Cannot add more than available stock ({product['stock']} units) for '{product['name']}'."
        )
    else:
        cart[pid_key] = new_qty
        session["cart"] = cart
        session["flash_message"] = f"Added '{product['name']}' to your shopping cart!"

    return redirect(request.referrer or url_for("cart"))


# Helper function to build detailed cart items list and total amount
def get_cart_details(conn):
    cart = session.get("cart", {})
    cart_items = []
    total_amount = 0.0
    updated_cart = {}

    for pid_str, qty in cart.items():
        product = conn.execute(
            "SELECT * FROM products WHERE id = ?",
            (int(pid_str),)
        ).fetchone()
        if product and qty > 0:
            subtotal = round(product["price"] * qty, 2)
            total_amount = round(total_amount + subtotal, 2)
            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "price": product["price"],
                "stock": product["stock"],
                "quantity": qty,
                "subtotal": subtotal
            })
            updated_cart[pid_str] = qty

    session["cart"] = updated_cart
    return cart_items, total_amount


# 7. View Shopping Cart
@app.route("/cart")
@customer_login_required
def cart():
    conn = get_db()
    cart_items, total_amount = get_cart_details(conn)
    conn.close()

    message, error = pop_flash_messages()
    return render_template(
        "cart.html",
        cart_items=cart_items,
        total_amount=total_amount,
        message=message,
        error=error
    )


# 8. Update Cart Item Quantity (Increase, Decrease, or Direct Input)
@app.route("/cart/update/<int:product_id>", methods=["POST"])
@customer_login_required
def update_cart(product_id):
    conn = get_db()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()
    conn.close()

    cart = session.get("cart", {})
    pid_key = str(product_id)

    if not product or pid_key not in cart:
        session["flash_error"] = "Item not found in your cart."
        return redirect(url_for("cart"))

    action = request.form.get("action", "")
    current_qty = cart.get(pid_key, 1)

    if action == "increase":
        new_qty = current_qty + 1
    elif action == "decrease":
        new_qty = current_qty - 1
    else:
        try:
            new_qty = int(request.form.get("quantity", current_qty))
        except ValueError:
            new_qty = current_qty

    if new_qty <= 0:
        cart.pop(pid_key, None)
        session["cart"] = cart
        session["flash_message"] = f"Removed '{product['name']}' from your cart."
    elif new_qty > product["stock"]:
        cart[pid_key] = product["stock"]
        session["cart"] = cart
        session["flash_error"] = (
            f"Only {product['stock']} units of '{product['name']}' are available in stock."
        )
    else:
        cart[pid_key] = new_qty
        session["cart"] = cart
        session["flash_message"] = f"Updated quantity for '{product['name']}' to {new_qty}."

    return redirect(url_for("cart"))


# 9. Remove Product from Shopping Cart
@app.route("/cart/remove/<int:product_id>", methods=["POST", "GET"])
@customer_login_required
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    pid_key = str(product_id)

    if pid_key in cart:
        cart.pop(pid_key, None)
        session["cart"] = cart
        session["flash_message"] = "Product removed from your shopping cart."

    return redirect(url_for("cart"))


# 10. Checkout & Place Order
@app.route("/checkout", methods=["GET", "POST"])
@customer_login_required
def checkout():
    conn = get_db()
    cart_items, total_amount = get_cart_details(conn)
    message, error = pop_flash_messages()

    if not cart_items:
        conn.close()
        session["flash_error"] = "Your shopping cart is empty. Please add products before checking out."
        return redirect(url_for("products"))

    if request.method == "POST":
        # Validate stock consistency for all cart items before creating the order
        insufficient_items = []
        for item in cart_items:
            live_product = conn.execute(
                "SELECT stock, name FROM products WHERE id = ?",
                (item["id"],)
            ).fetchone()
            if not live_product or item["quantity"] > live_product["stock"]:
                available = live_product["stock"] if live_product else 0
                insufficient_items.append(
                    f"'{item['name']}' (Requested: {item['quantity']}, Available: {available})"
                )

        if insufficient_items:
            conn.close()
            error = "Insufficient stock for: " + ", ".join(insufficient_items) + ". Please adjust your cart."
            return render_template(
                "checkout.html",
                cart_items=cart_items,
                total_amount=total_amount,
                message=message,
                error=error
            )

        # Create the order and reduce stock consistently inside one transaction
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO orders (user_id, total_amount, order_date, status) VALUES (?, ?, ?, ?)",
            (session["user_id"], total_amount, order_date, "Confirmed")
        )
        order_id = cursor.lastrowid

        for item in cart_items:
            cursor.execute(
                """
                INSERT INTO order_items (order_id, product_id, product_name, price, quantity)
                VALUES (?, ?, ?, ?, ?)
                """,
                (order_id, item["id"], item["name"], item["price"], item["quantity"])
            )
            cursor.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (item["quantity"], item["id"])
            )

        conn.commit()
        conn.close()

        # Clear shopping cart after successful order placement
        session["cart"] = {}
        return redirect(url_for("order_confirmation", order_id=order_id))

    conn.close()
    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total_amount=total_amount,
        message=message,
        error=error
    )


# 11. Order Confirmation Page
@app.route("/order-confirmation/<int:order_id>")
@customer_login_required
def order_confirmation(order_id):
    conn = get_db()

    # Ensure customer can only view their own order
    order = conn.execute(
        "SELECT * FROM orders WHERE id = ? AND user_id = ?",
        (order_id, session["user_id"])
    ).fetchone()

    if not order:
        conn.close()
        session["flash_error"] = "Order not found or access denied."
        return redirect(url_for("order_history"))

    items = conn.execute(
        "SELECT * FROM order_items WHERE order_id = ?",
        (order_id,)
    ).fetchall()
    conn.close()

    return render_template("order_confirmation.html", order=order, items=items)


# 12. Customer Order History (Only logged-in customer's own orders)
@app.route("/orders")
@customer_login_required
def order_history():
    conn = get_db()
    user_orders = conn.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC",
        (session["user_id"],)
    ).fetchall()

    orders_data = []
    for order in user_orders:
        items = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ?",
            (order["id"],)
        ).fetchall()
        orders_data.append({
            "id": order["id"],
            "order_date": order["order_date"],
            "total_amount": order["total_amount"],
            "status": order["status"],
            "items": items
        })

    conn.close()
    message, error = pop_flash_messages()

    return render_template(
        "order_history.html",
        orders=orders_data,
        message=message,
        error=error
    )


# ==============================================================================
# ADMIN ROUTES
# ==============================================================================

# 13. Admin Login
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    message, error = pop_flash_messages()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Check demonstration admin credentials
        if username == "admin" and password == "admin123":
            session["admin"] = username
            session["flash_message"] = "Welcome to the Store Administration Portal!"
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid admin username or password. Please try again."

    return render_template("admin_login.html", message=message, error=error)


# 14. Admin Logout
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    session["flash_message"] = "Admin logged out successfully."
    return redirect(url_for("admin_login"))


# 15. Admin Dashboard (Statistics, Recent Orders, and Product Inventory)
@app.route("/admin/dashboard")
@admin_login_required
def admin_dashboard():
    conn = get_db()

    # Real database statistics
    total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    total_customers = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    total_sales = conn.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders").fetchone()[0]

    # All products for product management table
    products_list = conn.execute("SELECT * FROM products ORDER BY id ASC").fetchall()

    # Recent customer orders (latest 5)
    recent_orders = conn.execute("""
        SELECT o.id, o.total_amount, o.order_date, o.status, u.name AS customer_name, u.email AS customer_email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.id DESC
        LIMIT 5
    """).fetchall()

    conn.close()
    message, error = pop_flash_messages()

    return render_template(
        "admin_dashboard.html",
        total_products=total_products,
        total_customers=total_customers,
        total_orders=total_orders,
        total_sales=round(total_sales, 2),
        products=products_list,
        recent_orders=recent_orders,
        message=message,
        error=error
    )


# 16. Admin Add Product
@app.route("/admin/add-product", methods=["GET", "POST"])
@admin_login_required
def add_product():
    conn = get_db()
    message, error = pop_flash_messages()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price_input = request.form.get("price", "").strip()
        stock_input = request.form.get("stock", "").strip()

        if not name or not description or price_input == "" or stock_input == "":
            error = "All product fields (Name, Description, Price, and Stock) are required."
        else:
            try:
                price = round(float(price_input), 2)
                stock = int(stock_input)

                if price <= 0:
                    error = "Product price must be greater than 0."
                elif stock < 0:
                    error = "Stock quantity cannot be negative."
                else:
                    conn.execute(
                        "INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)",
                        (name, description, price, stock)
                    )
                    conn.commit()
                    conn.close()
                    session["flash_message"] = f"Product '{name}' added successfully!"
                    return redirect(url_for("admin_dashboard"))
            except ValueError:
                error = "Please enter a valid number for Price and a whole number for Stock Quantity."

    products_list = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    conn.close()

    return render_template(
        "add_product.html",
        products=products_list,
        message=message,
        error=error
    )


# 17. Admin Edit Product
@app.route("/admin/edit-product/<int:product_id>", methods=["GET", "POST"])
@admin_login_required
def edit_product(product_id):
    conn = get_db()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        conn.close()
        session["flash_error"] = "Product not found."
        return redirect(url_for("admin_dashboard"))

    message, error = pop_flash_messages()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price_input = request.form.get("price", "").strip()
        stock_input = request.form.get("stock", "").strip()

        if not name or not description or price_input == "" or stock_input == "":
            error = "All product fields (Name, Description, Price, and Stock) are required."
        else:
            try:
                price = round(float(price_input), 2)
                stock = int(stock_input)

                if price <= 0:
                    error = "Product price must be greater than 0."
                elif stock < 0:
                    error = "Stock quantity cannot be negative."
                else:
                    conn.execute(
                        "UPDATE products SET name = ?, description = ?, price = ?, stock = ? WHERE id = ?",
                        (name, description, price, stock, product_id)
                    )
                    conn.commit()
                    conn.close()
                    session["flash_message"] = f"Product '{name}' updated successfully!"
                    return redirect(url_for("admin_dashboard"))
            except ValueError:
                error = "Please enter a valid number for Price and a whole number for Stock Quantity."

    conn.close()
    return render_template(
        "edit_product.html",
        product=product,
        message=message,
        error=error
    )


# 18. Admin Delete Product
@app.route("/admin/delete-product/<int:product_id>", methods=["POST"])
@admin_login_required
def delete_product(product_id):
    conn = get_db()
    product = conn.execute(
        "SELECT name FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if product:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        session["flash_message"] = f"Product '{product['name']}' deleted successfully."
    else:
        session["flash_error"] = "Product not found."

    conn.close()
    return redirect(url_for("admin_dashboard"))


# 19. Admin View All Customer Orders
@app.route("/admin/orders")
@admin_login_required
def admin_orders():
    conn = get_db()
    orders_rows = conn.execute("""
        SELECT o.id, o.total_amount, o.order_date, o.status, u.name AS customer_name, u.email AS customer_email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.id DESC
    """).fetchall()

    orders_list = []
    for row in orders_rows:
        items = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ?",
            (row["id"],)
        ).fetchall()
        orders_list.append({
            "id": row["id"],
            "customer_name": row["customer_name"],
            "customer_email": row["customer_email"],
            "order_date": row["order_date"],
            "total_amount": row["total_amount"],
            "status": row["status"],
            "items": items
        })

    conn.close()
    message, error = pop_flash_messages()

    return render_template(
        "admin_orders.html",
        orders=orders_list,
        message=message,
        error=error
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

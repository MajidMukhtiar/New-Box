from datetime import datetime
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Connect to MongoDB
# client = MongoClient("mongodb://localhost:27017/")

MONGO_URI = "mongodb+srv://<username>:<password>@clustername.mongodb.net/?retryWrites=true&w=majority"

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)

db = client["ecommerce_db"]

# 📌 Ensure database and collections are created
def initialize_db():
    cars = db["cars"]
    cart = db["cart"]
    orders = db["orders"]
    order_items = db["order_items"]

# 📌 Get Database Collection
def get_collection(collection_name):
    return db[collection_name]

# 🏠 Home Page
@app.route("/")
def home():
    return render_template("redo.html")

# 🚗 Get all cars
@app.route("/get_cars", methods=["GET"])
def get_cars():
    try:
        cars_collection = get_collection("cars")
        cars = list(cars_collection.find())
        
        car_list = [
            {
                "id": str(car["_id"]),
                "name": car["name"],
                "price": car["price"],
                "image_url": car["image_url"],
                "description": car["description"]
            }
            for car in cars
        ]
        
        return jsonify({"cars": car_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add a single car
@app.route("/admin", methods=["GET"])
def admin_panel():
    return render_template("admin.html")

@app.route("/admin/add_car", methods=["POST"])
def add_car():
    try:
        data = request.get_json()  # Get JSON data
        
        # Validate input
        required_fields = ["name", "price", "image_url", "description"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        cars_collection = get_collection("cars")

        # Insert a single car
        car_id = cars_collection.insert_one({
            "name": data["name"], 
            "price": data["price"], 
            "image_url": data["image_url"], 
            "description": data["description"]
        }).inserted_id
        
        return jsonify({"message": "Car added successfully!", "car_id": str(car_id)}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete a car
@app.route("/admin/delete_car", methods=["POST"])
def delete_car():
    try:
        data = request.get_json()  # Get JSON data

        car_id = data.get("id")
        car_name = data.get("name")

        if not car_id and not car_name:
            return jsonify({"error": "Either ID or Name is required!"}), 400

        cars_collection = get_collection("cars")

        if car_id:
            result = cars_collection.delete_one({"_id": ObjectId(car_id)})
        elif car_name:
            result = cars_collection.delete_one({"name": car_name})

        if result.deleted_count == 0:
            return jsonify({"error": "Car not found!"}), 404

        return jsonify({"message": "Car deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Update a car
@app.route("/admin/update_car", methods=["POST"])
def update_car():
    try:
        data = request.get_json()  # Get JSON data

        car_id = data.get("id")
        car_name = data.get("name")

        if not car_id and not car_name:
            return jsonify({"error": "Car ID or Name is required!"}), 400

        update_fields = {}
        if "new_name" in data and data["new_name"]:
            update_fields["name"] = data["new_name"]
        if "price" in data and data["price"]:
            update_fields["price"] = data["price"]
        if "image_url" in data and data["image_url"]:
            update_fields["image_url"] = data["image_url"]
        if "description" in data and data["description"]:
            update_fields["description"] = data["description"]

        if not update_fields:
            return jsonify({"error": "No update fields provided!"}), 400

        cars_collection = get_collection("cars")

        if car_id:
            result = cars_collection.update_one({"_id": ObjectId(car_id)}, {"$set": update_fields})
        else:
            result = cars_collection.update_one({"name": car_name}, {"$set": update_fields})

        if result.matched_count == 0:
            return jsonify({"error": "Car not found!"}), 404

        return jsonify({"message": "Car updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add multiple cars (Optional)
@app.route("/add_cars", methods=["POST"])
def add_cars():
    try:
        data = request.get_json()

        if not isinstance(data, list) or not data:
            return jsonify({"error": "Invalid data format. Expected a list of cars."}), 400
        
        cars_collection = get_collection("cars")

        # Insert multiple cars
        cars_collection.insert_many(
            [{
                "name": car["name"], 
                "price": car["price"], 
                "image_url": car["image_url"], 
                "description": car.get("description", "")
            } for car in data]
        )
        
        return jsonify({"message": "Cars added successfully!"}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🛒 Get Cart Items
@app.route("/cart", methods=["GET"])
def view_cart():
    try:
        cart_collection = get_collection("cart")
        cars_collection = get_collection("cars")

        cart_items = list(cart_collection.aggregate([
            {
                "$lookup": {
                    "from": "cars",
                    "localField": "car_id",
                    "foreignField": "_id",
                    "as": "car_details"
                }
            },
            {"$unwind": "$car_details"}
        ]))

        total_price = sum(item["car_details"]["price"] * item["quantity"] for item in cart_items)

        cart_list = [
            {
                "id": str(item["_id"]),
                "name": item["car_details"]["name"],
                "price": item["car_details"]["price"],
                "image_url": item["car_details"]["image_url"],
                "quantity": item["quantity"]
            }
            for item in cart_items
        ]

        return render_template("cart.html", cart_items=cart_list, total_price=total_price)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    try:
        data = request.get_json()
        car_id = data.get("car_id")

        if not car_id:
            return jsonify({"error": "Car ID is required"}), 400

        cart_collection = get_collection("cart")
        cars_collection = get_collection("cars")

        # Convert string ID to ObjectId
        car_obj = cars_collection.find_one({"_id": ObjectId(car_id)})

        if not car_obj:
            return jsonify({"error": "Car not found"}), 404

        # Check if car is already in cart, increase quantity
        existing_item = cart_collection.find_one({"car_id": ObjectId(car_id)})
        if existing_item:
            cart_collection.update_one({"car_id": ObjectId(car_id)}, {"$inc": {"quantity": 1}})
        else:
            cart_collection.insert_one({"car_id": ObjectId(car_id), "quantity": 1})

        return jsonify({"message": "Car added to cart!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
@app.route("/place_order", methods=["GET"])
def place_order():
    try:
        cart_collection = get_collection("cart")

        # Fetch cart items and join with cars collection
        cart_items = list(cart_collection.aggregate([
            {
                "$lookup": {
                    "from": "cars",
                    "localField": "car_id",
                    "foreignField": "_id",
                    "as": "car_details"
                }
            },
            {"$unwind": "$car_details"}
        ]))

        # Ensure quantity exists in cart items
        for item in cart_items:
            if "quantity" not in item:
                item["quantity"] = 1  # Default to 1 if not set

        total_price = sum(item["car_details"]["price"] * item["quantity"] for item in cart_items)

        return render_template("place_order_receipt.html", cart_items=cart_items, total_price=total_price)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

from bson import ObjectId
from datetime import datetime

@app.route("/submit_order", methods=["POST"])
def submit_order():
    try:
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        address = data.get("address")

        if not name or not email or not address:
            return jsonify({"error": "All fields are required"}), 400

        cart_collection = get_collection("cart")
        orders_collection = get_collection("orders")
        order_items_collection = get_collection("order_items")

        # Fetch cart items
        cart_items = list(cart_collection.aggregate([
            {
                "$lookup": {
                    "from": "cars",
                    "localField": "car_id",
                    "foreignField": "_id",
                    "as": "car_details"
                }
            },
            {"$unwind": "$car_details"}
        ]))

        if not cart_items:
            return jsonify({"error": "Cart is empty"}), 400

        # Calculate total price
        total_price = sum(item["car_details"]["price"] * item["quantity"] for item in cart_items)

        # Insert order into orders collection
        order_data = {
            "name": name,
            "email": email,
            "address": address,
            "total_price": total_price,
            "status": "Pending",
            "order_date": datetime.utcnow()
        }

        order_id = orders_collection.insert_one(order_data).inserted_id
        order_id_str = str(order_id)  # Convert ObjectId to string

        # Insert each cart item into order_items collection
        for item in cart_items:
            order_item = {
                "order_id": order_id_str,  # Convert ObjectId to string
                "car_id": str(item["car_details"]["_id"]),  # Convert ObjectId to string
                "car_name": item["car_details"]["name"],
                "price": item["car_details"]["price"],
                "quantity": item["quantity"],
                "subtotal": item["car_details"]["price"] * item["quantity"]
            }
            order_items_collection.insert_one(order_item)

        # Generate receipt data before clearing cart
        receipt_data = {
            "name": name,
            "email": email,
            "address": address,
            "cart_items": [
                {
                    "car_name": item["car_details"]["name"],
                    "price": item["car_details"]["price"],
                    "quantity": item["quantity"],
                    "subtotal": item["car_details"]["price"] * item["quantity"]
                }
                for item in cart_items
            ],
            "total_price": total_price
        }

        # Clear cart after successful order
        cart_collection.delete_many({})

        return jsonify({
            "message": "Order placed successfully!",
            "order_id": order_id_str,
            "receipt": receipt_data  # Returning receipt data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/orders')
def orders_page():
    return render_template('orders.html') 

@app.route('/get_orders')
def get_orders():
    try:
        # Fetch all orders from the orders collection
        orders_collection = get_collection('orders')
        orders = list(orders_collection.find())
        
        # Convert ObjectId to string
        for order in orders:
            order['_id'] = str(order['_id'])  # Convert ObjectId to string

        return jsonify({'orders': orders}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/total_sales')
def total_sales():
    try:
        orders_collection = get_collection('orders')
        total_sales = sum(order['total_price'] for order in orders_collection.find())
        return jsonify({'total_sales': total_sales}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/total_orders')
def total_orders():
    try:
        orders_collection = get_collection('orders')
        total_orders = orders_collection.count_documents({})
        return jsonify({'total_orders': total_orders}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/top_orders')
def top_orders():
    try:
        orders_collection = get_collection('orders')
        top_orders = list(orders_collection.find().sort('total_price', -1).limit(10))  # Sort by highest total price

        # Convert ObjectId to string
        for order in top_orders:
            order['_id'] = str(order['_id'])

        return jsonify({'top_orders': top_orders}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == "__main__":
    initialize_db()
    app.run(debug=True, port=5000)

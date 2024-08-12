import threading
import time
import logging
from functools import wraps
import os

# Setting up logging
logging.basicConfig(filename='order_processing.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Decorator for timing functions
def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

# Product class
class Product:
    def __init__(self, name: str, price: float, stock: int):
        self.name = name
        self.price = price
        self.stock = stock

    def reduce_stock(self, quantity: int):
        if quantity > self.stock:
            raise ValueError(f"Not enough stock for product {self.name}")
        self.stock -= quantity

# Customer class
class Customer:
    def __init__(self, customer_id: int, name: str):
        self.customer_id = customer_id
        self.name = name

# Order class
class Order:
    order_id_counter = 1

    def __init__(self, customer: Customer, product: Product, quantity: int):
        self.order_id = Order.order_id_counter
        Order.order_id_counter += 1
        self.customer = customer
        self.product = product
        self.quantity = quantity
        self.status = "Pending"

    @timed
    def process_order(self):
        try:
            self.product.reduce_stock(self.quantity)
            self.status = "Completed"
            logging.info(f"Order {self.order_id} processed for {self.customer.name}: {self.quantity} x {self.product.name}")
        except ValueError as e:
            self.status = "Failed"
            logging.error(f"Order {self.order_id} failed: {e}")

    def __str__(self):
        return f"Order {self.order_id} for {self.customer.name}: {self.quantity} x {self.product.name} - Status: {self.status}"

# Function to simulate processing multiple orders
def process_orders(orders):
    threads = []
    for order in orders:
        thread = threading.Thread(target=order.process_order)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

# Example usage
if __name__ == "__main__":
    # Create some products
    product1 = Product(name="Laptop", price=999.99, stock=5)
    product2 = Product(name="Smartphone", price=499.99, stock=10)

    # Create customers
    customer1 = Customer(customer_id=1, name="Alice")
    customer2 = Customer(customer_id=2, name="Bob")

    # Create orders
    orders = [
        Order(customer=customer1, product=product1, quantity=1),
        Order(customer=customer2, product=product2, quantity=2),
        Order(customer=customer1, product=product2, quantity=10),  # This will fail due to insufficient stock
    ]

    # Process the orders
    process_orders(orders)

    # Print the results
    for order in orders:
        print(order)

    # Check the log file
    if os.path.exists('order_processing.log'):
        with open('order_processing.log', 'r') as log_file:
            print("\nLog file content:")
            print(log_file.read())

import csv
import os
from typing import Optional, Dict


class OrderManager:
    """Manages order lookups, customer data, and refund processing."""
    
    def __init__(self, data_path: str = "data/"):
        self.data_path = data_path
        self.orders = self._load_csv("orders.csv")
        self.customers = self._load_csv("customers.csv")
        self.products = self._load_csv("products.csv")
        self.transactions = self._load_csv("transactions.csv")
        
        print(f"Loaded {len(self.orders)} orders, {len(self.customers)} customers, "
              f"{len(self.products)} products, {len(self.transactions)} transactions")

    def _load_csv(self, filename: str) -> list:
        """Load CSV file and return list of dictionaries."""
        try:
            filepath = os.path.join(self.data_path, filename)
            with open(filepath, 'r', newline='', encoding='utf-8') as file:
                return list(csv.DictReader(file))
        except FileNotFoundError:
            print(f"⚠ Warning: {filename} not found in {self.data_path}")
            return []

    def _find_by_id(self, data: list, id_field: str, search_id: str):
        """Find a record by ID in the data list."""
        for record in data:
            if record.get(id_field) == search_id:
                return record
        return None

    def get_order_details(self, order_id: str) -> Optional[Dict]:
        """Retrieve complete order details including customer and product info."""
        order = self._find_by_id(self.orders, 'id', order_id)
        if not order:
            return None
        
        transaction = self._find_by_id(self.transactions, 'order_id', order_id)
        customer = self._find_by_id(
            self.customers, 'id', transaction.get('customer_id', '')
        ) if transaction else None
        product = self._find_by_id(
            self.products, 'id', transaction.get('product_id', '')
        ) if transaction else None
        
        return {
            "order": order,
            "transaction": transaction,
            "customer": customer,
            "product": product
        }

    def format_order_response(self, order_id: str) -> str:
        """Format order details into a readable string."""
        details = self.get_order_details(order_id)
        if not details:
            return f"I couldn't find order #{order_id}. Please check your order ID."
        
        order = details['order']
        transaction = details['transaction']
        customer = details['customer']
        product = details['product']
        
        return f"""
╔══════════════════════════════════════════════════════╗
║           ORDER DETAILS - #{order_id}
╚══════════════════════════════════════════════════════╝

Date: {order['date']} at {order['time']}
Code: {order['code']}
Status: {transaction['status']}

Customer: {customer['name'] if customer else 'N/A'}
Product: {product['name'] if product else 'N/A'}
Quantity: {order['quantity']}

Total: ${transaction['amount']}
Payment: {transaction['payment_method']}
"""

    def process_refund(self, order_id: str) -> str:
        """Process a refund request for an order."""
        details = self.get_order_details(order_id)
        if not details:
            return f"I couldn't find order #{order_id}. Please check your order ID."
        
        transaction = details['transaction']
        
        # Check if order is already cancelled
        if transaction['status'].lower() == 'cancelled':
            return f"⚠ This order (#{order_id}) was already cancelled. No refund needed."
        
        # Calculate refund (80% of original amount, 20% processing fee)
        original_amount = float(transaction['amount'])
        refund_amount = original_amount * 0.8
        processing_fee = original_amount * 0.2
        
        return f"""
╔══════════════════════════════════════════════════════╗
║           REFUND PROCESSED - #{order_id}
╚══════════════════════════════════════════════════════╝

Refund request approved

Original Amount: ${original_amount:.2f}
Processing Fee (20%): ${processing_fee:.2f}
Refund Amount: ${refund_amount:.2f}

The refund will be credited to your original payment method 
within 5-7 business days.
"""

    def validate_order_exists(self, order_id: str) -> bool:
        """Check if an order ID exists in the system."""
        return self._find_by_id(self.orders, 'id', order_id) is not None
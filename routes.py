from flask import Blueprint, request, jsonify
from services import add_customer, delete_customer, delete_all_customers
from decorators import log_action

routes = Blueprint('routes', __name__)

def resp(data, code=200):
    return jsonify(data), code

@routes.route('/customer', methods=['POST'])
@log_action("Adding new customer via API")
def api_add_customer():
    d = request.json or {}
    try:
        new_cust = add_customer(
            d.get('name', ''),
            d.get('phone', ''),
            d.get('email', ''),
            d.get('address', ''),
            d.get('due', 0.0)
        )
        return resp(new_cust, 201)
    except Exception as e:
        return resp({"error": f"Failed to add customer: {e}"}, 500)

@routes.route('/customer/<int:customer_id>', methods=['DELETE'])
@log_action("Deleting customer via API")
def api_delete_customer(customer_id):
    try:
        if delete_customer(customer_id):
            return resp({"message": "Customer deleted successfully."})
        else:
            return resp({"error": "Customer not found."}, 404)
    except Exception as e:
        return resp({"error": f"Failed to delete customer: {e}"}, 500)

@routes.route('/customers', methods=['DELETE'])
@log_action("Deleting all customers via API")
def api_delete_all_customers():
    try:
        if delete_all_customers():
            return resp({"message": "All customers deleted successfully."})
        else:
            return resp({"error": "No customers to delete."}, 404)
    except Exception as e:
        return resp({"error": f"Failed to delete all customers: {e}"}, 500)

@routes.route('/customers', methods=['GET'])
@log_action("Fetching all customers via API")
def api_get_customers():
    try:
        customers = get_all_customers()
        return resp(customers)
    except Exception as e:
        return resp({"error": f"Failed to fetch customers: {e}"}, 500)

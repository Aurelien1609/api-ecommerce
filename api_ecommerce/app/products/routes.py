from flask import Blueprint, jsonify
from sqlalchemy import select

products_print = Blueprint('products', __name__)

@products_print.route('/products', methods=['GET'])
def get_products():
        return jsonify("Test")

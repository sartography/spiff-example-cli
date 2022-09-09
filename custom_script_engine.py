# Standard Library
from collections import namedtuple

# Dependencies
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine

ProductInfo = namedtuple("ProductInfo", ["color", "size", "style", "price"])

INVENTORY = {
    "product_a": ProductInfo(False, False, False, 15.00),
    "product_b": ProductInfo(False, False, False, 15.00),
    "product_c": ProductInfo(True, False, False, 25.00),
    "product_d": ProductInfo(True, True, False, 20.00),
    "product_e": ProductInfo(True, True, True, 25.00),
    "product_f": ProductInfo(True, True, True, 30.00),
    "product_g": ProductInfo(False, False, True, 25.00),
}


def lookup_product_info(product_name):
    """
    Look in the inventory for the product information.

    :param product_name: name of the product.
    :type product_name: str
    :return: Information on the product.
    :rtype: ProductInfo
    """
    return INVENTORY[product_name]


def lookup_shipping_cost(shipping_method):
    """
    Return the shipping cost based on the selected choice.

    :param shipping_method: Method of shipping selected.
    :type shipping_method: str
    :return: Cost of the shipping.
    :rtype: float
    """
    return 25.00 if shipping_method == "Overnight" else 5.00


additions = {
    "lookup_product_info": lookup_product_info,
    "lookup_shipping_cost": lookup_shipping_cost,
}

CustomScriptEngine = PythonScriptEngine(scriptingAdditions=additions)

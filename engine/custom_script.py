import json
from collections import namedtuple

from SpiffWorkflow.bpmn.serializer.workflow import BpmnDataConverter

ProductInfo = namedtuple('ProductInfo', ['color', 'size', 'style', 'price'])

INVENTORY = {
    'product_a': ProductInfo(False, False, False, 15.00),
    'product_b': ProductInfo(False, False, False, 15.00),
    'product_c': ProductInfo(True, False, False, 25.00),
    'product_d': ProductInfo(True, True, False, 20.00),
    'product_e': ProductInfo(True, True, True, 25.00),
    'product_f': ProductInfo(True, True, True, 30.00),
    'product_g': ProductInfo(False, False, True, 25.00),
}

def lookup_product_info(product_name):
    return INVENTORY[product_name]

def lookup_shipping_cost(shipping_method):
    return 25.00 if shipping_method == 'Overnight' else 5.00

def get_globals(context, external_methods):
    _context = {
        'lookup_product_info': lookup_product_info,
        'lookup_shipping_cost': lookup_shipping_cost,
    }
    _context.update(context)
    _context.update(external_methods)
    return _context

def product_info_to_dict(obj):
    return {
        'color': obj.color,
        'size': obj.size,
        'style': obj.style,
        'price': obj.price,
    }

def product_info_from_dict(dct):
    return ProductInfo(**dct)

custom_data_converter = BpmnDataConverter()
custom_data_converter.register(ProductInfo, product_info_to_dict, product_info_from_dict)

def dumps(obj):
    dct = custom_data_converter.convert(obj)
    return json.dumps(dct)

def loads(s):
    dct = json.loads(s)
    return custom_data_converter.restore(dct)


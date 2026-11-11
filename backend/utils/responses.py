"""Every API answer has the same shape, so the frontend code stays simple."""
from flask import jsonify


def success(data=None, status=200):
    return jsonify(success=True, data=data), status


def error(code, status=400, **extra):
    # 'code' is a short message code such as PIN_INCORRECT.
    # The frontend turns it into English or Hindi text.
    return jsonify(success=False, code=code, **extra), status
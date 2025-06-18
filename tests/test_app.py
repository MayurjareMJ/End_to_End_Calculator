import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app

def test_add():
    assert app.add(2, 3) == 5

def test_subtract():
    assert app.subtract(5, 3) == 2

def test_multiply():
    assert app.multiply(4, 5) == 20

def test_divide():
    assert app.divide(10, 2) == 5

def test_divide_by_zero():
    assert app.divide(10, 0) == "❌ Error: Division by zero."

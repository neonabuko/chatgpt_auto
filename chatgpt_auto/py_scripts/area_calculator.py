# area_calculator.py
import numpy as np

def calculate_area(radius):
    return np.pi * radius ** 2

def main():
    radius = float(input("Enter radius: "))
    area = calculate_area(radius)
    print(f"Area of the circle with radius {radius} is {area}.")

if __name__ == '__main__':
    main()
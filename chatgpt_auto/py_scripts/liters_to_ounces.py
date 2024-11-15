# liters_to_ounces.py
def liters_to_ounces(liters):
    return liters * 33.814

liters = float(input("Enter volume in liters: "))
ounces = liters_to_ounces(liters)
print(f"{liters} liters is equal to {ounces:.2f} ounces.")
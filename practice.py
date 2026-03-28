#Define method here
def steps_to_miles(steps):
    
    miles = steps / 2000
    return miles
    while steps < 0:
        raise ValueError("Exception:Negative step count entered")
    

if __name__ == "__main__":
steps = int(input(""))
try:
    miles = steps_to_miles(steps)
    print(f'{miles:.2f}')
except ValueError as ve:
    print(ve)
    
"""This file contains notes and examples on lists and tuples in Python.
#Notes on Lists and Tuples

My_list = ["List", "#", 1]
print(f"My_list is: {My_list[0]} {My_list[1]} {My_list[2]}")
My_list2 = My_list.copy()
My_list2.append(2)
print(f"My_list2 is: {My_list2}")
if 1 in My_list2:
    My_list2.remove(1)
    print(f"My_list2 after removing 1 is: {My_list2}")
else:
    print("1 not found in My_list2")
print(f"Length of My_list2 is: {len(My_list2)}")
My_tuple = ("Tuple", "#", 1)
#My_tuple.append(2)   This will raise an AttributeError since tuples are immutable
#Write a program that gets a list of integers from input, and outputs negative integers in descending order (highest to lowest).
input_list = input("Enter a list of integers separated by spaces:")
ints = [int(x) for x in input_list.split()] #convert input strings to integers
neg_ints = [x for x in ints if x < 0]
neg_ints.sort(reverse=True)
# now print one by one with no brackets, in same line
for num in neg_ints:
    print(num, end=' ')



"""
// user input can be from 18 to 75 or value error exception
user_input =int(input())
while user_input < 18 or user_input > 75:
    throw ValueError("Invalid age")
    def get_age():
    age = int(input())
    while age < 18 or age > 75:
        raise ValueError("Invalid age")
    return age


# TODO: Complete fat_burning_heart_rate() function
def fat_burning_heart_rate(age):
    fat_burning_heart_rate == (220-age)*0.7
    return heart_rate


if __name__ == "__main__":
    # TODO: Modify to call get_age() and fat_burning_heart_rate()
    #       and handle the exception
    age = get_age()
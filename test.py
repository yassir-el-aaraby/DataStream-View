import uuid
import random
import copy
from collections import deque

def generate_random_name():
    # Generating a random name using a combination of letters
    letters = 'abcdefghijklmnopqrstuvwxyz'
    name_length = random.randint(5, 10)
    random_name = ''.join(random.choice(letters) for _ in range(name_length))
    return random_name

# Generating an array with 100 objects
num_objects = 100
objects_array = deque(maxlen=100)

for obj_id in range(num_objects):
    obj_name = generate_random_name()
    
    # Creating the object with ID and random name
    obj = {'id': obj_id, 'name': obj_name}
    
    # Adding the object to the array
    objects_array.appendleft(obj)

# Creating a shallow copy of the first 10 elements of the objects_array
# second_array = copy.deepcopy(objects_array[:10])
second_array = deque(copy.copy(obj) for obj in list(objects_array)[:10])

# Modify an element in the original array
print(objects_array[3]['id'])
print(objects_array[3]['id'])
objects_array[3]['id'] = 6000

# Print both arrays to see the separation
print("Original Array:")
for obj in objects_array:
    print(obj)

print("\nSecond Array:")
for obj in second_array:
    print(obj)

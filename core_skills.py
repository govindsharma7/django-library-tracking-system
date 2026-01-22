import random
rand_list = random.choice(range(1, 20))

list_comprehension_below_10 = [i for i in range(rand_list) if i < 10]

list_comprehension_below_10 = rand_list.filter(lambda x:x < 10)



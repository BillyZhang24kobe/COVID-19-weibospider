import json

with open('userID.json', 'r') as jfile:
 id_list = json.load(jfile)

list1, list2, list3, list4, list5, list6 = [], [], [], [], [], []
count = 0
for id in id_list:
    if count <= 563782:
        list1.append(id)
    elif count <= 1127564:
        list2.append(id)
    elif count <= 1691346:
        list3.append(id)
    elif count <= 2255128:
        list4.append(id)
    elif count <= 2818910:
        list5.append(id)
    else:
        list6.append(id)
    count += 1

with open('userID_1.json', "w") as jfile:
   json.dump(list1, jfile)

with open('userID_2.json', "w") as jfile:
   json.dump(list2, jfile)

with open('userID_3.json', "w") as jfile:
   json.dump(list3, jfile)

with open('userID_4.json', "w") as jfile:
   json.dump(list4, jfile)

with open('userID_5.json', "w") as jfile:
   json.dump(list5, jfile)

with open('userID_6.json', "w") as jfile:
   json.dump(list6, jfile)

print(count)

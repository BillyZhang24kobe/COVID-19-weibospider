import os, json
import pandas

user_id = set()
for root, dirs, files in os.walk('./output'):
   for dir in dirs:
       dirname = os.path.join(root, dir)
       for filename in os.listdir(dirname):
           if filename.endswith(".csv"):
               filename = os.path.join(dirname, filename)
               data = pandas.read_csv(filename)
               for id in data["user_id"]:
                   user_id.add(id)

user_id_list = list(user_id)
with open('userID.json', "w") as jfile:
   json.dump(user_id_list, jfile)

# with open('userID.json', 'r') as jfile:
#     id = json.load(jfile)
#
# print(len(id))

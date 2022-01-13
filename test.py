#import pathlib as Path
#Path("file.py").touch()
import pymongo

#f = open("demofile2.txt", "a")
#f.write("Now the file has more content!")
#f.close()

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["mydatabase"]

f = open("demofile2.txt", "a")
f.write(str(mydb))
f.close()
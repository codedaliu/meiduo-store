#"_*_coding:UTF-8_*_"
import pickle

dict = {'name':'daliu'}
dump = pickle.dumps(dict)
print(dump)
loda = pickle.loads(dump)
print(loda)
# All dictionaries should be in a json format
import pickle

class Loader:

    
    def _init_(self,dictionary):
	self.dictionary=dictionary

    def getDictionary(self):
	return self.dictionary


    def loadDictionary(self,file_name):
	if file_name is not None :
	    with open(file_name,'r') as dict_file:	
		self.dictionary=pickle.loads(dict_file)
	else:
	    print 'Error in the file specified. Try again.'


    def loadDictionary_from_json(self,source):
	with open(source+'tiny_dict.json','r') as f:
	    dictionary=pickle.loads((f.read()))
	with open(source+'tiny_rules.json','r') as f:
	    rules=pickle.loads((f.read()))
	return [dictionary,rules]




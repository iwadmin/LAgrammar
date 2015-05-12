import io
import sys
import pickle
from nltk.tokenize import word_tokenize

class Interface:

    def start(self,pipe):
        print('Starting the interface with the pipe')
        self.pipe=pipe

    def load_input(self,pipe):
        print ('Getting the input ')
        input_stream=sys.stdin
        input_data=input_stream.readline()
        input_words=word_tokenize(input_data)
        return input_words

    def load_dict(self,dict_file_name):
        print ('Getting the dictionary')
        with open(dict_file_name,'w') as dict_file:
            pickle.dump("{'a':1}",dict_file)
	    #self.dict_json=pickle.load(dict_file)
	    

    
    def load_dict_file(self,dict_file_name):
        print ('Getting the file to be processed')
        with open(dict_file_name,'r') as dict_file:
            file_data=dict_file.read()	    
        print (file_data)




    


import io
import sys
import language_check
import rethinkdb as r
from rethinkdb import RqlRuntimeError
from plagiarismChecker import PlagiarismChecker
class Processor:
	
    def __init__(self):
        simple_dictionary=[]
        self.macros={}
		



    def start(self,pipe):
        print ('Starting the Processor')
        self.pipe=pipe
#Load the dictionary
        r.connect('localhost', 28015).repl()
        tool=language_check.LanguageTool('en-GB')
        try:
            r.db_create('lagrammer').run()
        except RqlRuntimeError:
            try:
                r.db('lagrammer').table_create('comments').run()
            except RqlRuntimeError:
                print("The table aready exists")            
#        with open('comments','r') as comments:
        comments={}
        pc = PlagiarismChecker()
        while True:
            user_dict={}
            if True:
                print ('Enter the user name:')
                input_stream=sys.stdin
                user_name=input_stream.readline()
                user_dict['name']=user_name
                if user_name not in pc.comments.keys():
                    pc.add_user(user_name) 
                print ('Enter the comment to be checked for grammar')
                input_data=input_stream.readline()
                if  input_data in pc.get_comments(user_name):
                    print("The comment by the user "+user_name+ " is Plagiarised and hence will not be analyzed" )
                    continue
                else:
                    print("Analyzing the comment "+input_data)
                    pc.add_comments(user_name,[input_data])
                    

                comment_dict={}
                comment_dict['data']=input_data
                print('The sentence is:'+input_data)
                matches=tool.check(input_data)
                analysis={'rule_id':[],'str':[],'category':[],'msg':[],'spos':[],'epos':[],'suggestions':[]}

                for match in matches:
                    analysis['rule_id'].append(match.ruleId)
                    analysis['str'].append(match.__str__())
                    analysis['category'].append(match.category)
                    analysis['msg'].append(match.msg)
                    analysis['spos'].append(match.fromx)
                    analysis['epos'].append(match.tox)
                    analysis['suggestions'].append(match.replacements)



                    print (str(match)+' THE CORRECTION AND THE SUGGESTION')
                
                comment_dict['analysis']=analysis
                user_dict['comment']=comment_dict
                r.db('lagrammer').table('comments').insert(user_dict).run()
                print(' \n\n '+str(r.db('lagrammer').table('comments').filter({'name':user_name}).run()))

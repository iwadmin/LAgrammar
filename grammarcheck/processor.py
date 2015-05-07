import json
import io
import sys
import language_check
import rethinkdb as r
from rethinkdb import RqlRuntimeError
from plagiarismChecker import PlagiarismChecker
import psycopg2
from datetime import datetime

class Processor:
	
    def __init__(self):
        simple_dictionary=[]
        self.macros={}
		
   
    def analyze_comments_from_db(self,pipe):
        self.pipe=pipe
# Get the comments from the comments table. Currently all of the comments are pulled from the database. But, later on a date range is to be used for 
# getting only the 'new' comments.
        conn = psycopg2.connect("dbname=iwadmin user=idb password=idb")
        cur = conn.cursor()
        cur.execute("SELECT * FROM comments ORDER BY commentable_id;")
        all_comments=cur.fetchall()
        dict_of_comments_by_users={}
        for comment in all_comments:
            if comment[4] not in dict_of_comments_by_users.keys():
                dict_of_comments_by_users[comment[4]]={}
            if comment[2] not in dict_of_comments_by_users[comment[4]].keys():
                dict_of_comments_by_users[comment[4]][comment[2]]=[]

            dict_of_comments_by_users[comment[4]][comment[2]].append({'data':comment[1],'datetime':comment[5]})
        cur.close()
        conn.close()

# Creating and/or updating the lagrammer database and the comments table in rethinkdb.
        r.connect('localhost', 28015).repl()
        tool=language_check.LanguageTool('en-GB')
        try:
            r.db_create('lagrammer').run()
        except RqlRuntimeError:
            try:
                r.db('lagrammer').table_create('comments').run()
            except RqlRuntimeError:
                print("The table aready exists")


        users=dict_of_comments_by_users.keys()
        pc = PlagiarismChecker()
        dict_of_items={}
        for user in users:
            items=dict_of_comments_by_users[user].keys()
            for item in items:
                if (item not in dict_of_items):
                    dict_of_items[item]={}
                if (user not in dict_of_items[item]):
                    dict_of_items[item][user]=[]
                comments=dict_of_comments_by_users[user][item]    
                for comment in comments:
                    user_dict={}
                    comment_dict={}
                    comment_dict['user_id']=user
                    comment_dict['item_id']=item
                    comment_dict['data']=comment['data']
                    comment_dict['datetimestamp']=str(comment['datetime'])
                    print('The sentence is:'+comment['data'])
                    users_by_item=dict_of_items[item].keys()
                    for user_by_item in users_by_item:
                        if comment['data'] in dict_of_items[item][user_by_item]:
                            print('plagiarised')
                            comment_dict['type']='plagiarised'
                            user_dict['comment']=comment_dict
                            break
                    if 'type' in comment_dict and comment_dict['type']=='plagiarised' :
                        dict_of_items[item][user].append(comment['data'])
                        continue	
                    try:
                        matches=tool.check(comment['data'])
                    except :
                        print('Some exception in checking')
                        tool=language_check.LanguageTool('en-GB')
                        continue
                    print('analyzed')
                    analysis={'rule_id':[],'category':[],'msg':[],'spos':[],'epos':[],'suggestions':[]}
                    if len(matches)==0:
                        comment_dict['type']='good'
                        user_dict['comment']=comment_dict
                        dict_of_items[item][user].append(comment['data'])
                        print(json.dumps(user_dict,indent=4,sort_keys=True))      
                        continue
                        
                    for match in matches:
                        analysis['rule_id'].append(match.ruleId)
                        #analysis['str'].append(match.__str__())
                        analysis['category'].append(match.category)
                        analysis['msg'].append(match.msg)
                        analysis['spos'].append(match.fromx)
                        analysis['epos'].append(match.tox)
                        analysis['suggestions'].append(match.replacements)
                    dict_of_items[item][user].append(comment['data'])
                        #print (str(match)+' THE CORRECTION AND THE SUGGESTION')
                    comment_dict['analysis']=analysis
                    user_dict['comment']=comment_dict
                    print(json.dumps(user_dict,indent=4,sort_keys=True))
                    r.db('lagrammer').table('comments').insert(user_dict).run()
                    #print(' \n\n '+str(r.db('lagrammer').table('comments').filter({'name':user}).run()))
                    



    @staticmethod
    def print_the_analysis(dictionary):
        print(json.dumps(dictionary,indent=4,sort_keys=True))

    def analyze_comments_from_stdin(self,pipe):
        self.pipe=pipe
        print ('Starting the Processor')
        r.connect('localhost', 28015).repl()
        tool=language_check.LanguageTool('en-GB')
        try:
            r.db_create('lagrammer').run()
        except RqlRuntimeError:
            try:
                r.db('lagrammer').table_create('comments').run()
            except RqlRuntimeError:
                print("The table aready exists")
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
                comment_dict['datetimestamp']=str(datetime.now())
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

import json
import io
import sys
import language_check
import rethinkdb as r
from rethinkdb import RqlRuntimeError
from plagiarismChecker import PlagiarismChecker
from datetime import datetime
import pycurl
class Processor:
	
    def __init__(self):
        simple_dictionary=[]
        self.macros={}
		
   
    def analyze_comments_from_db(self,pipe):
        self.pipe=pipe
        dict_of_comments_by_users={}
        language_abbrv='en-GB'
        spelling_mistake_rule_id='MORFOLOGIK_RULE_EN'       
        tool_for_replace_errors=language_check.LanguageTool('en-US')        
        page=0
        comments_per_page=15
        while True:
            page+=1
            if page > 100:
                break
            self.buffer = io.BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, 'http://learnapt.informationworks.in/api/grammar_check/comments?per_page='+str(comments_per_page)+'&page='+str(page))
            c.setopt(c.HTTPHEADER, ['Authorization: Token %s' % str('b2661fa415440adb2ef6eb37af6ca3e5')])
            c.setopt(c.WRITEDATA, self.buffer)
            c.perform()
            c.close()
            self.body = self.buffer.getvalue()
            comments_details=json.loads(self.body.decode('UTF-8'))['comments']
            for comment_details in comments_details:
                if comment_details['content'] is None or str(comment_details['content']).strip() == '' :
                    continue
                if comment_details['user_id'] not in dict_of_comments_by_users.keys():
                    dict_of_comments_by_users[comment_details['user_id']]={}
                if comment_details['commentable_id'] not in dict_of_comments_by_users[comment_details['user_id']].keys():
                    dict_of_comments_by_users[comment_details['user_id']][comment_details['commentable_id']]=[]
                dict_of_comments_by_users[comment_details['user_id']][comment_details['commentable_id']].append({'data':comment_details['content'].strip(),'datetime':comment_details['created_at'],'commentable_type':comment_details['commentable_type']})

# Creating and/or updating the lagrammer database and the comments table in rethinkdb.
        r.connect('localhost', 28015).repl()
        tool=language_check.LanguageTool(language_abbrv)
        try:
            r.db_create('lagrammer').run()
        except RqlRuntimeError:
            try:
                r.db('lagrammer').table_create('comments').run()
            except RqlRuntimeError:
                print("The table aready exists")
        users=dict_of_comments_by_users.keys()
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
                    comment_dict['commentable_type']=comment['commentable_type']
                    comment_dict['data']=comment['data']
                    comment_dict['datetimestamp']=str(comment['datetime'])
                    print('The comment is:'+comment['data'])
                    users_by_item=dict_of_items[item].keys()
                    for user_by_item in users_by_item:
                        if comment['data'] in dict_of_items[item][user_by_item]:
                            comment_dict['type']='plagiarised'
                            user_dict['comment']=comment_dict
                            break
                    if 'type' in comment_dict and comment_dict['type']=='plagiarised' :
                        dict_of_items[item][user].append(comment['data'])
                        r.db('lagrammer').table('comments').insert(user_dict).run()
                        continue

                    count_retries=0	
                    while True:
                        count_retries+=1
                        if count_retries>1:
                            break

                        try:
                            matches=tool.check(comment['data'])
                            break
                        except :
                            tool=language_check.LanguageTool('en-GB')
                            
                    analysis={'rule_id':[],'category':[],'msg':[],'spos':[],'epos':[],'suggestions':[]}
# Special handling for comments which aren't found to be having an error
                    if len(matches)==0:
                        comment_dict['type']='good'
                        user_dict['comment']=comment_dict
                        dict_of_items[item][user].append(comment['data'])
                        r.db('lagrammer').table('comments').insert(user_dict).run()                        
                        continue
                        
                    for match in matches:
# This check is to ensure that words which are misspelled as per exactly one of British and American english dictionaries, and not as per the other, are not to be shown to be as if they are misspelled. Only if there is a spelling mistake as per both the dictionaries, should it consider as a spelling mistake.
                        if match.ruleId == spelling_mistake_rule_id+'_GB':
                            count_retries=0
                            while True:
                                count_retries+=1
                                if count_retries>1:
                                    break

                                try :
                                    matches_for_replace=tool_for_replace_errors.check(comment['data'])
                                    break
                                except:
                                    tool_for_replace_errors=language_check.LanguageTool('en-US')        
                            to_continue=True
                            for match_for_replace in matches_for_replace:
                                if match_for_replace.ruleId==spelling_mistake_rule_id+'_US':
                                    to_continue=False
                                    break    
                            if to_continue==True:
                                continue
# The check to follow is to skip the errors for those words which highlight the differences in american and british dictionaries. This is to narrow the gap between the american and the british dictionaries. 
                        if match.ruleId == 'EN_GB_SIMPLE_REPLACE':
                            continue

                        analysis['rule_id'].append(match.ruleId)
                        analysis['category'].append(match.category)
                        analysis['msg'].append(match.msg)
                        analysis['spos'].append(match.fromx)
                        analysis['epos'].append(match.tox)
                        analysis['suggestions'].append(match.replacements)
                    dict_of_items[item][user].append(comment['data'])
                        #print (str(match)+' THE CORRECTION AND THE SUGGESTION')
                    comment_dict['analysis']=analysis
                    user_dict['comment']=comment_dict
                    #print(json.dumps(user_dict,indent=4,sort_keys=True))
                    r.db('lagrammer').table('comments').insert(user_dict).run()
                    #print(' \n\n '+str(r.db('lagrammer').table('comments').filter({'name':user}).run()))
                    



    @staticmethod
    def print_the_analysis(dictionary):
        print(json.dumps(dictionary,indent=4,sort_keys=True))

    def analyze_comments_from_stdin(self,pipe):
        self.pipe=pipe
        spelling_mistake_rule_id='MORFOLOGIK_RULE_EN'
        #print ('Starting the Processor')
        r.connect('localhost', 28015).repl()
        tool=language_check.LanguageTool('en-GB')
        tool_for_replace_errors=language_check.LanguageTool('en-US')

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
                input_data=input_stream.readline().strip()
                if  input_data in pc.get_comments(user_name):
                    print("The comment by the user "+user_name+ " is Plagiarised and hence will not be analyzed" )
                    continue
                else:
                    print("Analyzing the comment "+input_data)
                    pc.add_comments(user_name,[input_data])
                comment_dict={}
                comment_dict['data']=input_data
                comment_dict['datetimestamp']=str(datetime.now())
                print('The comment is:'+input_data)
                count_retries=0
                while True:
                    count_retries+=1
                    if count_retries>1:
                        break
                    try :
                        matches=tool.check(input_data)
                        break
                    except:
                        tool=language_check.LanguageTool('en-GB')
                analysis={'rule_id':[],'str':[],'category':[],'msg':[],'spos':[],'epos':[],'suggestions':[]}

                for match in matches:
# This check is to ensure that words which are misspelled as per exactly one of British and American english dictionaries, and not as per the other, are not to be shown to be as if they are misspelled. Only if there is a spelling mistake as per both the dictionaries, should it consider as a spelling mistake.
                    if match.ruleId == spelling_mistake_rule_id+'_GB':
                        count_retries=0
                        while True:
                            count_retries+=1
                            if count_retries>1:
                                break

                            try :
                                matches_for_replace=tool_for_replace_errors.check(input_data)
                                break
                            except:
                                tool_for_replace_errors=language_check.LanguageTool('en-US')
                        to_continue=True
                        for match_for_replace in matches_for_replace:
                            if match_for_replace.ruleId==spelling_mistake_rule_id+'_US':
                                to_continue=False
                                break    
                        if to_continue==True:
                            continue
# The check to follow is to skip the errors for those words which highlight the differences in american and british dictionaries. This is to narrow the gap between the american and the british dictionaries. 
                    if match.ruleId == 'EN_GB_SIMPLE_REPLACE':
                        continue
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




    @staticmethod
    def get_analysis():
        r.connect('localhost', 28015).repl()        
#        allcomments=r.db('lagrammer').table('comments').run()
        allcomments=r.db('lagrammer').table('comments').filter({'comment':{'type':'plagiarised'}}).run()
#        allcomments=r.db('lagrammer').table('comments').filter({'comment':{'analysis':{'category':['Grammar']}}}).run()

        i=0
        for comment in allcomments:
            i+=1
            if i>100:
                break
            print(json.dumps(comment,indent=4,sort_keys=True))

            

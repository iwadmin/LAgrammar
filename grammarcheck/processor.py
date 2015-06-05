import json
import io
import sys
import rethinkdb as r
from rethinkdb import RqlRuntimeError
from plagiarismChecker import PlagiarismChecker
from datetime import datetime
import pycurl
from main import PScripts
class Processor:
	
    def __init__(self):
        pass
   
    def analyze_comments_from_db(self,pipe):
        r.connect('localhost', 28015).repl()
#####################Delete the following patch once all of the comments are received and processed.#####################
        try:
            r.db_create('lagrammar').run()
        except RqlRuntimeError:
            try:
                r.db('lagrammar').table_create('raw_comments').run()
            except RqlRuntimeError:
                print("The table raw_comments aready exists")
########################################################################################################################
        dict_of_comments_by_users={}
        spelling_mistake_rule_id='MORFOLOGIK_RULE_EN'       
        try:
            with open('pypg.config','r') as config:
                path=config.read()
                sys.path.append(path)
            import language_check
            from gibberish_detector import gib_detect_train
            from gibberish_detector import gib_detect
            gib_detect_train.train()
        except :
            print("I am sorry, but the language_check is not found, or a valid path where does the language_check package preside. ")
            sys.exit()

        tool_for_replace_errors=language_check.LanguageTool('en-US')        
        page=0
        comments_per_page=50
        cursors=r.db('lagrammar').table('raw_comments').run()
        if True:
            page+=1
#            if(page==1):
#                break
            self.buffer = io.BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, 'http://learnapt.informationworks.in/api/grammar_check/comments?per_page='+str(comments_per_page)+'&page='+str(page))
            c.setopt(c.HTTPHEADER, ['Authorization: Token %s' % str('b2661fa415440adb2ef6eb37af6ca3e5')])
            c.setopt(c.WRITEDATA, self.buffer)
            c.perform()
            c.close()
            self.body = self.buffer.getvalue()
            comments_details=json.loads(self.body.decode('UTF-8'))['comments']
            print("Got "+str(comments_per_page) + " comments for the page "+str(page) )
#            if(len(comments_details)==0):
#                break
            for comment_details in cursors:
                if(comment_details['id']%1000==0):
                    print(str(comment_details['id']))
                if comment_details['content'] is None or str(comment_details['content']).strip() == '' :
                    continue
                if comment_details['user_id'] not in dict_of_comments_by_users.keys():
                    dict_of_comments_by_users[comment_details['user_id']]={}
                if comment_details['commentable_id'] not in dict_of_comments_by_users[comment_details['user_id']].keys():
                    dict_of_comments_by_users[comment_details['user_id']][comment_details['commentable_id']]=[]
                dict_of_comments_by_users[comment_details['user_id']][comment_details['commentable_id']].append({'id':comment_details['id'], 'data':comment_details['content'].strip(),'datetime':comment_details['created_at'],'commentable_type':comment_details['commentable_type']})
                try:
                    r.db('lagrammar').table('raw_comments').insert(comment_details).run()
                except:
                    print('Not able to insert the raw comment details. Is it important? ')
#        dict_of_comments_by_users={1:{1:[{'id':'1','data':'hi','datetime':'2014-12-05T17:04:31.813+05:30', 'commentable_type':'Item'},{'id':'2','data':'hi','datetime':'2014-12-05T17:04:31.813+05:30','commentable_type':'Item'}, {'id':'3','data':'hi','datetime':'2014-12-05T17:04:31.813+05:30','commentable_type':'Item'}]},2:{2:[{'id':'1','data':'hi','datetime':'2014-12-05T17:04:31.813+05:30', 'commentable_type':'Item'}]}}
# Creating and/or updating the lagrammar database and the comments table in rethinkdb.


        tool=language_check.LanguageTool('en-GB')
        try:
            r.db_create('lagrammar').run()
        except RqlRuntimeError:
            try:
                r.db('lagrammar').table_create('analyzed_comments').run()
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
                    type_of_comment=None
                    comment_dict={}
                    comment_dict['user_id']=user
                    comment_dict['comment_id']=comment['id']
                    comment_dict['item_id']=item
                    comment_dict['commentable_type']=comment['commentable_type']
                    comment_dict['data']=comment['data']
                    comment_dict['datetimestamp']=str(comment['datetime'])
                    comment_dict['rule_id']=[]
                    comment_dict['category']=[]
                    comment_dict['msg']=[]
                    comment_dict['spos']=[]
                    comment_dict['epos']=[]
                    comment_dict['suggestions']=[]
                    print('The comment is:'+comment['data'])

                    # Next we check whether the comment is gibberish.
                    gib_detect_tokens=[]
                    gib_detect_results=gib_detect.check(comment['data'])
                    if gib_detect_results is not None:
                        type_of_comment='gibberish'
                        print('The comment is '+comment['data'] +' a gibberish one.')
                        for result in gib_detect_results:
                            gib_detect_tokens.append(result['token'])

                    # Next we check for the comment to be either copied, repeated or plagiarized if the comment is not a gibberish one.
                    if(type_of_comment != 'gibberish'):            
                        users_by_item=dict_of_items[item].keys()
                        for user_by_item in users_by_item:
                            if comment['data'] in dict_of_items[item][user_by_item]:
                                if user!=user_by_item:
                                    comment_dict['type']='copied'
                                    comment_dict['copied_from_user']=user_by_item
                                    type_of_comment='copied'
                                else:
                                    comment_dict['type']='repetition'
                                    type_of_comment='repetition'
                                break
                        if type_of_comment!='copied' and type_of_comment!='repetition':
                            try:#Check for plagiarism against the sources from the internet.
                                plagiarism_results=PScripts.main(comment['data'],'po.txt') 
                                if len(plagiarism_results.keys())>0:
                                    type_of_comment='plagiarised'
                                    comment_dict['type']='plagiarised'
                                    comment_dict['plagiarised_dict']=plagiarism_results
                            except:
                                print("Plagiarism check failed.")
                        
                                            
                    count_retries=0	
                    while count_retries<2:
                        count_retries+=1
                        try:
                            matches=tool.check(comment['data'])
                            break
                        except :
                            tool=language_check.LanguageTool('en-GB')
                            
                    #analysis={'rule_id':[],'category':[],'msg':[],'spos':[],'epos':[],'suggestions':[]}
# Special handling for comments which aren't found to be having an error
                    if len(matches)==0:
                        comment_dict['type']='good'
                        dict_of_items[item][user].append(comment['data'])
                        r.db('lagrammar').table('analyzed_comments').insert(comment_dict).run()                        
                        continue
                    else:
                        if type_of_comment is not None:
                            comment_dict['type']=type_of_comment
                        else:
                            comment_dict['type']='incorrect'
                    for match in matches:
# This check is to ensure that words which are misspelled as per exactly one of British and American english dictionaries, and not as per the other, are not to be shown to be as if they are misspelled. Only if there is a spelling mistake as per both the dictionaries, should it consider as a spelling mistake.
                        token_with_error=comment['data'][match.fromx:match.tox+1]
                        if match.ruleId == spelling_mistake_rule_id+'_GB':
                            count_retries=0
                            while count_retries<2:
                                count_retries+=1
                                try :
                                    matches_for_replace=tool_for_replace_errors.check(comment['data'])
                                    break
                                except:
                                    tool_for_replace_errors=language_check.LanguageTool('en-US')        
                            to_continue=True
                            for match_for_replace in matches_for_replace:
                                if match_for_replace.ruleId==spelling_mistake_rule_id+'_US':
                                    if token_with_error in gib_detect_tokens:
                                        comment['type']='gibberish'
                                        comment['gibberish_details']=gib_detect_results
                                    else:
                                        comment['type']='incorrect'
                                        type_of_comment='incorrect'    
                                    to_continue=False
                                    break
                            if to_continue==True:
                                continue
# The check to follow is to skip the errors for those words which highlight the differences in american and british dictionaries. This is to narrow the gap between the american and the british dictionaries. 
                        if match.ruleId == 'EN_GB_SIMPLE_REPLACE':
                            continue

                        comment_dict['rule_id'].append(match.ruleId)
                        comment_dict['category'].append(match.category)
                        comment_dict['msg'].append(match.msg)
                        comment_dict['spos'].append(match.fromx)
                        comment_dict['epos'].append(match.tox)
                        comment_dict['suggestions'].append(match.replacements)
                    dict_of_items[item][user].append(comment['data'])
                    r.db('lagrammar').table('analyzed_comments').insert(comment_dict).run()
                    



    @staticmethod
    def print_the_analysis(dictionary):
        print(json.dumps(dictionary,indent=4,sort_keys=True))

    def analyze_comments_from_stdin(self,pipe):
        self.pipe=pipe
        spelling_mistake_rule_id='MORFOLOGIK_RULE_EN'
        #print ('Starting the Processor')
        r.connect('localhost', 28015).repl()
        try:
            with open('pypg.config','r') as config:
                path=config.read()
                sys.path.append(path)
            import language_check
        except FileNotFoundError:
            print("I am sorry, but the language_check is not found, or a valid path where does the language_check package preside. ")
            sys.exit()
        tool=language_check.LanguageTool('en-GB')
        tool_for_replace_errors=language_check.LanguageTool('en-US')

        try:
            r.db_create('lagrammar').run()
        except RqlRuntimeError:
            try:
                r.db('lagrammar').table_create('analyzed_comments').run()
            except RqlRuntimeError:
                print("The table aready exists")
        comments={}
        pc = PlagiarismChecker()
        while True:
            user_dict={}
            comment_dict={}
            comment_dict['rule_id']=[]
            comment_dict['category']=[]
            comment_dict['msg']=[]
            comment_dict['spos']=[]
            comment_dict['epos']=[]
            comment_dict['suggestions']=[]

            if True:
                print ('Enter the user name:')
                input_stream=sys.stdin
                user_name=input_stream.readline().strip()
                comment_dict['name']=user_name
                if user_name not in pc.comments.keys():
                    pc.add_user(user_name) 
                print ('Enter the comment to be checked for grammar')
                input_data=input_stream.readline().strip()
                print(input_data)                
                
                comment_dict['data']=input_data
                comment_dict['datetimestamp']=str(datetime.now())
                print('The comment is:'+input_data)
                try:
                    plagiarism_results=PScripts.main(input_data,'po.txt')
                    if  len(plagiarism_results.keys()) >0:
                        print("The comment by the user "+user_name+ " is Plagiarised and hence will not be analyzed" )
                        comment_dict['type']='plagiarised'
                        comment_dict['plagiarised_dict']=plagiarism_results
                        r.db('lagrammar').table('analyzed_comments').insert(comment_dict).run()
                        continue
                except:
                    print("Plagiarism check failed")
                print("Analyzing the comment "+input_data)
                pc.add_comments(user_name,[input_data])
                count_retries=0
                matches=[]
                while True:
                    count_retries+=1
                    if count_retries>1:
                        break
                    try :
                        matches=tool.check(input_data)
                        break
                    except:
                        tool=language_check.LanguageTool('en-GB')
                #analysis={'rule_id':[],'str':[],'category':[],'msg':[],'spos':[],'epos':[],'suggestions':[]}

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
                    comment_dict['rule_id'].append(match.ruleId)
                    comment_dict['str'].append(match.__str__())
                    comment_dict['category'].append(match.category)
                    comment_dict['msg'].append(match.msg)
                    comment_dict['spos'].append(match.fromx)
                    comment_dict['epos'].append(match.tox)
                    comment_dict['suggestions'].append(match.replacements)
                    print (str(match)+' THE CORRECTION AND THE SUGGESTION')                
                r.db('lagrammar').table('analyzed_comments').insert(comment_dict).run()



    @staticmethod
    def get_analysis():
        r.connect('localhost', 28015).repl()        
#        allcomments=r.db('lagrammar').table('comments').run()
        allcomments=r.db('lagrammar').table('analyzed_comments').filter({'comment':{'type':'plagiarised'}}).run()
#        allcomments=r.db('lagrammar').table('comments').filter({'comment':{'analysis':{'category':['Grammar']}}}).run()

        i=0
        for comment in allcomments:
            i+=1
            if i>100:
                break
            print(json.dumps(comment,indent=4,sort_keys=True))

            
    @staticmethod
    def get_analysis():
        r.connect('localhost', 28015).repl()        
#        allcomments=r.db('lagrammar').table('comments').run()
        allcomments=r.db('lagrammar').table('analyzed_comments').filter({'comment':{'type':'plagiarised'}}).run()
#        allcomments=r.db('lagrammar').table('comments').filter({'comment':{'analysis':{'category':['Grammar']}}}).run()

        i=0
        for comment in allcomments:
            i+=1
            if i>100:
                break
            print(json.dumps(comment,indent=4,sort_keys=True))

import io
import sys
import pickle
import twisted
from tree import Tree
from StrPWeb import Webs
import copy
from Utils import Utils
import os.path
class Matcher:

    def __init__(self):
	self.disjuncts={'count':0}
	self.count=0	

    def match(self,tree_or_disjunct,connector):
	found_disjuncts=[]
	listofdisjuncts=tree_or_disjunct
	sign = connector[-1]
	if sign == '-':
	    sign_to_check='+'
	else:
	    sign_to_check='-'
	    
	for disjuncts in listofdisjuncts:
	    if connector[:-1]+sign_to_check in disjuncts:
		found_disjuncts.append(disjuncts)
	return True 


    
    def does_equal(self,token1,token2):
	pass

    def convert_tree_to_links(self,tree):

	if isinstance(tree,Tree) and tree.val == None :
# The ori and &i operations for the negation in the tree have to be put back to or and & :)
	    if len(tree.nodes)==2:
	        return False	
	    elif len(tree.nodes)==1 and isinstance(tree.nodes[0],Tree):
		print str(tree.nodes[0]) + str(tree) + ' >>>'
		return self.convert_tree_to_links(tree.nodes[0])
	    elif len(tree.nodes)==1 and not isinstance(tree.nodes[0],Tree):
		print 'An extended string node found'
		return [[tree.nodes[0]]]
	elif tree.val !=None:
	    tree.val=tree.val.split('$')[0]
	    
	nodes= tree.nodes
	templist=[]	
	if tree.val=='&':
	    nodelists=[]
	    if not isinstance(nodes[0],Tree) and not isinstance(nodes[1],Tree) :
		return [[nodes[0],nodes[1]]]
	    elif  isinstance(nodes[0],Tree) and not isinstance(nodes[1],Tree):	
	        subtreelists=self.convert_tree_to_links(nodes[0])
		returnlist=[]		
		for subtreelist in subtreelists:
		     subtreelist.append(nodes[1])
		     returnlist.append(subtreelist)
		return returnlist
	    elif  not isinstance(nodes[0],Tree) and  isinstance(nodes[1],Tree):	
	        subtreelists=self.convert_tree_to_links(nodes[1])
		returnlist=[]		
		for subtreelist in subtreelists:
		     subtreelist.append(nodes[0])
		     returnlist.append(subtreelist)
		return returnlist

	    elif  isinstance(nodes[0],Tree) and  isinstance(nodes[1],Tree):	
		subtreelists0=self.convert_tree_to_links(nodes[0])
		subtreelists1=self.convert_tree_to_links(nodes[1])
		returnlist=[]
		for list0 in subtreelists0:
		    for list1 in subtreelists1:
		    	templist=[]
			templist.extend(list1)
			templist.extend(list0)			
			returnlist.append(templist)
		return returnlist
	
	elif tree.val=='or':
	    nodelists=[]
	    if not isinstance(nodes[0],Tree) and not isinstance(nodes[1],Tree) :
		nodelists.extend([[nodes[0]],[nodes[1]]])
		return nodelists
	    elif  isinstance(nodes[0],Tree) and not isinstance(nodes[1],Tree):	
	        subtreelists=self.convert_tree_to_links(nodes[0])
		subtreelists.append([nodes[1]])
		return subtreelists
	    elif  not isinstance(nodes[0],Tree) and  isinstance(nodes[1],Tree):	
	        subtreelists=self.convert_tree_to_links(nodes[1])
		subtreelists.append([nodes[0]])
		return subtreelists
	    elif  isinstance(nodes[0],Tree) and  isinstance(nodes[1],Tree):	
		subtreelists0=self.convert_tree_to_links(nodes[0])
		subtreelists1=self.convert_tree_to_links(nodes[1])
		subtreelists0.extend(subtreelists1)
	    	return subtreelists0			    		
		
	




    def convert_links_to_web(self,list_of_lists):
	graph={}	
	index_of_plank=0;
	for plank in list_of_lists:
	    keys=graph.keys()
	    for conn in plank:
		if conn[:4] == 'NONE':
		    continue		    
		if conn not in keys:
		    graph[conn]=[]
		graph[conn].append(index_of_plank)
	    index_of_plank +=1

	return graph



    def construct_links(self,stack_of_webs,distance,level,justone):
# DEFINE TWO STACK, ONE FOR SUGGESTIONS and OTHER FOR MISTAKES.
	suggest=[]
	mistakes=[]	
	length=len(stack_of_webs)
	level +=1
	print('The level is >>>>>>>>>>>>>>>>>> '+str(level) + ' >>>>>>>>>>>>>>>>>>>>>>> '+str(stack_of_webs) + ' THE DISTANCE IS '+str(distance))
	if stack_of_webs==None:
	    print('The level is .................................'+str(level) + '................ but null stack of webs')
	    return []
	elif length>2:
	    constructionincomplete=False
	    for s in stack_of_webs[1:-1]:
		if len(s.connectors)!=0:
		    constructionincomplete=True			    
		    break
	    if not constructionincomplete:
		print('The level is .................................'+str(level) + '................ COMPLETE construction'		)
		return stack_of_webs
	count=0 
	toskip=[]
# When the length of the stack is breater than 2.    	    
	i=count

	while i>=count and i<length:
	    j=i+distance-1
	    toskip=[]
	    while j>=i+distance-1 and j<length-1  and (not justone or j<i+distance ):
		j = j+1
		w1=stack_of_webs[i]
		w2=stack_of_webs[j]
# If the two selected webs are already connected, then skip
		if (w2 in w1.whom_linked and w1 in w2.whom_linked):
		    print('ALREADY CONNECTED, HENCE SKIPPING THE WEBS')
		    continue
# Create backups for the words that are forming the links
		backupstack=Matcher.create_backup(stack_of_webs)
		ismatched=Webs.can_merge(w1,w2,toskip)
		if ismatched:
		    # part one	
		    partone=stack_of_webs[i:j+1]
		    updatedstackone=partone
		    # part three
		    partthree=(stack_of_webs[0:i+1])
		    updatedstackthree=partthree
		    # part two
		    parttwo=(stack_of_webs[j:length])
		    updatedstacktwo=parttwo
		    # update all of  the three parts
		    
# The third subpart check
		    if len(partthree) >1:
			updatedstackthree=self.construct_links(partthree,len(partthree)-1,level,False)
		    	print('\n**************PRINTING UPDATEDSTACKTHREE '+str(level))
		    	Matcher.print_stack(updatedstackthree)
		    	print('\n**************PRINTED UPDATEDSTACKTHREE'+str(level)+'***************'+str(distance)	    )

		    	allconnectedthree=True
		    	for index in range(0,len(updatedstackthree)-1):			
			    if ((index==len(updatedstackthree)-1)) and level>1:
			        continue			
# This piece of computation is to determine if a plank we have selected is a superset of another plank	
		            f=set([])
		            if len(updatedstackthree[index].list_links)!=0 and len(updatedstackthree[index].connectors)!=0 :
			        d=set(updatedstackthree[index].graph[updatedstackthree[index].list_links[0]])
			        for c in updatedstackthree[index].list_links[1:]:
			            d=d.intersection(set(updatedstackthree[index].graph[c]))
			        e=None
			        for c in updatedstackthree[index].connectors:
				    if c[0]=='@' and c in updatedstackthree[index].list_links:
				        continue
				    if e==None:
				        e=d-set(updatedstackthree[index].graph[c])
			            else:
				        e=e.intersection(d-set(updatedstackthree[index].graph[c]))	
			        f=e
			    if len(updatedstackthree[index].connectors) !=0:
			        print( str(f) + ' THE DIFFERENCE FOR THREE IS '+str(updatedstackthree[index]))

			        if len(f)==0:
			            mistakes.append(updatedstackthree[index])
			            allconnectedthree=False
			        else:
				    updatedstackthree[index].connector=[]	    	
							

		        if allconnectedthree==False :
			    print(' Have to revert back********************************'+str(level))
			    stack_of_webs=Matcher.restore_backup(stack_of_webs,backupstack)
			    Matcher.print_stack(stack_of_webs) 			
			    print("THE LINK TO BE REVERSED IS ****************************** "+str(ismatched[2]))
			    j = j-1
			    toskip.append(ismatched[2])
		    	    continue

# The first subpart check

		    if len(partone) >1:
		        updatedstackone=self.construct_links(partone,len(partone)-1,level,False)
		        print('**************PRINTING UPDATEDSTACKONE '+str(level) )
		        Matcher.print_stack(updatedstackone)
		    	print('**************PRINTED UPDATEDSTACKONE '+str(level)+ '************** '+str(distance))
		        allconnectedone=True
		        for connected_web in updatedstackone:
			    if  j==len(stack_of_webs)-1 and updatedstackone.index(connected_web)== len(updatedstackone)-1:
				continue
			    
# This piece of computation is to determine if a plank we have selected is a superset of another plank	
		            f=set([])
		            if len(connected_web.list_links)!=0 and len(connected_web.connectors)!=0 :
			        d=set(connected_web.graph[connected_web.list_links[0]])
			        for c in connected_web.list_links[1:]:
			            d=d.intersection(set(connected_web.graph[c]))
			        e=None
			        for c in connected_web.connectors:
				    if c[0]=='@' and c in connected_web.list_links:
				        continue
				    if e==None:
				        e=d-set(connected_web.graph[c])
			            else:
				        e=e.intersection(d-set(connected_web.graph[c]))						     
			        f=e
			    if len(connected_web.connectors) !=0: 
			        print( str(f) + '  THE DIFFERENCE FOR PART ONE'+str(connected_web))
			        if len(f)==0:
			            mistakes.append(connected_web)
			            allconnectedone=False
			        else:
				    connected_web.connectors=[]


		        if allconnectedone==False :
			    print('\nHave to revert back********************************'+str(level))
			    stack_of_webs=Matcher.restore_backup(stack_of_webs,backupstack)
			    Matcher.print_stack(stack_of_webs) 			
			    print("THE LINK TO BE REVERSED IS ****************************** "+str(ismatched[2]))
			    j = j-1
			    toskip.append(ismatched[2])
		    	    continue



# The second subpart check
		    if len(parttwo) >1:
		        updatedstacktwo=self.construct_links(parttwo,len(parttwo)-1,level,False)
		        print('\n**************PRINTING UPDATEDSTACKTWO '+str(level))
		        Matcher.print_stack(updatedstacktwo)
		        print('\n**************PRINTED UPDATEDSTACKTWO'+str(level)+'***************'+str(distance)	    )

		        allconnectedtwo=True
		        for index in range(0,len(updatedstacktwo)):			
# This piece of computation is to determine if a plank we have selected is a superset of another plank	
		            f=set([])
		            if len(updatedstacktwo[index].list_links)!=0 and len(updatedstacktwo[index].connectors)!=0 :
			        d=set(updatedstacktwo[index].graph[updatedstacktwo[index].list_links[0]])
			        for c in updatedstacktwo[index].list_links[1:]:
			            d=d.intersection(set(updatedstacktwo[index].graph[c]))
			        e=None
			        for c in updatedstacktwo[index].connectors:
				    if c[0]=='@' and c in updatedstacktwo[index].list_links:
				        continue
				    if e==None:
				        e=d-set(updatedstacktwo[index].graph[c])
			            else:
				        e=e.intersection(d-set(updatedstacktwo[index].graph[c]))	
			        f=e
			    if len(updatedstacktwo[index].connectors) !=0:
			        print( str(f) + ' THE DIFFERENCE FOR TWO IS '+str(updatedstacktwo[index]))

			        if len(f)==0:
			            mistakes.append(updatedstacktwo[index])
			            allconnectedtwo=False
			        else:
				    updatedstacktwo[index].connector=[]	    	
							

		        if allconnectedtwo==False :
			    print(' Have to revert back********************************'+str(level))
			    stack_of_webs=Matcher.restore_backup(stack_of_webs,backupstack)
			    Matcher.print_stack(stack_of_webs) 			
			    print("THE LINK TO BE REVERSED IS ****************************** "+str(ismatched[2]))
			    j = j-1
			    toskip.append(ismatched[2])
		    	    continue
# Merge the edge webs for building the final stack of webs
		    stack_of_webs=updatedstackthree[:-1]
		    stack_of_webs.extend(updatedstackone)
		    stack_of_webs.extend(updatedstacktwo[1:])
		    print('RETURNING AT THE LEVEL ................. '+str(level)+' AND THE DISTANCE '+str(level))
		    return stack_of_webs
	    i+=1
# Here we return a false as a valid statement will not reach till here 
	print('The level is .................................'+str(level) + '....'+str(distance)+'............  FALSIFYING NO MATCH FOUND')
	Matcher.print_stack(stack_of_webs)
	print('The level is .................................'+str(level) + '..................... ' + str(distance)+' ....................')
# We might have to decrease the distance in such a case and attempt again. 
	if  distance>1 and not Matcher.check_graceful_exit(stack_of_webs) :
	    print('DECREASING THE DISTANCE AT LEVEL ****************** '+str(level)+ ' '+str(distance))
	    self.construct_links(stack_of_webs,distance-1,level-1,True)	
	return stack_of_webs
	

    @staticmethod
    def print_stack(stack_of_webs):
	print(' **********PRINTING THE STACK****************** ')
	for i in range(0,len(stack_of_webs)):
	    print(str(stack_of_webs[i].list_links)+' >>>>>>>>>> LINKS  ')
	    print(str(stack_of_webs[i].connectors)+' >>>>>>>>>> CONNECTORS ')
	    print(str(stack_of_webs[i].whom_linked)+' >>>>>>>>>> whom ')
	    print(str(stack_of_webs[i].name)+' >>>>>>>>>> WHO ')
	print('PRINTED THE STACK ********************************')


    @staticmethod
    def create_backup(stack_to_backup):
	backupstack=[]
	for aweb in stack_to_backup:
	    backupstack.append([copy.copy(aweb.connectors),copy.copy(aweb.list_links),copy.copy(aweb.whom_linked)])
	return backupstack

    @staticmethod
    def restore_backup(stack_to_reload,backupstack):
	for index in range(0,len(backupstack)):
	    stack_to_reload[index].connectors=copy.copy(backupstack[index][0])
	    stack_to_reload[index].whom_linked=copy.copy(backupstack[index][2])
	    stack_to_reload[index].list_links=copy.copy(backupstack[index][1])
	return stack_to_reload
	    

    @staticmethod
    def check_graceful_exit(stack_of_webs):
	print( " ***********HERE WE HAVE TO CHECK IF WE HAVE OBTAINED A SOLUTION **********************")
	isvalid=True
	for web in stack_of_webs:
	    if len(web.whom_linked)==0:
		return False
	    else:
	        f=set([])
	        if len(web.list_links)!=0 and len(web.connectors)!=0 :
		    d=set(web.graph[web.list_links[0]])
	            for c in web.list_links[1:]:
		        d=d.intersection(set(web.graph[c]))
		    e=None
		    for c in web.connectors:
			if c[0]=='@' and c in web.list_links:
			    continue
			if e==None:
			    e=d-set(web.graph[c])
			else:
			    e=e.intersection(d-set(web.graph[c]))						     
			f=e
		    if len(web.connectors) !=0: 
		        print( str(f) + ' The difference eeeeeeeeeeeeeeeeeeee'+str(web))
			if len(f)==0:
			    isvalid=False
			    break
	    	
	return isvalid

import io
import sys
import pickle
import twisted
from tree import Tree


class Webs:


    def __self__(self):
	pass
    def setname(self,theword):
	self.name=theword

    def setweb(self,graph):
	self.connectors=graph.keys()
	self.graph=graph
	self.child_webs=None
	self.list_links=[]
	self.whom_linked=[]

    @staticmethod
    def merge(web1,web2):
	if not web1 or not web2:

	    return False
	if web2.child_webs ==None and web1.child_webs ==None:
	    updated=Webs.can_merge(web2,web1)
	    if updated:
		web = Webs()
		web.graph=None
		web.child_webs=updated[0:2]
		web.list_links=[updated[2]]			
		return web 
	    else :
		return False
	elif web2.child_webs ==None and web1.child_webs !=None:
	    for web in web1.child_webs:
		updated=Webs.can_merge(web2,web)
		if updated :
		    return_web=Web()
		    web1.child_webs.remove(web)
		    web1.child_webs.append(updated[1])
		    return_web.child_webs= [updated[0],web1]
		    return_web.list_links=[updated[2]]	
		    return return_web     		   
		
	elif web2.child_webs !=None and web1.child_webs ==None:	    	
	    for web in web2.child_webs:
		updated=Webs.can_merge(web1,web)
		if updated :
		    web2.child_webs.remove(web)
		    web2.child_webs.append(updated[1])
		    return_web=Web()
		    return_web.child_webs= [updated[0],web2]
		    return_web.list_links=[updated[2]]	
		    return return_web     		   
	else :
	    for web2child in web2.child_webs:
		for web1child in web1.child_webs:
		    updated=Webs.can_merge(web1child,web2child)
		    if updated :
		        web2.child_webs.remove(web2child)
		        web1.child_webs.remove(web1child)						
			web2.child_webs.append(updated[0])
		        web1.child_webs.append(updated[1])						
			return_web=Webs()
		        return_web.child_webs= [web1,web2]
		        return_web.list_links=[updated[2]]
		        return return_web   
  		   

	    
    @staticmethod
    def can_merge(web1,web2,toskip):
	pconnectors1=web1.connectors
	pconnectors2=web2.connectors
	#print str(pconnectors1) + ' THE CONNECTORS FOR '+str(web1.name)
	#print str(web1.list_links) + ' THE LINKS FOR '+str(web1.name)
	#print str(pconnectors2) + ' THE CONNECTORS FOR '+str(web2.name)
	#print str(web2.list_links) + ' THE Links FOR '+str(web2.name)
	pconnectors=Webs.intersect_connectors(pconnectors1,pconnectors2,toskip)
	if len(pconnectors1)==0 or len(pconnectors2) ==0:

	    return False
	elif len(pconnectors)==0:

	    return False
	else:
	    oneconnectors=pconnectors.pop().split(' ')
#	    print 'THE CONNECTOR USED IS ********************** '+' '.join(oneconnectors)
# update the web1
	    validconnectors=[]
	    for pconnector1 in pconnectors1:
		a=set(web1.graph[pconnector1]).intersection(set(web1.graph[oneconnectors[0]]))
		links=web1.list_links
		for link in links:
		    a=a.intersection(web1.graph[link])
		if(len(a)!=0):
		    validconnectors.append(pconnector1)
	    web1.connectors=validconnectors
# update the web2
	    validconnectors=[]
	    for pconnector2 in pconnectors2:
		a=set(web2.graph[pconnector2]).intersection(set(web2.graph[oneconnectors[1]]))
		links=web2.list_links
		for link in links:
		    a=a.intersection(web2.graph[link])

		if(len(a)!=0):
		    validconnectors.append(pconnector2)
	    web2.connectors=validconnectors
	    if oneconnectors[0][0]!='@':
		web1.connectors.remove(oneconnectors[0])
	    if oneconnectors[0][1]!='@':
		web2.connectors.remove(oneconnectors[1])
# Keep a tab on the links being used
	    web1.list_links.append(oneconnectors[0])
	    web2.list_links.append(oneconnectors[1])	    
	    web1.whom_linked.append(web2)
	    web2.whom_linked.append(web1)
	    
	    return [web1,web2,' '.join(oneconnectors)]
	
		

    @staticmethod
    def match_connectors(c1,c2):
	if c1[0]=='@':
	    c1=c1[1:]
	if c2[0]=='@':
	    c2=c2[1:]

	c1=c1.split('$')[0]
	c2=c2.split('$')[0]

	if c1[-1]==c2[-1] or c1[-1]=='-':
	    return False
	else:
	    c1=c1[:-1]
	    c2=c2[:-1]
	    
	parentchar1=[]
	parentchar2=[]
	children1=''
	children2=''

	for char in c1:
	    if char.isupper():
		parentchar1.append(char)
	    else :
		children1 +=char
	for char in c2:
	    if char.isupper():
		parentchar2.append(char)
	    else :
		children2 +=char

	if parentchar1 != parentchar2:
	    return False
	else:
	    if len(children1) >= len(children2):
		diff=len(children1)-len(children2)
		for index in range(0,diff):
		    children2+='*'
	    else:
		diff=len(children2)-len(children1)
		for index in range(0,diff):
		    children1+='*'
	    pointer=0
	    while(pointer<len(children1)):
		if(children1[pointer] !='*' and  children2[pointer] !='*'  ):
		    if children1[pointer]!= children2[pointer]:
			return False
	        pointer +=1
	    return True
		    
				

    @staticmethod
    def intersect_connectors(c1,c2,toskip):
	intersection=[]
	for con1 in c1:
	    for con2 in c2:
		if con1[-1]=='-' or con2[-1]=='+':
		    continue
		if str(con1)+' '+str(con2) in toskip:
		    continue
		if Webs.match_connectors(con1,con2) ==True:
		   # print 'CONNECTOR USED IS '+str(con1+' ' +con2)
		    intersection.append(con1+' ' +con2)
	return intersection



import io
import sys
import pickle
import twisted
from tree import Tree


class Webs:


    def __self__(self):
	pass

    def setweb(self,graph):
	self.connectors=graph.keys()
	self.graph=graph
	self.child_webs=None
	self.list_links=[]

    @staticmethod
    def merge(web1,web2):
	if not web1 or not web2:
	    print "The Parse Failed Somerhwere.... " 
	    return False
	if web2.child_webs ==None and web1.child_webs ==None:
	    if Webs.can_merge(web1,web2) :
		web = Webs()
		web.graph=None
		web.child_webs=[web1,web2]				
		return web 
	    else :
		return False
	elif web2.child_webs ==None and web1.child_webs !=None:
	    for web in web1.child_webs:
		updated=Webs.can_merge(web2,web)
		if updated :
		    web1.child_webs.remove(web)
		    web1.child_webs.append(updated[1])
		    web1.child_webs.append(updated[0])
		    return web1     		   
		
	elif web2.child_webs !=None and web1.child_webs ==None:	    	
	    for web in web2.child_webs:
		updated=Webs.can_merge(web1,web)
		if updated :
		    web2.child_webs.remove(web)
		    web2.child_webs.append(updated[1])
		    web2.child_webs.append(updated[0])
		    return web2     		   
	else :
	    for web2child in web2.child_webs:
		for web1child in web1.child_webs:
		    updated=Webs.can_merge(web1child,web2child)
		    if updated :
		        web2.child_webs.remove(web2child)
		        web1.child_webs.remove(web1child)						
			web = Webs()
			web.graph=None
			web.child_webs=[]
			web.child_webs.append(web1.child_webs)
			web.child_webs.append(web2.child_webs)
		        return web     		   

	    
    @staticmethod
    def can_merge(web1,web2):
	pconnectors1=web1.connectors
	pconnectors2=web2.connectors
	pconnectors=set(pconnectors1).intersection(set(pconnectors2))
	if len(pconnectors)==0:
	    return False
	else:
	    oneconnector=pconnectors.pop()
# update the web1
	    for pconnector1 in pconnectors1:
#		print str(web1.graph) + ' >>>>>>>>>>>>>> '
		a=set(web1.graph[pconnector1]).intersection(set(web1.graph[oneconnector]))
		links=web1.list_links
		for link in links:
		    a=a.intersection(web1.graph[link])
#		print a
		if(len(a)==0):
		    web1.connectors.remove(pconnector1)
# update the web2
	    for pconnector2 in pconnectors2:
#		print str(web2.graph) + ' >>>>>>>>>>>>>> '
		a=set(web2.graph[pconnector2]).intersection(set(web2.graph[oneconnector]))
		links=web2.list_links
		for link in links:
		    a=a.intersection(web2.graph[link])

		if(len(a)==0):
		    web2.connectors.remove(pconnector2)
	    web1.connectors.remove(oneconnector)
	    web2.connectors.remove(oneconnector)
# Keep a tab on the links being used
	    web1.list_links.append(oneconnector)
	    web2.list_links.append(oneconnector)	    

	    print str(web1.connectors) + ' >>>><<<<<<<<<>>>>>>>><<<<<<<< '+ str(web2.connectors)
	    return [web1,web2]
	
		


    def match_connectors(self,c1,c2):
	return True

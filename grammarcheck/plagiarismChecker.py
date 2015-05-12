import io
import sys

class PlagiarismChecker:
	
    def __init__(self):
        self.comments={}	

    def add_user(self,user):
        self.comments[user]=[]


    def load_comments(self,user,comments):
        self.comments[user]=comments

    def add_comments(self,user,comments):
        self.comments[user].extend(comments)

    def get_comments(self,user):
        return self.comments[user]



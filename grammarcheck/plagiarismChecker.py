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

<<<<<<< HEAD
    def get_comments(self,user):
        return self.comments[user]

=======


    def get_comments(self,user):
        return self.comments[user]
        
    def check(self,comment):
        isPlagiarised=False
        for c in comments:
            if c==comment:
                isPlagiarised=True
                break
        return isPlagiarised
>>>>>>> bad74ec4d51c587a91159c92b4c3ebe3e11b260d


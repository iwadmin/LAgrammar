import sys

from processor import Processor
p = Processor()

args=sys.argv
pipe=None
if len(args)>2 and args[1]=='-pipe':
    if args[2] is not None and args[2] == 'database':
        p.analyze_comments_from_db(None)
    elif args[2] is not None and args[2] == 'stdin':
        p.analyze_comments_from_stdin(None)
    else:
        print('No valid input pipe specified, and hence the program exited.')
        

#ld=p.process_things('test.dict')
#ld=p.process_things('4.0.dict')
<<<<<<< HEAD

#Processor.get_analysis()
#p.analyze_comments_from_stdin(None)
=======
>>>>>>> dcb30addb8f44bb1b5d786923de57d31f22b8bee

#Processor.get_analysis()
#p.analyze_comments_from_stdin(None)



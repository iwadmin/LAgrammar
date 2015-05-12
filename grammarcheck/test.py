from processor import Processor

p = Processor()
#ld=p.process_things('test.dict')
#ld=p.process_things('4.0.dict')
#p.analyze_comments_from_db(None)
#Processor.get_analysis()
p.analyze_comments_from_stdin(None)




import json
import csv
import urllib2
import re
import time
 
# TODO
# write to file
# record and estimate timing
# functionality to specific paths and size
 
bug_dict = {}
err_dict = {}
bug_loc = './bugs.js'
site_loc = './top-100000.csv'
start_url = 1
end_url = 100000
out_loc = './foundbugs1.csv'

print 'Loading Ghostery bug data from ' + bug_loc
try:
        bug_file=open(bug_loc,'r')
        bug_data=json.load(bug_file)
except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
        exit()
except ValueError:
        print "Value error: Check json format"
        exit()
except Exception as ex:
        print type(ex)
        print 'Unexpected error: ' + str(ex)
        exit()
print 'Ghostery bug data version ' + str(bug_data["bugsVersion"]) + ' loaded and parsed. Found ' + str(len(bug_data["bugs"])) + ' bugs.'
print ''
print 'Loading site list from ' + site_loc
try:
        site_file=open(site_loc)
        site_reader = csv.reader(site_file, delimiter=',')
except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
        exit()
except ValueError:
        print "Value error: Check json format"
        exit()
except Exception as ex:
        print type(ex)
        print 'Unexpected error: ' + str(ex)
        exit()
print 'Site data loaded and ready to read.'
print ''
 
print 'Building dictionary of bug patterns to be searched for.'
i=0
for bug in bug_data["bugs"]:
        try:
                #TODO: Make list safe
                bug_pattern = bug["pattern"].replace('*)?','*)')
                bug_regex = re.compile(bug_pattern)
                bug_dict[bug["name"]]=bug_regex
                i=i+1
        except Exception as ex:
                print 'Error trying to parse pattern: ' + str(bug["pattern"]) + 'for bug ' + bug["name"]
                print 'Exception: ' + str(ex)
print 'Dictionary of bug patterns built, contains ' + str(i) + ' bugs.'
print ''

print 'Preparing output file. Writing results to: ' + out_loc
try:
        bug_writer = open(out_loc, 'wb')
except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno,strerror)
except Exception as ex:
        print type(ex)
        print 'Unexcepted error: ' + str(ex)
        exit()
 
print 'Pre processing complete.'
print ''
 
print 'Beginning to parse URLs to identify bug patterns. Starting at URL' + str(start_url) + ' and stopping at URL ' + str(end_url)
b = 0
u = 0
e = 0
count=0
urls = end_url - start_url + 1
print 'Processing ' + str(urls) + ' urls'
url=''
fullurl = ''
headreg = re.compile("<head>.*</head>",re.IGNORECASE|re.MULTILINE|re.DOTALL)
start=time.clock()
for site in site_reader:
        try:              
                count=count+1 #pre increment - this is always hit
                if count < start_url:
                        continue
                
                if count > end_url:
                        print 'Last URL processed. Stopping...'               
                        break
 
                if count%10 == 0:
                        dur=time.clock()-start
                        print 'Processed ' +str(count-start_url)+ ' URLs. Time elapsed: ' + str(dur)
                        processed = count-start_url
                        if processed == 0:
                                processed = 1
                        print 'Est. time remaining for ' + str(urls) + ' URLs: ' + str(int(dur/(processed)*(urls-processed))) + 'secs'
               
                url=site[1]
                fullurl = 'http://www.'+url
                                       
                #Process site
                #print 'Processing URL ' + url
                
                usock = urllib2.urlopen(fullurl,None,5)
                data = usock.read()
                usock.close()

                       
                #Check for bugs
                for k,v in bug_dict.iteritems():
                        match = v.search(data)
                        if match != None:
                                print url+','+k
                                bug_writer.write(url+','+k+'\n')
                                b=b+1
                                           
                u=u+1 #post increment - only hit on success
                bug_writer.flush()
               
        except Exception as ex:
                print 'Error handling ' + fullurl + ': '
                print '         ' + str(ex)
                err_dict[url]=str(ex)
                e=e+1
        #print 'Finished processing URL ' + url
bug_writer.close()
print ''
print 'Completed parsing URLs in ' + str(time.clock()-start) +'s'
print 'Successfully handled ' + str(u) + ' URLs'
print 'Found a total of ' + str(b) + ' bugs.'
print ''
print 'Found ' + str(e) + ' error(s). Printing...'
for k,v in err_dict.iteritems():
        print 'URL: ' + k
        print 'Error: ' + v
print ''
print 'Processing complete'

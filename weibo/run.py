from scrapy import cmdline

cmdline.execute('scrapy crawl search-user -s JOBDIR=crawlsUser7/user7'.split())

# import time, subprocess, signal
#
# cmd = "scrapy crawl search -s JOBDIR=crawls/Feb"
# with open("output.txt", 'w') as ofile:
#     while True:
#         t_begin = time.time()
#         seconds_passed = 0
#         p = subprocess.Popen(cmd, shell=True, stdout=ofile, stderr=ofile)
#         seconds_passed = time.time() - t_begin
#         if seconds_passed >= 60:
#             p.send_signal(signal.SIGINT)
#             print("start to sleep...")
#             time.sleep(60)

# import subprocess
# import signal
#
# cmd = "scrapy crawl search -s JOBDIR=crawls/Feb"

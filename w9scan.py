#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: w8ay
# @Date:   2017年12月17日 19:21:35

import sys

sys.dont_write_bytecode = True  # 不生成pyc文件
try:
    __import__("lib.utils.versioncheck")  # this has to be the first non-standard import
except ImportError:
    exit("[!] wrong installation detected (missing modules). Please install python version for 2.7.x")

from lib.core.common import weAreFrozen
from lib.core.common import getUnicode
from lib.core.common import setPaths
from lib.core.common import makeurl
from lib.core.common import banner
from lib.core.common import Get_lineNumber_fileName
from lib.core.log import logger
import os
import inspect,time
from distutils.version import LooseVersion
from lib.core.settings import VERSION
from lib.core.settings import LIST_PLUGINS
from lib.core.data import urlconfig
from lib.core.exploit import Exploit_run
from lib.utils import crawler
from lib.core.common import createIssueForBlog
from lib.core.update import updateProgram
import argparse

def modulePath():
    """
    This will get us the program's directory, even if we are frozen
    using py2exe
    """

    try:
        _ = sys.executable if weAreFrozen() else __file__
    except NameError:
        _ = inspect.getsourcefile(modulePath)

    return getUnicode(os.path.dirname(os.path.realpath(_)), encoding=sys.getfilesystemencoding())

def checkEnvironment():
    try:
        os.path.isdir(modulePath())
    except UnicodeEncodeError:
        errMsg = "your system does not properly handle non-ASCII paths. "
        errMsg += "Please move the w9scan's directory to the other location"
        logger.critical(errMsg)
        raise SystemExit

    if LooseVersion(VERSION) < LooseVersion("1.0"):
        errMsg = "your runtime environment (e.g. PYTHONPATH) is "
        errMsg += "broken. Please make sure that you are not running "
        errMsg += "newer versions of w9scan with runtime scripts for older "
        errMsg += "versions"
        logger.critical(errMsg)
        raise SystemExit


def main():
    """
    Main function of w9scan when running from command line.
    """
    checkEnvironment() # 检测环境
    setPaths(modulePath()) # 为一些目录和文件设置了绝对路径
    banner()
    
    parser = argparse.ArgumentParser(description="w9scan scanner")
    parser.add_argument("--update", help="update w9scan",action="store_true")
    parser.add_argument("--guide", help="w9scan to guide",action="store_true")
    args = parser.parse_args()

    if args.update:
        updateProgram()
        return 0
    try:
        urlconfig.url = raw_input('[1] Input url > ')
        if urlconfig.url is '':
            logger.critical("[xxx] You have to enter the url")
            exit()

        urlconfig.url = makeurl(urlconfig.url)
        print '[***] ScanStart Target:%s' % urlconfig.url
        print("[Tips] You can select these plugins (%s) or select all"%(' '.join(LIST_PLUGINS)))
        diyPlugin = raw_input("[2] Please select the required plugins > ")

        if diyPlugin.lower() == 'all':
            urlconfig.diyPlugin = LIST_PLUGINS
        else:
            urlconfig.diyPlugin = diyPlugin.strip().split(' ')
        print "[***] You select the plugins:%s"%(' '.join(urlconfig.diyPlugin))    
        urlconfig.scanport = False
        if 'find_service' in urlconfig.diyPlugin:
            input_scanport = raw_input('[2.1] Need you scan all ports ?(Y/N) (default N)> ')
            if input_scanport.lower() in ("y","yes"):
                urlconfig.scanport = True
        
        urlconfig.threadNum = raw_input('[3] You need start number of thread (default 5) > ')
        if urlconfig.threadNum == '':
            urlconfig.threadNum = 5

        urlconfig.threadNum = int(urlconfig.threadNum)
        urlconfig.deepMax = raw_input('[4] Set the depth of the crawler (default 200 | 0 don\'t use crawler ) > ')
        if urlconfig.deepMax == '':
            urlconfig.deepMax = 200

        startTime = time.clock()
        e = Exploit_run(urlconfig.threadNum)
        e.load_modules("www",urlconfig.url)
        e.run()
        e.init_spider()
        s = crawler.SpiderMain(urlconfig.url)
        time.sleep(0.5)
        s.craw()
        endTime = time.clock()
        urlconfig.runningTime = endTime - startTime
        e.report()
        
    except KeyboardInterrupt:
        logger.critical("[***] User Interrupt")
        exit()
    except Exception as info:
        logger.critical("[xxx] MainError: %s:%s"%(str(Exception),info))
        data = e.buildHtml.getData()
        aax = "error:%s urlconfig:%s date:%s"%(str(Exception) + " " + str(info),str(urlconfig),data)
        createIssueForBlog(aax)
        exit()

if __name__ == '__main__':
    main()
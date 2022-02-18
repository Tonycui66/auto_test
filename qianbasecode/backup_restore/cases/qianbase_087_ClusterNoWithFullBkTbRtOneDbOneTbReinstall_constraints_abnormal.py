# -*- coding:utf8 -*-
#################################
# date        : 2021-11-12
# func        : backup and restore
# author      : caihailong
# copyright   : esgyn
# date file   : 当前路径下的/PrepareTheData/constraints.sql
# description : 集群级备份表级恢复，单database单table全量备份库表恢复无with skip_missing_foreign_keys参数，删除其中一张表恢复无with skip_missing_foreign_keys参数,涉及中英文参数和约束
#################################


import pytest
import time
import os
import sys
import re
#if not os.environ.get("typeinfo"):
#    os.environ["typeinfo"] = "backup_restore"
print(os.environ.get("typeinfo"))
try:
    curdir=os.getcwd()
    syspath = curdir
    if "qianbasecode" in curdir:
        syspath = curdir.split("qianbasecode")[0]
    os.chdir(syspath)
except Exception as e:
    print("修改工作到根路径失败:errmsg:%s"%e)
    sys.exit()

try:
    from factory.collect import write_logger
    from factory.backup_restore import ssh
    from factory.backup_restore import execsql
    from factory.conf import *
    from factory.backup_restore import backup_restore
except Exception as e:
    sys.path.append(syspath)
    from factory.collect import write_logger
    from factory.backup_restore import ssh
    from factory.backup_restore import execsql
    from factory.conf import *
    from factory.backup_restore import backup_restore

def case87_qianbase():
    try:
        basepath = os.getcwd()
        prepath = os.path.abspath(os.path.join(basepath, "qianbasecode/backup_restore/PrepareTheData/"))   
     
        #获取OneDatabaseOneTable.sql的数据文件
        sonpath = os.path.abspath(os.path.join(basepath, "qianbasecode/backup_restore/PrepareTheData/constraints.sql"))
        
        #获取配置文件的相应参数
        qianbase = backup_restore.Base_bk().returnpara()
        dbname = qianbase['dbname']
        user = qianbase['user']
        securepw = qianbase['securepw']
        password = qianbase['sshpassword']
        host = qianbase['host']
        dbport = qianbase['dbport']
        sshport = qianbase['sshport']
        bindir = qianbase['bindir']
        securemode = qianbase["securemode"]
        gm = qianbase['gm']
        nodeid = qianbase['nodeid']
        backdir = qianbase['backdir']

        if gm == 'gm':
            with_para_bk = "with gm_encryption"
            with_para_rt = "with gm_encryption"
        else:
            with_para_bk = ""
            with_para_rt = ""
        ssharg = [host, sshport,user, password]

        backup_restore.Base_bk().scp_file(sonpath,prepath) 
        #集群初始化
        backup_restore.instbk()

        #执行数据文件
        command,command2,d  = execsql.execdatafile(bindir,host,dbport,sonpath)
        ssh.myssh(command,ssharg)

        #获取其他信息
        # 和导入的OneDatabaseOneTable.sql文件第一行一致。
        newdb = d["newdb"]
        tabname = d['tabname']
        #进行备份
        bakcommand = "BACKUP INTO 'nodelocal://%s/%s'  %s;" % (nodeid, backdir,with_para_bk)
        ssh.myssh(execsql.execcmd(bakcommand,host,dbport),ssharg)
        #等待备份完成
        execsql.judgecmd("BACKUP",ssharg,3)

        #查备份文件
        backuppath,backfile = execsql.showbackupcmd(nodeid, backdir,ssharg)

        #获取所有nodeid ip
        ssh2 = ssh.myssh(command2,ssharg)
        
        backip,backdbport = execsql.nodeidip(ssh2,nodeid)
        storeinfo = execsql.querystore()
        newssharg = [backip, sshport, user, password]  
        
        #改表名
        renamecom= 'use %s;alter table %s rename to new%s ;' %(newdb,tabname,tabname)
        ssh.myssh(execsql.execcmd(renamecom,host,dbport),ssharg)
        
        #进行恢复
        backuppath = eval(backuppath)
        rescommand = "RESTORE table %s.%s FROM '%s%s' %s;" % (newdb,tabname,backuppath, backfile,with_para_rt)
        ret = ssh.myssh(execsql.execcmd(rescommand,host,dbport),ssharg,flag=1)
        
        write_logger(logfile).info('%s' %(ret))
        assert b'(or "skip_missing_foreign_keys" option)' in ret,'nopass'

        #检查状态是否正常
        execsql.checkstat(ssharg)

        #删除scp的文件目录(回退操作)
        backup_restore.Base_bk().rm_file()

    except Exception as e:
        #删除scp的文件目录(回退操作)
        backup_restore.Base_bk().rm_file()
        write_logger(logfile).error("--errmsg:%s" % e)
        sys.exit()


if __name__ == '__main__':
    case87_qianbase()



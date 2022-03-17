#!/usr/bin/python3
# coding=utf-8
import paramiko

hostip = '192.168.0.75'
user = 'root'
passwd = 'yzfar'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostip, 22, user, passwd)

def nodes(node):
    stdin,stdout, stderr= ssh.exec_command(node)
    result = stdout.readlines()
    for i in range(1,len(result)):
        for j in range(0,5):
            print(result[0].split()[j]+":"+result[i].split()[j])

node='kubectl top node --use-protocol-buffers'
nodes(node)

def pods(pod):
    stdin,stdout, stderr= ssh.exec_command(pod)
    result = stdout.readlines()
    for i in range(1,len(result)):
        for j in range(0,4):
            print(result[0].split()[j]+":"+result[i].split()[j])

pod='kubectl top pods --all-namespaces --use-protocol-buffers'
pods(pod)






ssh.close()
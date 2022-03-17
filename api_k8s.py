#!/usr/bin/python3
# coding=utf-8
import datetime
import math
import urllib3
import requests
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#k8s的api地址
url = "https://192.168.0.75:6443"

#k8s的token
token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjRZYnJtckRSbmhSNWRqNGN4YmhRUjMyeHU0aHdkQV83V2Q0UUtpRWlTc0EifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Inl6ZmFyYXBpLXRva2VuLWc2Njh4Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6Inl6ZmFyYXBpIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNTFjZmY4MTItZmI1YS00ODAwLWE2M2ItY2I4MGI2MDYwY2JkIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmRlZmF1bHQ6eXpmYXJhcGkifQ.iIAXmf8whJQmF4Wz6Ot5tLU7w-4k1JDQy3AaFMCR14VkT5SAwyAWI3No-TjlZoITa4vIfGUfO04Dv94kkNoZh1XkvFAFxuoN9J6KaI9gCCp0INzk_cauNmWClaF5rUtd-rztTEXuCvRUCBBqd2HpliefZuuHMpwBxp0p3R-Dw4RQaE0XImISmQjRZZShaGdcwBzIh5nGCN0U3K8gaeDzLroVR72mmV_-Mgnbs1n8JUY38DDTtiu_XPzPyAXIM9i2meA1ByX3lYi9AMNT1hASh3u_HVnr5ErASUMU30Cmg8giW30OFhUE7aucoIeXePOhwB7PHRD0-HPGEmSg8YDWbw"

def get_result(api_name):
    headers = {"Authorization":"Bearer "+token}
    json_data = requests.get(url+api_name,headers=headers,verify=False)
    return json_data.json()


#时间转换,把所有服务的创建时间变成运行时间
def Trantime(time_data):
    time = re.match(r"(\d+)-(\d+)-(\d+).*?(\d+):(\d+):(\d+)",time_data)
    total_send = round((datetime.datetime.now()-datetime.datetime(int(time.group(1)),int(time.group(2)),int(time.group(3)),int(time.group(4)),int(time.group(5)),int(time.group(6)))).total_seconds())
    return str(math.floor(total_send/86400)).split(".")[0]+"d"+str(math.floor((total_send%86400)/3600)).split(".")[0]+"h"

#把所有的单位转换成b
def Tranunit(unit_data):
    unit = re.match(r"(\d+)(.*)",unit_data)
    value = int(unit.group(1))
    if unit.group(2) == "K":
        return value*1000
    elif unit.group(2) == "Ki":
        return value*1024
    elif unit.group(2) == "M":
        return value*1000*1000
    elif unit.group(2) == "Mi":
        return value*1024*1024
    elif unit.group(2) == "G":
        return value*1000*1000*1000
    elif unit.group(2) == "Gi":
        return value*1024*1024*1024
    elif unit.group(2) == "n":
        return math.ceil(value/1000/1000)
    elif unit.group(2) == "m":
        return value
    else:
        return value

#获取所有k8s节点的信息
def get_node():
    print("获取所有k8s节点的信息")
    node_result = get_result("/api/v1/nodes")
    node_use_result = get_result("/apis/metrics.k8s.io/v1beta1/nodes")
    for j in node_use_result.get("items"):
        for i in node_result.get("items"):
            if i.get("metadata").get("name") == j.get("metadata").get("name"):
                data={"{#NAME}": i.get("metadata").get("name"),
                      "{#STATUS}": [i.get("status").get("conditions")[-1].get("type") if i.get("status").get("conditions")[-1].get("status") == "True" else "NotReady"],
                      "{#IP}": [i.get("status").get("addresses")[0].get("address")],
                      "{#KUBELET_VERSION}": [i.get("status").get("nodeInfo").get("kubeletVersion")],
                      "{#OS_IMAGE}": [i.get("status").get("nodeInfo").get("osImage")],
                      "{#CPU}": [str(i.get("status").get("capacity").get("cpu"))+"%"],
                      "{#MEMORY}": [str(int(Tranunit(i.get("status").get("capacity").get("memory"))/1000/1000/1000))+"核"],
                      "{#LIMIT_STORAGE}": [Tranunit(i.get("status").get("capacity").get("ephemeral-storage"))],
                      "{#RUNTIME}":[Trantime(i.get("metadata").get("creationTimestamp"))],
                      "{#USECPU}":[Tranunit(j.get("usage").get("cpu"))],
                      "{#USEMEMORY}":[Tranunit(j.get("usage").get("memory"))]
                      }
        print(data)


#获取k8s组件的健康信息
def get_health():
    print("获取k8s组件的健康信息")
    health_result = get_result("/api/v1/componentstatuses")
    for i in health_result.get("items"):
        data = {}
        data = {"{#NAME}": i.get("metadata").get("name"),
                "{#STATUS}": ["status",i.get("conditions")[0].get("type")],
                }
        print(data)


#获取k8s的所有namespaces 名称空间
def get_namespaces():
    print("获取k8s的所有名称空间")
    pod_result = get_result("/api/v1/namespaces")
    for i in pod_result.get("items"):
        data = {"#NAME":i.get("metadata").get("name"),
                "{#RUNTIME}":[Trantime(i.get("metadata").get("creationTimestamp"))]
                }
        print(data)


#获取k8s的所有pod
def get_pods():
    print("获取k8s的所有pod")
    pod_result = get_result("/api/v1/pods")
    for i in pod_result.get("items"):
        data = {"{#NAME}":i.get("metadata").get("name"),
                "{#RUNTIME}":["runtime",Trantime(i.get("metadata").get("creationTimestamp"))],
                "{#STATUS}":["status",i.get("status").get("phase")],
                "{#RESTARTCOUNT}":["restartcount",i.get("status").get("containerStatuses")[0].get("restartCount")]
                }
        print(data)


#获取k8s的所有pod的cpu和磁盘
def get_pod():
    print("获取k8s的所有pod的cpu和磁盘")
    pod_result = get_result("/api/v1/namespaces")
    for i in pod_result.get("items"):
        namespaces = i.get("metadata").get("name")
        pod_result = get_result("/apis/metrics.k8s.io/v1beta1/namespaces/"+namespaces+"/pods")
        for i in pod_result.get("items"):
            data = {"{#NAME}":i.get("metadata").get("name"),
                "{#CPU}":[Tranunit(i["containers"][0].get("usage").get("cpu"))],
                "{#memory}":[str(int(int(re.match(r"(\d+)(.*)",i["containers"][0].get("usage").get("memory")).group(1))/1024))+"Mi"],
                }
            print(data)


#获取所有k8s节点的信息
get_node()
#获取k8s组件的健康信息
get_health()
#获取k8s的所有namespaces 名称空间
get_namespaces()
#获取k8s的所有pod
get_pods()
#获取k8s的所有pod的cpu和磁盘
get_pod()
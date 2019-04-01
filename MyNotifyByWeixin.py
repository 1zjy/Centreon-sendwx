#!/usr/bin/env python
#coding:utf-8
import urllib2
import urllib
import json
from config import *
import pickle
import datetime,time
import argparse

###############MyNotifyByWeixin.py create by yl#######################

def url_request(url,values={},method='GET'):
    if method == 'GET':
        if len(values) != 0:
            url_values=urllib.urlencode(values)
            furl=url+'?'+url_values
        else:
            furl=url
        req=urllib2.Request(furl)
    elif method == 'POST':
        #data=urllib.urlencode(values)
        try:
            data=json.dumps(values,ensure_ascii=True)
        except:
            import sys
            sys_encoding=sys.stdin.encoding
            data=json.dumps(values,ensure_ascii=True,encoding=sys_encoding)
        
        req=urllib2.Request(url,data)
        req.add_header('Content-Type','application/json')
        req.get_method=lambda: 'POST'
    else:
        pass
    
    try:
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36')
        response = urllib2.urlopen(req)
        result=json.loads(response.read())
    except urllib2.URLError as e:
        if hasattr(e, 'code'):
            print 'Error code:',e.code
        elif hasattr(e, 'reason'):
            print 'Reason:',e.reason
        
        result={}
    except:
        result={}

    return result

def get_token():
    data_pkl='token_data.pkl'
    try:
        f=file(data_pkl,'rb')
        data_dict=pickle.load(f)
        f.close()
    except:
        data_dict={}
    try:
        expires_time=data_dict['expires_time']
    except:
        expires_time=0
    now_time=int(time.mktime(datetime.datetime.now().timetuple()))
    if now_time >= expires_time:
        url='https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values={
                'corpid':CorpID,
                'corpsecret':Secret,
                }
        result=url_request(url, values, method='GET')
        if len(result) != 0:
            now_time=int(time.mktime(datetime.datetime.now().timetuple()))
            expires_time=now_time+7200-10
            result['expires_time']=expires_time
            f=file(data_pkl,'wb')
            pickle.dump(result,f)
            f.close()
            access_token=result['access_token']
        else:
            print "Get token error,exit!"
            access_token=''
    else:
        access_token=data_dict['access_token']
    
    return access_token

#文本消息格式
def  text_type(notify_contact,AgentId,notify_content):
     values={
            "touser":notify_contact,
            #"toparty":ToParty,
            "msgtype": "text",
            "agentid": AgentId,
            "text": {
                   "content": notify_content
            },
            "safe": 0 
     }
     return values

#textcard消息格式
def textcard_type(notify_contact,AgentId,notify_describe):
    values={
           "touser":notify_contact,
           "msgtype" : "textcard",
           "agentid": AgentId,
	   "textcard" : {
                  "title": "告警通知", 
                  "description": notify_describe,
		  "url" : "无",
		  "btntxt": ""
           }
     }
    return values

#图文消息格式
def  mpnews_type(notify_contact,AgentId,jk_qy,host_name,ywmc,service_desc,host_address,service_infokey,notify_content,notify_describe):
     img_media_id="xxxxxxxxxxx"
     imageid='xxxxxxxxxxxxxxxxxxxxxx'
     values={
            "touser":notify_contact,
            "msgtype" : "mpnews",
            "agentid": AgentId,
            "mpnews" : {
            "articles":[
               {
                   "title": ywmc, 
                   "thumb_media_id": imageid,
                   "author": "",
                   "content_source_url": "",
                   "content": "暂无",
                   "digest": ""
                },
               {
                   "title": key_nr, 
                   "thumb_media_id": img_media_id,
                   "author": jk_qy,
                   "content_source_url": "",
                   "content": notify_content,
                   "digest": ""
                }
             ]
           },
	   "safe":1
            }
     return values

def send_wxmessage(token,content):
    url='https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token='+token+'&debug='+str(DEBUG)
    content_data=content.split('-@@-')
    notify_type=content_data[0]
    #fs_time=str(datetime.datetime.now()).split('.')[0]
    if notify_type == 'host':
        type1=content_data[1]
        jk_qy=content_data[2]
        host_name=content_data[3]
        host_state=content_data[4]
        host_address=content_data[5]
        fs_time=content_data[6]
	    host_info=content_data[7]
        notify_contact=content_data[8]
        notify_content="告警通知\n\n通知类型: "+ type1 + \
		                "\n监控区域: "  + jk_qy  + \
                        "\n主机名称: " + host_name + \
                        "\n主机状态: " + host_state + \
                        "\nIP  地址: " + host_address + \
                        "\n触发时间: " + fs_time  + \
                        "\n告警内容: " + host_info + "\n"
        notify_describe="主机名: " + host_name + \
                        "\n触发时间: " + fs_time  + \
                        "\n告警内容: " + host_info
    elif notify_type == 'service':
        xxid=content_data[1]
        type1=content_data[2]
        jk_qy=content_data[3]
        service_desc=content_data[4]
        host_name=content_data[5]
        ywlxmc=content_data[6]
        ywmc=content_data[7]
        host_address=content_data[8]
        service_state=content_data[9]
        service_info=content_data[11]
        cfsj_time=content_data[12]
        notify_contact=content_data[13]
        sendtype=content_data[14]
        if sendtype=='2' or sendtype=='3':
            notify_content="告警通知\n\n监控区域:"  + jk_qy  + \
                           "\n信息编号:" + xxid + \
                           "\n监控主机名:" + host_name + \
                           "\n服务器IP:" + host_address + \
                           "\n监控服务名:" + service_desc + \
                           "\n业务大类:" + ywlxmc + \
                           "\n业务名称:" + ywmc + \
                           "\n服务状态:" + service_state + \
                           "\n告警触发时间:" + cfsj_time  + \
                           "\n告警内容:" + service_info + "\n" 
        
        notify_describe="业务名称: " + ywmc + \
                        "\n主机名: " + host_name + \
		                "\n服务名: " + service_desc + \
		                "\nIP地址: " + host_address + \
                        "\n触发时间: " + cfsj_time  + \
                        "\n告警内容: " + desc_info
    else:
        notify_content="Get Centreon message notify info error.\n\nContent: %s" % content
        notify_contact=ToUser
    if  sendtype =='1':
        values=mpnews_type(notify_contact,AgentId,jk_qy,host_name,ywmc,service_desc,host_address,service_infokey,notify_content,notify_describe)
    elif sendtype =='2':
         values=textcard_type(notify_contact,AgentId,notify_describe)
    elif sendtype =='3':
         values= text_type(notify_contact,AgentId,notify_content)
    else:
         values=mpnews_type(notify_contact,AgentId,jk_qy,host_name,ywmc,service_desc,host_address,service_infokey,notify_content,notify_describe)
    return url_request(url, values, method='POST')

def main():
    token=get_token()
    parser=argparse.ArgumentParser(description="Centreon weixin notify by yl")
    parser.add_argument("content",default=None,help="notify content,split with -@@-")
    args = parser.parse_args()
    content=args.content
    send_wxmessage(token, content)
    
if __name__ == "__main__":
    main()




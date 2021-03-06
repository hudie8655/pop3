import poplib
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import json
import re
import pickle

import io
import sys

from testOfflineDB import News
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') #改变标准输出的默认编码

def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

def print_info(msg, indent=0):
    if indent == 0:
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header=='Subject':
                    value = decode_str(value)
                else:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
            print('%s%s: %s' % ('  ' * indent, header, value))
    if (msg.is_multipart()):
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            print('%spart %s' % ('  ' * indent, n))
            print('%s--------------------' % ('  ' * indent))
            print_info(part, indent + 1)
    else:
        content_type = msg.get_content_type()
        if content_type=='text/plain' or content_type=='text/html':
            content = msg.get_payload(decode=True)
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
            print('%sText: %s' % ('  ' * indent, content + '...'))
        else:
            print('%sAttachment: %s' % ('  ' * indent, content_type))
			
if __name__=='__main__':

	# 输入邮件地址, 口令和POP3服务器地址:
	email = 'rmrb321@yeah.net'
	password = 'rmrb321'
	pop3_server = 'pop.yeah.net'

	# 连接到POP3服务器:
	server = poplib.POP3(pop3_server)
	# 可以打开或关闭调试信息:
	server.set_debuglevel(1)
	# 可选:打印POP3服务器的欢迎文字:
	print(server.getwelcome().decode('utf-8'))

	# 身份认证:
	server.user(email)
	server.pass_(password)

	# stat()返回邮件数量和占用空间:
	print('Messages: %s. Size: %s' % server.stat())
	# list()返回所有邮件的编号:
	resp, mails, octets = server.list()
	# 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
	print(mails)

	# 获取最新一封邮件, 注意索引号从1开始:
	index = len(mails)
	received_title=set()
	with open('data.bin', 'wb') as f:
		for i in range(1,index+1):
			resp, lines, octets = server.retr(i)

			# lines存储了邮件的原始文本的每一行,
			# 可以获得整个邮件的原始文本:
			msg_content = b'\r\n'.join(lines).decode('utf-8')
			# 稍后解析出邮件:
			msg = Parser().parsestr(msg_content)
			#print_info(msg)

			subject = msg.get( 'Subject','')#.decode('utf-8')
			#判断是否是需要的邮件，是否已经收取过
			patten = re.compile(r'\d{4}-\d{2}/\d{2}')
			if re.match(patten,subject):
				if subject not in received_title:
					content = msg.get_payload(decode=True)
                    #TODO: 这里解码出错会崩溃，比如错误的邮件，以后处理
					content = content.decode('utf-8')

					for js in content.split('###'):
						d=json.loads(js)
						news = News(d['title'], d['content'], '人民日报', d['date'], d['ban'])
						pickle.dump(news, f, True)
					received_title.add(subject)
			# 可以根据邮件索引号直接从服务器删除邮件:
			# server.dele(index)
			# 关闭连接:
	server.quit()
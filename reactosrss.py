import requests, html
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
        
def findall_between(s, first, last):
    try:
        while True:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            yield s[start:end]
            s = s[end:]
    except ValueError:
        yield ""
        
def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

class ReactosRss:
    @staticmethod
    def get(count = 20):
        url = 'https://jira.reactos.org/sr/jira.issueviews:searchrequest-rss/temp/SearchRequest.xml?jqlQuery=statusCategory+%3D+Done+order+by+updated+DESC&tempMax={0}'.format(count)
        res = requests.get(url)
        text = res.text
        res.close()
        text = (html.unescape(text)).replace('&#39;', "'")
        
        res = []
        for item in findall_between(text, '<item>', '</item>'):
            if item == '':
                break
            title = find_between(item, "<title>", "</title>").strip()
            link = find_between(item, "<link>", "</link>").strip()
            pubDate = find_between(item, "<pubDate>", "</pubDate>").strip()
            status = find_between(item, 'Resolution', ' </table>')
            status = find_between(status, '<td bgcolor="#ffffff" valign="top" width="30%" nowrap>', '</td>').strip()
            assigneeNode = find_between(item, "Assignee", "</tr>")
            assignee = find_between(assigneeNode, '">', "<").strip()
            assigneeLink = find_between(assigneeNode, 'href="', '"').strip()
            fixversion = find_between(item, '<td><b>Fix Version/s:</b></td>', '</table>')
            fixversion = find_between(fixversion, '<a title="', '"').strip()
            headers= {'X-Requested-With':'XMLHttpRequest', 'X-PJAX':'true', 'X-AUSERNAME':''}
            historynodesres = requests.get('{0}?page=com.atlassian.jira.plugin.system.issuetabpanels:changehistory-tabpanel'.format(link), headers=headers)
            historynodes = historynodesres.text
            issue_data_block = find_between_r(historynodes, '"issue-data-block"', '</div>')
            usernode = find_between(issue_data_block, '<a class="user', '/a>')
            resolver = find_between(usernode, '</span></span>', '<').strip()
            resolverlink = 'https://jira.reactos.org/{0}'.format(find_between(usernode, 'href="', '"'))
            
            
            res.append( 
                {
                    'title':title,
                    'link':link,
                    'status':status,
                    'assigneeLink':assigneeLink,
                    'assignee':assignee,
                    'pubDate':pubDate,
                    'fixversion':fixversion,
                    'resolver':resolver,
                    'resolverlink':resolverlink
                }
                )
        return res
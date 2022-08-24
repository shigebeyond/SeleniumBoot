from lxml import etree

# lxml.etree.HTML()，lxml.etree.fromstring()和lxml.etree.tostring()三者的区别与联系:  https://www.cnblogs.com/lincappu/p/12888183.html

# xpath demo: https://www.cnblogs.com/superhin/p/16121279.html
html = '''
<div id="content">
    <ul>
        <li id="top_001" class="item">肖申克的救赎<li>
        <li id="top_001" class="item">霸王别姬</li>
        <li id="top_002" class="item">阿甘正传</li>
    </ul>
    <a href='https://baidu.com'>百度</a>
</div>
'''
root = etree.HTML(html)
def test_xpath(path):
    nodes = root.xpath(path)
    node = nodes[0]
    print(node.text)
    return node

def test_css(path):
    nodes = root.cssselect(path)
    node = nodes[0]
    print(node.text)
    return node

'''
test_xpath('/html/body/div') # 绝对路径查找
test_xpath('//ul/li[2]') # 相对路径，结合索引
test_xpath('//div[@id="content"]') # 结合属性查找
test_xpath('//li[@id="top_001" and @class="item"]') # 多条件查找
test_xpath('//li[text()="阿甘正传"]') # 使用text()函数根据元素文本查找
test_xpath('//li[contains(text(), "阿甘")]') # 使用contains函数查找文本包含
test_xpath('//li[1]/following-sibling::li') # 使用XPath的轴方法获取后面所有的同级元素
'''

node = test_css('a')
# 报错：Pseudo-elements are not supported. 不支持伪元素
if isinstance(node, etree._Element):
    print('类型match')
attr = node.cssselect('::attr(href)')
test_css('a::attr(href)')
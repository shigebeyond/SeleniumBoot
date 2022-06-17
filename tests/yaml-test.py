import yaml
# yaml原生的语法中不支持配置与引用变量
txt = '''
default-db:
  port: 3306
user-db:
  port: ${default-db.port}
'''
data = yaml.load(txt, Loader=yaml.FullLoader)
print(data)
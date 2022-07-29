[GitHub](https://github.com/shigebeyond/SeleniumBoot) | [Gitee](https://gitee.com/shigebeyond/SeleniumBoot)

# SeleniumBoot - yaml驱动Selenium测试

## 概述
Selenium是基于浏览器的自动化测试工具，但是要写python代码；

考虑到部分测试伙伴python能力不足，因此扩展Selenium，支持通过yaml配置测试步骤;

框架通过编写简单的yaml, 就可以执行一系列复杂的浏览器操作步骤, 如填充表单/提交表单/上传文件/下载文件/识别验证码/校验响应/提取变量/打印变量等，极大的简化了伙伴编写自动化测试脚本的工作量与工作难度，大幅提高人效；

框架通过提供类似python`for`/`if`/`break`语义的步骤动作，赋予伙伴极大的开发能力与灵活性，能适用于广泛的测试场景。

框架提供`include`机制，用来加载并执行其他的步骤yaml，一方面是功能解耦，方便分工，一方面是功能复用，提高效率与质量，从而推进测试整体的工程化。

## 特性
1. 基于 selenium 的webdriver
2. 使用 selenium-requests 扩展来处理post请求与上传请求
3. 支持通过yaml来配置执行的步骤，简化了自动化测试开发:
每个步骤可以有多个动作，但单个步骤中动作名不能相同（yaml语法要求）;
动作代表webdriver上的一种操作，如goto/get/post/upload/submit_form等等;
4. 支持提取器
5. 支持校验器
6. 支持识别验证码(使用有道ocr)
7. 支持类似python`for`/`if`/`break`语义的步骤动作，灵活适应各种场景
8. 支持`include`引用其他的yaml配置文件，以便解耦与复用

## todo
1. 支持更多的动作

## 安装
```
pip3 install SeleniumBoot
```

安装后会生成命令`SeleniumBoot`;

注： 对于深度deepin-linux系统，生成的命令放在目录`~/.local/bin`，建议将该目录添加到环境变量`PATH`中，如
```
export PATH="$PATH:/home/shi/.local/bin"
```

## 使用
```
# 1 执行单个文件
SeleniumBoot 步骤配置文件.yml

# 2 执行多个文件
SeleniumBoot 步骤配置文件1.yml 步骤配置文件2.yml ...

# 3 执行单个目录, 即执行该目录下所有的yml文件
SeleniumBoot 步骤配置目录

# 4 执行单个目录下的指定模式的文件
SeleniumBoot 步骤配置目录/step-*.yml
```

如执行 `SeleniumBoot example/step-mn52.yml`，输出如下
```
加载并执行步骤文件: /ohome/shi/code/python/SeleniumBoot/example/step-mn52.yml
处理动作: goto={'url': 'https://www.mn52.com/'}
处理动作: download_img_elements_by={'xpath': '//img[@class="img-responsive"]'}
下载文件: url为https://www.mn52.com/img/allimg/2021-04-27/0a3abe80-4616-4740-9968-8d961fe1ab7c_5f9f95f226fb2.jpg, 另存为/ohome/shi/code/python/SeleniumBoot/downloads/0a3abe80-4616-4740-9968-8d961fe1ab7c_5ffb2.jpg
下载文件: url为https://www.mn52.com/img/allimg/2021-04-27/11cc4156-6e93-4526-9d0d-d911df8d8492_5fa0e85d40cfa.jpg, 另存为/ohome/shi/code/python/SeleniumBoot/downloads/11cc4156-6e93-4526-9d0d-d911df8d8492_5fcfa.jpg
下载文件: url为https://www.mn52.com/img/allimg/2021-04-27/213fbbec-22f2-4ae4-9f90-15126d980d56_5f895f29a9d5a.jpg, 另存为/ohome/shi/code/python/SeleniumBoot/downloads/213fbbec-22f2-4ae4-9f90-15126d980d56_5fd5a.jpg
......
```
命令会自动打开浏览器，自动跳转，自动下载图片

## 步骤配置文件及demo
用于指定多个步骤, 示例见源码 [example](https://github.com/shigebeyond/SeleniumBoot/tree/main/example) 目录下的文件;

顶级的元素是步骤;

每个步骤里有多个动作(如goto/sleep/submit_form)，如果动作有重名，就另外新开一个步骤写动作，这是由yaml语法限制导致的，但不影响步骤执行。

简单贴出2个demo
1. 下载图片: 详见 [example/step-mn52.yml](https://github.com/shigebeyond/SeleniumBoot/blob/main/example/step-mn52.yml)
```yaml
# 下载美女图
- # 首页
  goto:
    url: https://www.mn52.com/
  # 下载多个图片
  download_img_elements_by:
    xpath: '//img[@class="img-responsive"]'
    save_dir: downloads
```

2. 内部项目测试: 详见 [example/step-jym.yml](https://github.com/shigebeyond/SeleniumBoot/blob/main/example/step-jym.yml)
```yaml
- # 登录
  goto:
    url: http://admin.jym1.com/login
  sleep: 5 # 人工介入，浏览器F12打开开发者模式，切network，打开Preserve log，来监听提交登录验证的请求，以便检查识别的验证码参数是否有问题
  # 识别验证码, 验证码会写到变量captcha
  recognize_captcha:
    url: http://admin.jym1.com/login/verify_image
  # 提交表单
  submit_form:
    account: '18877310999'
    passwd: '123456'
    verify_text: $captcha # 验证码
- # 商品列表
  goto:
    url: http://admin.jym1.com/goods/goods_service_list
    # 网页中html的提取变量
    extract_by_xpath:
      goods_id: //table/tbody/tr[1]/td[1] # 第一行第一列
  #  extract_by_css:
  #    goods_id: table>tbody>tr:nth-child(1)>td:nth-child(1) # 第一行第一列
- # 商品详情
  goto:
    url: http://admin.jym1.com/goods/goods_info?id=$goods_id&type=1
  download_img_element_by:
    xpath: //img[@class="layui-upload-img"] # 过滤<img>标签的xpath路径， 与css属性只能二选一
    #css: img.layui-upload-img # 过滤<img>标签的css selector模式， 与xpath属性只能二选一
- # 新建门店
  goto:
    url: http://admin.jym1.com/store/add_store
  upload: # 上传文件/图片
    url: http://admin.jym1.com/upload/common_upload_img/store_img
    files: # 上传的多个文件
      # 参数名:文件本地路径
      file: /home/shi/fruit.jpeg
    extract_by_jsonpath:
      img: $.data.url
  # 提交新建门店，不要用 submit_form，ui中太麻烦了太复杂了（如三级地址要逐级动态加载）
  post:
    url: http://admin.jym1.com/store/add_store
    is_ajax: true
    data: # post的参数
      # 参数名:参数值
      store_name: teststore-${random_str(6)}
      store_logo_url: '$img'
      store_img_urls: '["$img"]'
      province: 450000
      city: 450100
      district: 450102
      address: testadd
      phone: 1347115${random_int(4)}
      business_day_from: 1
      business_day_to: 1
      work_start_time: 09:00:00 - 20:00:00
      store_type: 0
      licence_url: '$img'
      license_code: 91450100788439413D
      card_true_name: shi
      bank_name: 中国工商银行
      bank_card_num: 6222024100018669328
      store_work_time: '["{\"date_from\":\"1\",\"date_to\":\"1\",\"work_start_time\":\"09:00:00\",\"work_end_time\":\"20:00:00\"}"]'
- # 门店列表,查看新建门店
  goto:
    url: http://admin.jym1.com/store/store_list
  sleep: 2
```

## 配置详解
支持通过yaml来配置执行的步骤;

每个步骤可以有多个动作，但单个步骤中动作名不能相同（yaml语法要求）;

动作代表webdriver上的一种操作，如goto/get/post/upload/submit_form等等;

下面详细介绍每个动作:

1. sleep: 线程睡眠; 
```yaml
sleep: 2 # 线程睡眠2秒
```

2. print: 打印, 支持输出变量/函数; 
```yaml
# 调试打印
print: "总申请数=${dyn_data.total_apply}, 剩余份数=${dyn_data.quantity_remain}"
```

变量格式:
```
$msg 一级变量, 以$为前缀
${data.msg} 多级变量, 用 ${ 与 } 包含
```

函数格式:
```
${random_str(6)} 支持调用函数，目前仅支持3个函数: random_str/random_int/incr
```

函数罗列:
```
random_str(n): 随机字符串，参数n是字符个数
random_int(n): 随机数字，参数n是数字个数
incr(key): 自增值，从1开始，参数key表示不同的自增值，不同key会独立自增
```

3. base_url: 设置基础url
```yaml
base_url: https://www.taobao.com/
```

4. goto: 浏览器跳转; 
```yaml
goto:
    url: http://admin.jym1.com/goods/goods_service_list # url,支持写变量
    extract_by_xpath: # 网页中html的提取变量
      goods_id: //table/tbody/tr[1]/td[1] # 第一行第一列
```

5. get: 发get请求, 但无跳转; 
```yaml
get:
    url: $dyn_data_url # url,支持写变量
    extract_by_eval:
      dyn_data: "json.loads(response.text[16:-1])" # 变量response是响应对象
```

6. post: 发post请求, 但无跳转; 
```yaml
post:
    url: http://admin.jym1.com/store/add_store # url,支持写变量
    is_ajax: true
    data: # post的参数
      # 参数名:参数值
      store_name: teststore-${random_str(6)}
      store_logo_url: '$img'
```

7. upload: 上传文件; 
```yaml
upload: # 上传文件/图片
    url: http://admin.jym1.com/upload/common_upload_img/store_img
    files: # 上传的多个文件
      # 参数名:文件本地路径
      file: /home/shi/fruit.jpeg
    extract_by_jsonpath:
      img: $.data.url
```

8. submit_form: 提交表单; 
是 `input_by_name` 与 `click_by({'css':'[type=submit]'})` 的结合
```yaml
submit_form:
  # 输入框name: 填充的值(支持写变量)
  account: '18877310999'
  passwd: '123456'
```

9. input_by_name: 填充 name 指定的输入框; 
```yaml
input_by_name:
  # 输入框name: 填充的值(支持写变量)
  account: '18877310999'
```

10. input_by_css: 填充 css selector 指定的输入框; 
```yaml
input_by_css:
  # 输入框css selector模式: 填充的值(支持写变量)
  '#account': '18877310999'
```

11. input_by_xpath: 填充 xpath 指定的输入框; 
```yaml
input_by_xpath:
  # 输入框xpath路径: 填充的值(支持写变量)
  "//input[@id='account']": '18877310999'
```

12. download: 下载文件; 
变量`download_file`记录最新下载的单个文件
```yaml
download:
    url: https://img.alicdn.com/tfscom/TB1t84NPuL2gK0jSZPhXXahvXXa.jpg_q90.jpg
    save_dir: downloads # 保存的目录，默认为 downloads
    save_file: test.jpg # 保存的文件名，默认为url中最后一级的文件名
```

13. download_img_element_by: 下载单个`<img>`标签中加载的图片; 
变量`download_file`记录最新下载的单个图片
```yaml
download_img_element_by:
    xpath: //img[@class="pro-img"] # 过滤<img>标签的xpath路径，与css属性只能二选一
    #css: img.pro-img # 过滤<img>标签的css selector模式，与xpath属性只能二选一
    save_dir: downloads # 保存的目录，默认为 downloads
    #save_file: test.jpg # 保存的文件名，默认为url中最后一级的文件名
```

14. download_img_elements_by: 下载多个`<img>`标签中加载的图片; 
变量`download_files`记录最新下载的多个图片
```yaml
download_img_elements_by:
    xpath: '//a[@class="pic J_ImgLoad"]/img'
    save_dir: downloads
```

15. recognize_captcha: 识别验证码; 
参数同 `download` 动作， 因为内部就是调用 `download`;
而变量`captcha`记录识别出来的验证码
```
recognize_captcha:
    url: http://admin.jym1.com/login/verify_image
    # save_dir: downloads # 保存的目录，默认为 downloads
    # save_file: test.jpg # 保存的文件名，默认为url中最后一级的文件名
```

16. recognize_captcha_element: 识别验证码标签中的验证码; 
参数同 `download_img_element_by` 动作， 因为内部就是调用 `download_img_element_by`;
而变量`captcha`记录识别出来的验证码
```
recognize_captcha_element:
    xpath: //img[@class="pro-img"] # 过滤<img>标签的xpath路径， 与css属性只能二选一
    #css: img.pro-img # 过滤<img>标签的css selector模式， 与xpath属性只能二选一
    #save_dir: downloads # 保存的目录，默认为 downloads
    #save_file: test.jpg # 保存的文件名，默认为url中最后一级的文件名
```

17. click_by/click_by_if_exist: 点击指定的元素; 
```yaml
click_by:
  css: 'button[type=submit]' # 元素的css selector模式，与xpath属性只能二选一
  #xpath: '//button[@type="submit"]' # 元素的xpath路径，与css属性只能二选一
```
如果点击之前要先判断元素是否存在，则换用 click_by_if_exist

18. right_click_by: 右击指定的元素; 
```yaml
right_click_by:
  css: 'button[type=submit]' # 元素的css selector模式，与xpath属性只能二选一
  #xpath: '//button[@type="submit"]' # 元素的xpath路径，与css属性只能二选一
```

19. double_click_by: 双击指定的元素; 
```yaml
double_click_by:
  css: 'button[type=submit]' # 元素的css selector模式，与xpath属性只能二选一
  #xpath: '//button[@type="submit"]' # 元素的xpath路径，与css属性只能二选一
```

20. alert_accept: 点击弹框的确定按钮; 
```yaml
alert_accept: 
```

21. alert_dismiss: 取消弹框; 
```yaml
alert_dismiss: 
```

22. max_window: 最大化窗口; 
```yaml
max_window: 
```

23. resize_window: 调整窗口大小; 
```yaml
resize_window: 100,200 # 宽,高
```

24. switch_to_frame_by: 切换进入iframe; 
```yaml
switch_to_frame_by:
  css: 'iframe#main' # iframe的css selector模式，与xpath属性只能二选一
  #xpath: '//iframe[@id="main"]' # iframe的xpath路径，与css属性只能二选一
```

25. switch_to_frame_out: 跳回到主框架页; 
```yaml
switch_to_frame_out: 
```

26. switch_to_window: 切到第几个窗口; 
```yaml
switch_to_window: 1 # 切到第1个窗口
```

27. screenshot: 整个窗口截图存为png; 
```yaml
screenshot:
    save_dir: downloads # 保存的目录，默认为 downloads
    save_file: test.png # 保存的文件名，默认为:时间戳.png
```

28. screenshot_element_by: 对某个标签截图存为png; 
```yaml
screenshot_element_by
    css: 'iframe#main' # iframe的css selector模式，与xpath属性只能二选一
    #xpath: '//iframe[id="main"]' # iframe的xpath路径，与css属性只能二选一
    save_dir: downloads # 保存的目录，默认为 downloads
    save_file: test.png # 保存的文件名，默认为:时间戳.png
```

29. execute_js: 执行js; 
```yaml
execute_js: alert('hello world')
```

30. scroll: 滚动到指定位置; 
```yaml
scroll: 100,200
```

31. scroll_top: 滚动到顶部; 
```yaml
scroll_top: 
```

32. scroll_bottom: 滚动到底部; 
```yaml
scroll_bottom: 
```

33. scroll_to_by: 滚动到指定元素; 
```yaml
scroll_to_by: 
    css: 'button[type=submit]'
```

34. move_to_by: 鼠标移动到指定元素; 
```yaml
move_to_by: 
    css: 'button[type=submit]'
```

35. refresh: 刷新网页; 
```yaml
refresh: 
```

36. forward: 前进; 
```yaml
forward: 
```

37. back: 后退; 
```yaml
back: 
```

38. select_all_by: 全选 ctrl + a
```
select_all_by:
    css: '#name'
```
    
39. copy_by: 复制 ctrl + c
```
copy_by:
    css: '#name'
```
    
40. clip_by: 剪切 ctrl + x
```
clip_by:
    css: '#name'
```
    
41. paste_by: 粘贴 ctrl + v
```
paste_by:
    css: '#name'
```

42. for: 循环; 
for动作下包含一系列子步骤，表示循环执行这系列子步骤；变量`for_i`记录是第几次迭代（从1开始）
```yaml
# 循环3次
for(3) :
  # 每次迭代要执行的子步骤
  - scroll_bottom:
    sleep: 2

# 无限循环，直到遇到跳出动作
# 有变量for_i记录是第几次迭代（从1开始）
for:
  # 每次迭代要执行的子步骤
  - break_if: for_i>2 # 满足条件则跳出循环
    scroll_bottom:
    sleep: 2
```

43. once: 只执行一次，等价于 `for(1)`; 
once 结合 moveon_if，可以模拟 python 的 `if` 语法效果
```yaml
once:
  # 每次迭代要执行的子步骤
  - moveon_if: for_i<=2 # 满足条件则往下走，否则跳出循环
    scroll_bottom:
    sleep: 2
```

44. break_if: 满足条件则跳出循环; 
只能定义在for循环的子步骤中
```yaml
break_if: for_i>2 # 条件表达式，python语法
```

45. moveon_if: 满足条件则往下走，否则跳出循环; 
只能定义在for循环的子步骤中
```yaml
moveon_if: for_i<=2 # 条件表达式，python语法
```

46. moveon_if_exist_by: 如果检查元素存在 则往下走，否则跳出循环; 
只能定义在for循环的子步骤中
```yaml
moveon_if_exist_by:
    css: 'button[type=submit]'
```

47. include: 包含其他步骤文件，如记录公共的步骤，或记录配置数据(如用户名密码); 
```yaml
include: part-common.yml
```

48. set_vars: 设置变量; 
```yaml
set_vars:
  name: shi
  password: 123456
  birthday: 5-27
```

49. print_vars: 打印所有变量; 
```yaml
print_vars:
```

50. base_url: 设置基础url
```yaml
base_url: https://www.taobao.com/
```

## 校验器
主要是为了校验页面或响应的内容, 根据不同场景有2种写法
```
1. 针对当前页面, 那么校验器作为普通动作来写
2. 针对 goto/get/post/upload 有发送http请求的动作, 那么校验器在动作内作为普通属性来写
```

1. validate_by_xpath: 
从html的响应中校验 xpath 路径对应的元素的值
```yaml
validate_by_xpath:
  "//div[@id='goods_id']": # 元素的xpath路径
    '>': 0 # 校验符号或函数: 校验的值, 即 id 元素的值>0
  "//div[@id='goods_title']":
    contains: 衬衫 # 即 title 元素的值包含'衬衫'
```

2. validate_by_css: 
从html的响应中校验 css selector 模式对应的元素的值
```yaml
validate_by_css:
  '#id': # 元素的css selector 模式
    '>': 0 # 校验符号或函数: 校验的值, 即 id 元素的值>0
  '#goods_title':
    contains: 衬衫 # 即 title 元素的值包含'衬衫'
```

3. validate_by_jsonpath: 
从json响应中校验 多层属性 的值
```yaml
validate_by_jsonpath:
  '$.data.goods_id':
     '>': 0 # 校验符号或函数: 校验的值, 即 id 元素的值>0
  '$.data.goods_title':
    contains: 衬衫 # 即 title 元素的值包含'衬衫'
```

#### 校验符号或函数
1. `=`: 相同
2. `>`: 大于
3. `<`: 小于
4. `>=`: 大于等于
5. `<=`: 小于等于
6. `contains`: 包含子串
7. `startswith`: 以子串开头
8. `endswith`: 以子串结尾
9. `regex_match`: 正则匹配

## 提取器
主要是为了从页面或响应中提取变量, 根据不同场景有2种写法
```
1. 针对当前页面, 那么提取器作为普通动作来写
2. 针对 goto/get/post/upload 有发送http请求的动作, 那么提取器在动作内作为普通属性来写
```

1. extract_by_xpath:
从html的响应中解析 xpath 路径指定的元素的值
```yaml
extract_by_xpath:
  # 变量名: xpath路径
  goods_id: //table/tbody/tr[1]/td[1] # 第一行第一列
```

2. extract_by_css:
从html的响应中解析 css selector 模式指定的元素的值
```yaml
extract_by_css:
  # 变量名: css selector 模式
  goods_id: table>tbody>tr:nth-child(1)>td:nth-child(1) # 第一行第一列
```

3. extract_by_jsonpath:
从json响应中解析 多层属性 的值
```yaml
extract_by_jsonpath:
  # 变量名: json响应的多层属性
  img: $.data.url
```

4. extract_by_eval:
使用 `eval(表达式)` 执行表达式, 并将执行结果记录到变量中
```yaml
extract_by_eval:
    # 变量名: 表达式（python语法）
    dyn_data: "json.loads(response.text[16:-1])" # 变量response是响应对象
```
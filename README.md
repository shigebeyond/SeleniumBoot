# SeleniumRunner - yaml驱动Selenium测试

## 概述
Selenium是基于浏览器的自动化测试工具，但是要写python代码；
考虑到部分测试伙伴python能力不足，因此扩展Selenium，支持通过yaml配置测试步骤

## 特性
1. 基于 selenium 的webdriver
2. 使用 selenium-requests 扩展来处理post请求与上传请求
3. 支持通过yaml来配置执行的步骤
每个步骤可以有多个动作，但单个步骤中动作名不能相同（yaml语法要求）
动作代表webdriver上的一种操作，如get/post/upload/submit_form等等
4. 支持提取器

## todo
1. 支持外部指定配置文件
2. 支持校验器
3. 支持更多的动作

## 安装依赖
```
pip3 install -r requirements.txt
```

## 配置文件
用于指定步骤, 如 step.yml
```
- # 登录
  get: http://admin.jym1.com/login
  submit_form:
    account: '18877310999'
    passwd: '123456'
- # 商品列表
  get: http://admin.jym1.com/goods/goods_service_list
  # 网页中html的提取变量
  extract_by_xpath:
    goods_id: //table/tbody/tr[1]/td[1] # 第一行第一列
#  extract_by_css:
#    goods_id: table>tbody>tr:nth-child(1)>td:nth-child(1) # 第一行第一列
- # 商品详情
  get: http://admin.jym1.com/goods/goods_info?id=$goods_id&type=2
- # 新建门店
  get: http://admin.jym1.com/store/add_store
  upload: # 上传图片
    url: http://admin.jym1.com/upload/common_upload_img/store_img
    file: /home/shi/fruit.jpeg
    extract_by_jsonpath:
      img: $.data.url
  # 提交新建门店，不要用 submit_form，ui中太麻烦了太复杂了（如三级地址要逐级动态加载）
  post:
    url: http://admin.jym1.com/store/add_store
    is_ajax: true
    data:
      store_name: teststore-$random_str6
      store_logo_url: '$img'
      store_img_urls: '["$img"]'
      province: 450000
      city: 450100
      district: 450102
      address: testadd
      phone: 1347115$random_int4
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
-
  get: http://admin.jym1.com/store/store_list
  sleep: 2
```


## 运行
```
python ./runner.py 配置文件
```

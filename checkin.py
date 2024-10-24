import requests
import json
import os

from pypushdeer import PushDeer

# -------------------------------------------------------------------------------------------
# github workflows
# -------------------------------------------------------------------------------------------
if __name__ == '__main__':
    # pushdeer key 申请地址 https://www.pushdeer.com/product.html
    sckey = os.environ.get("SENDKEY", "")

    # 推送内容
    title = ""
    success, fail, repeats = 0, 0, 0        # 成功账号数量 失败账号数量 重复签到账号数量
    markdown_context = ""

    # glados账号cookie 直接使用数组 如果使用环境变量需要字符串分割一下
    cookies = os.environ.get("COOKIES", []).split("&")
    if cookies[0] != "":

        check_in_url = "https://glados.space/api/user/checkin"        # 签到地址
        status_url = "https://glados.space/api/user/status"          # 查看账户状态

        referer = 'https://glados.space/console/checkin'
        origin = "https://glados.space"
        useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        payload = {
            'token': 'glados.one'
        }
        
        for cookie in cookies:
            checkin = requests.post(check_in_url, headers={'cookie': cookie, 'referer': referer, 'origin': origin,
                                    'user-agent': useragent, 'content-type': 'application/json;charset=UTF-8'}, data=json.dumps(payload))
            state = requests.get(status_url, headers={
                                'cookie': cookie, 'referer': referer, 'origin': origin, 'user-agent': useragent})

            if checkin.status_code == 200:
                # 解析返回的json数据
                result = checkin.json()     
                # 获取签到结果
                check_result = result.get('message')
                points = result.get('points')

                # 获取账号当前状态
                result = state.json()
                # 获取剩余时间
                leftdays = int(float(result['data']['leftDays']))
                # 获取账号email
                email = result['data']['email']
                
                print(check_result)
                if "Checkin! Got" in check_result:
                    success += 1
                    message_status = "签到成功，会员点数 + " + points
                elif "Checkin Repeats!" in check_result:
                    repeats += 1
                    message_status = "重复签到，明天再来"
                else:
                    fail += 1
                    message_status = "签到失败，请检查..."

                if leftdays is not None:
                    message_days = f"{leftdays} 天"
                else:
                    message_days = "无法获取剩余天数信息"
            else:
                email = ""
                message_status = "签到请求URL失败, 请检查..."
                message_days = "获取账号状态失败..."

        # 推送内容 
        title = f'# Glados, 成功{success},失败{fail},重复{repeats}'
        markdown_context = f'''
                            **账号**: {email}<br>
                            **签到情况**: {message_status}<br>
                            **status字段**: {check_result}<br>
                            **剩余天数**: {message_days}<br>
                            '''
        print("Send Content:" + "\n", markdown_context)
    else:
        # 推送内容 
        title = f'# 未找到 cookies!'

    # 推送消息
    pushdeer = PushDeer(pushkey=sckey) 
    pushdeer.send_markdown(title, desp=markdown_context)

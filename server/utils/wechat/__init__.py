'''
公众号相关信息
'''
APPID = 'wxf1b19d71f836bb72'
SECRET = '4e6c83dd0d8036d0e862bdc3af4ba9c4'
WX_AUTH_URL = "https://open.weixin.qq.com/connect/oauth2/authorize"

# 基础令牌 https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_access_token.html
WX_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token'


# 微信换取用户信息和访问令牌的URL(通过code获取)
WX_CODE_ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
WX_CODE_ACCESS_REFRESH_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/refresh_token"

# 微信换取用户信息的URL
WX_USER_INFO_URL = "https://api.weixin.qq.com/sns/userinfo"
# WX_USER_INFO_URL = "https://api.weixin.qq.com/cgi-bin/user/info"

# 设置授权回调URL
# REDIRECT_URI = "http://www.ngsmq.online/api/us/wx/login/"
# REDIRECT_URI = "http://www.ngsmq.online/web/index.html"

# 获取凭证
WX_TICKET_URI = "https://api.weixin.qq.com/cgi-bin/ticket/getticket"


# 基础消息
WX_TEMPLATE_MESSAGE_SEND_URL = "https://api.weixin.qq.com/cgi-bin/message/template/send"

# 公众号菜单
WX_MENU_GET_URL = "https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info"
WX_MENU_CREATE_URL = " https://api.weixin.qq.com/cgi-bin/menu/create"

# 第三方登录配置指南

## 概述

校徽网支持4种第三方登录方式：
- 微信 (WeChat)
- 支付宝 (Alipay)
- Twitter / X
- Facebook

## 环境变量配置

在 `.env` 文件中添加以下配置：

### 1. 微信登录 (WeChat)

```bash
# 微信开放平台配置
WECHAT_APPID=your_wechat_appid
WECHAT_APPSECRET=your_wechat_appsecret
WECHAT_REDIRECT_URI=http://your-domain.com/auth/wechat/callback
```

**申请地址**: https://open.weixin.qq.com

**配置步骤**:
1. 在微信开放平台创建应用
2. 获取 AppID 和 AppSecret
3. 设置授权回调域名为你的域名

---

### 2. 支付宝登录 (Alipay)

```bash
# 支付宝开放平台配置
ALIPAY_APPID=your_alipay_appid
ALIPAY_PRIVATE_KEY=your_private_key
ALIPAY_PUBLIC_KEY=alipay_public_key
ALIPAY_REDIRECT_URI=http://your-domain.com/auth/alipay/callback
```

**申请地址**: https://open.alipay.com

**配置步骤**:
1. 在支付宝开放平台创建应用
2. 配置应用公钥
3. 获取支付宝公钥
4. 设置授权回调地址

---

### 3. Twitter / X 登录

```bash
# Twitter API 配置
TWITTER_CLIENT_KEY=your_twitter_api_key
TWITTER_CLIENT_SECRET=your_twitter_api_secret
TWITTER_REDIRECT_URI=http://your-domain.com/auth/twitter/callback
```

**申请地址**: https://developer.twitter.com

**配置步骤**:
1. 创建 Twitter Developer 账号
2. 创建应用并获取 API Key 和 API Secret
3. 设置 OAuth 2.0 回调地址
4. 启用 OAuth 2.0 登录

---

### 4. Facebook 登录

```bash
# Facebook API 配置
FACEBOOK_APPID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_REDIRECT_URI=http://your-domain.com/auth/facebook/callback
```

**申请地址**: https://developers.facebook.com

**配置步骤**:
1. 创建 Facebook Developer 账号
2. 创建应用并获取 App ID 和 App Secret
3. 添加 Facebook Login 产品
4. 设置有效的 OAuth 重定向 URI

---

## 本地开发配置示例

创建 `.env` 文件：

```bash
# 微信 (可选)
export WECHAT_APPID=""
export WECHAT_APPSECRET=""

# 支付宝 (可选)
export ALIPAY_APPID=""
export ALIPAY_PRIVATE_KEY=""
export ALIPAY_PUBLIC_KEY=""

# Twitter/X (可选)
export TWITTER_CLIENT_KEY=""
export TWITTER_CLIENT_SECRET=""

# Facebook (可选)
export FACEBOOK_APPID=""
export FACEBOOK_APP_SECRET=""

# 回调地址
export WECHAT_REDIRECT_URI="http://127.0.0.1:5001/auth/wechat/callback"
export ALIPAY_REDIRECT_URI="http://127.0.0.1:5001/auth/alipay/callback"
export TWITTER_REDIRECT_URI="http://127.0.0.1:5001/auth/twitter/callback"
export FACEBOOK_REDIRECT_URI="http://127.0.0.1:5001/auth/facebook/callback"
```

## 启动时加载环境变量

```bash
# Linux/Mac
source .env
python3 app.py

# 或使用 python-dotenv
pip install python-dotenv
```

## 配置状态检查

登录页面会检查是否已配置：
- ✅ 已配置：显示可点击的登录按钮
- ❌ 未配置：显示禁用的按钮

## 注意事项

1. **HTTPS要求**: 第三方登录通常要求生产环境使用 HTTPS
2. **域名备案**: 微信登录要求域名已ICP备案
3. **审核时间**: 支付宝、微信应用审核可能需要数天
4. **测试账号**: 开发阶段可使用沙箱环境测试

## 生产环境部署

```bash
# 设置生产环境变量
export FLASK_ENV=production
export WECHAT_APPID="your_production_appid"
# ... 其他配置

# 使用 Gunicorn 启动
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 快速测试 (无第三方API)

如果只是测试登录流程，可以使用内置的测试账号：

```python
# 创建测试用户
curl -X POST http://127.0.0.1:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'
```

或直接使用密码登录功能（无需第三方API）。

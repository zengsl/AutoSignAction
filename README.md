bilibil 登录信息  BILIBILI_COOKIE

<img width="1340" height="802" alt="1a85218e967226b1073cd37090141797" src="https://github.com/user-attachments/assets/d0203866-7fb4-47b5-9f78-1ee1e1fba365" />

``` json
bilibil 还有一个环境变量 MULTI    值是 [
    {
 "options": {
            "watch": 1,  # 每日观看视频
            "coins": 0,  # 投币个数
            "share": 1,  # 视频分享
            "comics": 1,  # 漫画签到
            "lb": 1,  # 直播签到
            "threshold": 100,  # 仅剩多少币时不再投币(不写默认100)
            "toCoin": 1,  # 银瓜子兑换硬币
        }
    }
]

```

COOKIE_QUARK  登录信息

<img width="1235" height="1165" alt="988a056b94af98364edc3dca350bab95" src="https://github.com/user-attachments/assets/1fa084bf-163b-4602-b316-67edb8463b52" />

 https://drive-m.quark.cn/1/clouddrive/capacity/growth/info

格式：
user=xxx;kps=xxx;sign=xxx;vcode=xxx
user=xxx;kps=xxx;sign=xxx;vcode=xxx

## 消息推送

签到结果通过环境变量 `PUSH`（JSON 格式）推送到手机，支持 Server酱、Bark、Pushplus、Qmsg、企业微信、邮件，可同时配置多个：

``` json
[
    {
        "type": "serverChan",
        "key": "sct的sendkey"
    },
    {
        "type": "bark",
        "key": "https://api.day.app/设备key"
    },
    {
        "type": "qmsg",
        "key": "qmsg的key"
    }
]
```

- `serverChan` / `server`：Server酱，key 为 `https://sct.ftqq.com` 上的 SendKey，接口 `https://sctapi.ftqq.com/<sendkey>.send`
- `bark`：Bark 推送，key 可填设备 key（自动使用 `https://api.day.app/`）或完整推送地址（支持自建服务），例如 `https://api.day.app/设备key`
- 更多类型（`pushplus`、`qmsg`、`workWechatRobot`、`workWechat`、`mail`）见 [push/README.md](push/README.md)

## GitHub Actions 配置

项目通过 GitHub Actions 定时运行（`bilibili签到`、`无时间限制签到`），需要在仓库 **Settings → Secrets and variables → Actions** 中配置以下环境变量：

| 环境变量 | 说明 | 是否必填 |
|------|------|------|
| `BILIBILI_COOKIE` | Bilibili 登录 Cookie，格式见上文 | 运行 bilibili 签到必填 |
| `MULTI` | Bilibili 多账号任务配置（JSON），格式见上文 | 选填，不填则无任务可跑 |
| `COOKIE_QUARK` | 夸克网盘登录 Cookie（多账号用换行分隔），格式见上文 | 运行夸克签到必填 |
| `PUSH` | 推送配置（JSON），支持 Server酱 / Bark / Pushplus / Qmsg / 企业微信 / 邮件 | 选填 |
| `SERVERCHAN_SENDKEY` | Server酱 SendKey（`https://sct.ftqq.com` 获取），单独配置时无需填 `PUSH` | 选填 |
| `BARK_URL` | Bark 推送地址，如 `https://api.day.app/设备key`，单独配置时无需填 `PUSH` | 选填 |
| `EMAIL_SMTP_SERVER` | SMTP 服务器地址，如 `smtp.qq.com` | 邮件通知选填 |
| `EMAIL_SMTP_PORT` | SMTP 端口，如 `465` | 邮件通知选填 |
| `EMAIL_SENDER` | 发件邮箱地址 | 邮件通知选填 |
| `EMAIL_PASSWORD` | 发件邮箱授权码（非登录密码） | 邮件通知选填 |
| `EMAIL_RECIPIENT` | 收件邮箱地址 | 邮件通知选填 |

推送配置支持两种方式（可同时使用）：一是通过 `PUSH` 变量集中配置多个渠道，二是分别配置 `SERVERCHAN_SENDKEY`、`BARK_URL` 单个渠道。配置示例：

``` json
[
    {
        "type": "serverChan",
        "key": "sct的sendkey"
    },
    {
        "type": "bark",
        "key": "https://api.day.app/设备key"
    }
]
```

- 涉及账号 Cookie 的变量建议配置为 **Secrets（密钥）**，不勾选公开；`PUSH` 同理。
- `SERVERCHAN_SENDKEY` / `BARK_URL` 也已接入两个工作流，直接配置为 **Secrets** 即可生效，无需再填 `PUSH`。
- `MULTI` 可在 **Variables（变量）** 中配置（非敏感信息）。
- 修改配置后，在 **Actions** 页面手动触发对应工作流即可立即生效，无需等待定时任务。

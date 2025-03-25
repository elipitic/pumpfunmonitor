# PumpFunMonitor
本系统实现了对于PumpFun上Meme币的监控功能<br>
- 监控新Meme币，通知到Telegram当中，并且将Meme币信息保存至Supabase数据库中
- 监控PumpFun中迁移至raydium池子当中的时间，并且将Mint地址通过Telegram通知用户

# PrePrepare
```
git pull 仓库地址
```
## 1. TG BOT
1. 打开@BotFather，点击Start
2. 输入/newbot发送并填写name和username
3. 获取token并且填入config.py中
4. 向你的Bot当中发送信息,然后打开网址https://api.telegram.org/bot<你的token>/getUpdates，复制id后的数字填入config.py

## 2. Supabase
1.首先注册supabase，获取supabase的SUPABASE_URL与SUPABASE_KEY，填入config.py
2.然后进入sql editor,执行以下sql语句创建表
```
create table
  new_coins (id int8 primary key,created_at timestamp DEFAULT now(), name text, symbol text, uri text, mint text, bondingCurve text, "user" text);
```

## 3. RPC节点获取
可于quicknode获取rpc节点填入config.py
## 3. Run
```
docker-compose up -d
```

## 待添加功能
- 迁移时自动购买功能


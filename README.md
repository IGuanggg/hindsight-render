# Hindsight on Render

简化版 Hindsight API，部署到 Render 免费套餐。

## 部署步骤

### 1. Fork 或上传代码到 GitHub

```bash
# 创建新仓库并推送
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/hindsight-render.git
git push -u origin main
```

### 2. 在 Render 创建服务

1. 登录 https://dashboard.render.com
2. 点击 "New +" → "Web Service"
3. 连接你的 GitHub 仓库
4. 配置：
   - **Name**: hindsight-api
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn core.api.main:app --host 0.0.0.0 --port $PORT`
5. 点击 "Create Web Service"

### 3. 配置环境变量

在 Render Dashboard → Settings → Environment Variables：

**使用百炼(Bailian/阿里)：**
```
LLM_PROVIDER=bailian
BAILIAN_API_KEY=sk-sp-xxxxxxxx
BAILIAN_BASE_URL=https://coding.dashscope.aliyuncs.com/v1
BAILIAN_MODEL=qwen3.5-plus
```

**或使用混元(Hunyuan)：**
```
LLM_PROVIDER=hunyuan
HUNYUAN_SECRET_ID=your_secret_id
HUNYUAN_SECRET_KEY=your_secret_key
```

### 4. 添加 PostgreSQL 数据库（可选）

1. Dashboard → "New +" → "PostgreSQL"
2. 选择 Free 套餐
3. 复制数据库连接字符串
4. 添加到 Web Service 的环境变量：`DATABASE_URL`

### 5. 配置 Keep Alive

使用 UptimeRobot 防止休眠：
1. 注册 https://uptimerobot.com
2. Add New Monitor → HTTP(s)
3. URL: `https://your-service.onrender.com/ping`
4. Interval: 5 minutes

## API 使用

### 创建记忆
```bash
curl -X POST https://your-service.onrender.com/banks/my-bank/memory-blocks \
  -H "Content-Type: application/json" \
  -d '{
    "content": "用户想在小红书做星座账号",
    "keywords": ["小红书", "星座", "运营"],
    "metadata": {"project": "星座账号"}
  }'
```

### 检索记忆
```bash
curl "https://your-service.onrender.com/banks/my-bank/memory-blocks?query=星座&limit=5"
```

### Ping 保活
```bash
curl https://your-service.onrender.com/ping
```

## 与 OpenClaw 集成

在 `~/.openclaw/openclaw.json` 中添加：

```json
{
  "mcpServers": {
    "hindsight": {
      "url": "https://your-service.onrender.com"
    }
  }
}
```

## 限制

- 免费套餐：750小时/月（约24小时/天）
- 15分钟无访问会休眠
- 使用 UptimeRobot 可保持活跃

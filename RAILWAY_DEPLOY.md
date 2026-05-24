# 期权异常流识别器 - Railway 部署指南

**5分钟部署，无需买域名，自动获得免费URL，永远免费试用！**

---

## 🎯 Railway vs 阿里云

| 对比项 | Railway | 阿里云香港 |
|------|---------|----------|
| **首年成本** | $5试用 | ¥300/年 |
| **长期成本** | $5/月 = $60/年 | ¥300/年 |
| **部署难度** | 🟢 极简（1步） | 🟡 中等（多步） |
| **需要买域名** | ❌ 不需要 | ❌ 不需要 |
| **自动获得URL** | ✅ https://xxx.railway.app | ❌ 需要自己的IP |
| **推荐用途** | 快速测试、演示、小项目 | 长期运营、大流量 |

---

## 💡 我的建议

如果你：
- 🟢 **只是想快速试用** → Railway（现在就用，不花钱）
- 🟢 **不确定要不要长期用** → Railway（$5试用）
- 🟢 **想要最简单的方式** → Railway（一键部署）
- 🟡 **已经确定长期用** → 阿里云（¥25/月，比Railway便宜）

---

## 🚀 Railway 5分钟快速部署

### 第1步：准备代码（1分钟）

需要这些文件：
- ✅ app.py
- ✅ requirements.txt
- ✅ options_scanner_mobile.html
- ✅ Procfile（新增，告诉Railway怎么运行）
- ✅ runtime.txt（可选，指定Python版本）

### 第2步：创建Procfile

在本地电脑创建一个文件 `Procfile`（无扩展名），内容：

```
web: python app.py
```

保存到和 app.py 同一个文件夹。

### 第3步：创建runtime.txt（可选）

创建文件 `runtime.txt`，内容：

```
python-3.11.7
```

保存到同一个文件夹。

### 第4步：上传到GitHub

1. 注册 GitHub: https://github.com/signup
2. 新建仓库（Repository），名字：`options-scanner`
3. 上传这些文件：
   - app.py
   - requirements.txt
   - options_scanner_mobile.html
   - Procfile
   - runtime.txt（可选）
   - .gitignore（可选）

**简单的办法：**
1. 在GitHub网页上创建仓库
2. 点 **Add file** → **Upload files**
3. 把5个文件拖进去
4. 点 **Commit changes**

### 第5步：在Railway部署

1. 进 https://railway.app/
2. 点 **Login** 或 **Start for free**
3. 选择 **GitHub** 登录（推荐）
4. 授权Railway访问你的GitHub
5. 点 **Create a new project**
6. 选 **Deploy from GitHub repo**
7. 选 `options-scanner` 仓库
8. **自动部署开始！**（等2-3分钟）

完成后你会看到：
```
✅ Deployment successful
🌐 Your app is live at: https://options-scanner-xxxx.railway.app
```

### 第6步：打开你的app

点那个链接，或者在浏览器输入：

```
https://options-scanner-xxxx.railway.app/options_scanner_mobile.html
```

**完成！** 就这么简单！🎉

---

## 📱 使用你的应用

### 在浏览器打开

```
https://options-scanner-xxxx.railway.app/options_scanner_mobile.html
```

### 测试后端

访问：
```
https://options-scanner-xxxx.railway.app/health
```

应该返回：
```json
{"status":"ok"}
```

### 手机访问

1. 手机浏览器输入上面的URL
2. 点 **🔍 开始扫描**
3. 等1-2分钟看结果

无需任何IP配置，直接用域名！

---

## 💰 费用说明

### 免费套餐（$5试用）

- ⏰ 时限：30天 或 用完$5额度
- 💾 存储：512MB
- 🔄 执行时间：不限
- 🌐 带宽：不限
- ✅ 足够测试整个app

### 付费套餐（可选）

如果30天后还想用：

- **Hobby**: $5/月
  - 内存：512MB
  - 存储：5GB
  - 完全够你的app用
  
- **Pro**: $12/月起
  - 内存：1GB+
  - 存储：100GB+
  - 适合商用

---

## 🔧 常见问题

### Q: Railway的免费$5试用怎么用？

1. 进 https://railway.app/
2. 点右上 **Account**
3. **Billing** 里看试用额度
4. $5试用自动应用，不需要信用卡

### Q: 试用期满了怎么办？

选择：
- 🔴 **删除项目**（免费，但app下线）
- 🔵 **升级到付费**（$5/月继续用）
- 🟢 **保持免费但受限**（速度变慢，但仍能用）

### Q: 怎么更新代码？

在GitHub更新 app.py，Railway会自动重新部署！

**步骤：**
1. 在GitHub编辑 app.py
2. 提交（Commit）
3. Railway看到更新，自动重新部署
4. 1-2分钟后生效

### Q: 怎么看日志？

1. 进 Railway Dashboard
2. 找你的项目
3. 点 **Deployments**
4. 看 **Logs** 标签

### Q: 能改扫描的股票吗？

可以！编辑 app.py：

```python
STOCK_SYMBOLS = ['AAPL', 'TSLA', '你的股票代码']
```

提交后自动重新部署。

### Q: 怎么绑定自己的域名？

Railway支持自定义域名：

1. Railway Dashboard → 你的项目
2. **Settings** → **Domains**
3. 添加你的域名
4. 按提示在域名DNS里添加CNAME记录

然后用自己的域名访问。

### Q: 为什么显示502或503错误？

通常是应用启动失败。检查：

1. Procfile 内容是否正确（`web: python app.py`）
2. requirements.txt 是否有遗漏
3. app.py 是否有语法错误
4. 查看 **Logs** 找具体错误

### Q: yfinance超时？

Railway在美国，到Yahoo Finance很快。如果还是超时：

1. 确保网络连接正常
2. 查看日志找错误信息
3. 重启应用（Railway Dashboard → Redeploy）

### Q: 能支持多少并发用户？

Railway免费/Hobby方案支持：
- 512MB内存
- 足以支持 50-100 并发用户
- 你的app完全够用

### Q: 怎么删除项目？

1. Railway Dashboard
2. 点你的项目
3. **Settings** → **Danger Zone**
4. **Delete Project**

确认删除，项目会立即下线。

---

## 📊 Railway vs 本地电脑

| 对比项 | Railway | 本地电脑 |
|------|---------|--------|
| **启动** | 1键部署，自动运行 | 双击run.bat，手动运行 |
| **网址** | 自动分配(xxx.railway.app) | 需要公网IP或内网访问 |
| **可靠性** | 24/7自动运行 | 依赖电脑一直开着 |
| **维护** | Railway处理 | 你自己维护 |
| **成本** | $5/月 | 电费 + U盘磨损 |
| **推荐** | ✅ 长期用 | ❌ 仅临时测试 |

---

## 🎯 3种部署方案对比

| 方案 | 成本 | 部署时间 | 难度 | 推荐 |
|------|------|---------|------|------|
| **Railway** | $5/月 | 5分钟 | 🟢 极简 | ✅ 快速试用 |
| **阿里云** | ¥25/月 | 15分钟 | 🟡 中等 | ✅ 长期用 |
| **AWS** | $3+隐形成本 | 30分钟 | 🔴 复杂 | ❌ 不推荐 |
| **本地电脑** | 0 | 1分钟 | 🟢 极简 | ❌ 仅测试 |
| **U盘** | 0 | 10分钟 | 🟡 中等 | ❌ 移动使用 |

---

## 💡 我的建议流程

```
第1周：用Railway $5试用
      ↓
第2周：如果满意，升级Railway Hobby ($5/月)
      或改用阿里云 (¥25/月，更便宜)
      ↓
第3周+：长期运营
```

---

## ✅ Railway部署检查清单

- [ ] 创建了GitHub账号
- [ ] 新建了 `options-scanner` 仓库
- [ ] 上传了5个文件（app.py, requirements.txt, options_scanner_mobile.html, Procfile, runtime.txt）
- [ ] 创建了Railway账号
- [ ] 连接了GitHub仓库
- [ ] 部署成功（看到绿色✅）
- [ ] 获得了Railway的免费域名（https://xxx.railway.app）
- [ ] 能打开 `https://xxx.railway.app/options_scanner_mobile.html`
- [ ] 能点 🔍 开始扫描并看到结果

都通过了？部署成功！🎉

---

## 🚀 现在就开始

1. ✅ 创建GitHub账号（免费）
2. ✅ 上传5个文件到GitHub
3. ✅ 连接Railway（自动部署）
4. ✅ 打开自动分配的URL
5. ✅ 开始使用

**总共5分钟，免费永久试用！**

---

## 📞 遇到问题？

常见问题和解决方案都在上面。如果还有问题：

1. 查看Railway的 **Logs**（找错误信息）
2. 检查 **Procfile** 和 **requirements.txt**
3. 确认 app.py 没有语法错误
4. 重新部署（点 **Redeploy**）

祝你使用愉快！🎉

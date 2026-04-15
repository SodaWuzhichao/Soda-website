# SODA567 个人网站

## 📁 项目结构
```
soda567/
├── index.html          # 主页
├── admin_new.html      # 后台管理（密码：soda567）
├── tools/
│   └── index.html      # 在线工具页
└── images/
    └── profile.jpg     # 个人照片
```

## 🚀 部署到 soda567.dpdns.org

### 方法一：使用 GitHub Pages（推荐）

1. 在 GitHub 创建仓库
2. 上传所有文件
3. 在仓库设置中启用 GitHub Pages
4. 在 digitalplat.org 设置 DNS 指向 GitHub Pages

### 方法二：使用 FTP 上传

1. 获取 FTP 账号信息
2. 使用 FileZilla 等工具上传所有文件
3. 确保 index.html 在根目录

---

## 🤖 Agent 操作规范

> **约束先行**：进入本项目目录，第一件事永远是完整阅读此区块。没有读完之前，不许动手改任何东西。

### 修改流程（铁律）

1. **必须先拉取远程最新代码**
   ```bash
   git fetch origin
   git pull origin main
   ```
   ⚠️ 禁止跳过此步骤！

2. **对比差异**
   ```bash
   git diff origin/main
   ```
   确认本地和远程没有冲突。

3. **本地修改**

4. **同步部署**
   | 文件 | 部署位置 |
   |------|----------|
   | index.html | GitHub → Cloudflare Pages |
   | admin_new.html | GitHub + soda-server/backend/ |
   | livestream.html | GitHub → Cloudflare Pages |
   | tools/*.html | GitHub → Cloudflare Pages |

   如果修改了 admin_new.html，需要同步到 Flask 目录：
   ```bash
   cp admin_new.html ~/Documents/soda-server/backend/
   pkill -f "python.*app.py"
   cd ~/Documents/soda-server/backend && nohup python3 app.py &
   ```

5. **提交并推送**
   ```bash
   git add 修改的文件
   git commit -m "描述修改内容"
   git push origin main
   ```

6. **验证部署**
   - 展示页：https://soda567.dpdns.org/
   - 后台：https://admin.soda567.dpdns.org/

### 🚫 禁止事项
- **禁止使用 git push --force** （除非得到伍老师明确同意）
- **禁止在 Cloudflare 后台直接编辑代码**——所有修改必须在本地完成后推送
- 禁止直接上传大文件到 Cloudflare（100MB限制）：使用 Tailscale 直连 `http://100.73.100.90:5001/admin`

### 🧪 实验规则
- 所有实验性修改放在 `_sandbox/` 目录
- `_sandbox/` 里的内容超过 30 天自动删除
- 实验验证通过后，移动到正式目录

---

## ⚙️ 配置

### Google Analytics
在 index.html 第 666 行替换 `G-XXXXXXXXXX` 为你的 GA ID

### 后台管理
- 访问：https://soda567.dpdns.org/admin_new.html
- 密码：soda567
- 修改密码：编辑 admin_new.html 第 246 行

## 📝 使用说明

1. 后台添加/编辑作品
2. 点击"💾 保存并同步到主页"
3. 刷新主页查看效果

## 🔧 维护

- 作品数据存储在浏览器 localStorage
- 定期使用"📦 导出备份"功能备份数据

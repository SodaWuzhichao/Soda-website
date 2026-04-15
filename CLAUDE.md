# CLAUDE.md - Soda Website 项目规范

> 本文件是 Soda-website 项目的宪法。所有修改必须遵守本文件约定的规则。

## 📂 项目结构

```
Soda-website/
├── index.html          # 主展示页
├── admin_new.html      # 后台管理页（通过 Flask 服务）
├── livestream.html     # 直播案例页
├── tools/              # 工具页面目录
├── images/             # 图片资源目录
└── _sandbox/          # 实验性内容（超过30天自动清理）
```

## 📋 修改流程（铁律）

### 1. 拉取远程最新代码
```bash
git fetch origin
git pull origin main
```
⚠️ 禁止跳过此步骤！

### 2. 对比本地和远程差异
```bash
git diff origin/main
```
确认要修改的文件，确保不会覆盖别人的修改。

### 3. 本地修改

### 4. 同步到所有部署位置
| 文件 | 部署位置 |
|------|----------|
| index.html | GitHub → Cloudflare Pages |
| admin_new.html | GitHub + soda-server/backend/ |
| livestream.html | GitHub → Cloudflare Pages |
| tools/*.html | GitHub → Cloudflare Pages |

如果修改了 admin_new.html，需要同步到 Flask 目录：
```bash
cp ~/Documents/Soda-website/admin_new.html ~/Documents/soda-server/backend/
# 然后重启 Flask
pkill -f "python.*app.py"
cd ~/Documents/soda-server/backend && nohup python3 app.py &
```

### 5. 提交并推送
```bash
git add 修改的文件
git commit -m "描述修改内容"
git push origin main
```

### 6. 验证部署
- 展示页：https://soda567.dpdns.org/
- 后台：https://admin.soda567.dpdns.org/

## 🚫 禁止事项

- **禁止使用 git push --force**（除非得到伍老师明确同意）
- **禁止在 Cloudflare 后台直接编辑代码**——所有修改必须在本地完成后推送
- 禁止直接上传大文件到 Cloudflare（100MB限制）：使用 Tailscale 直连 `http://100.73.100.90:5001/admin`

## 🧪 实验规则

- 所有实验性修改放在 `_sandbox/` 目录
- `_sandbox/` 里的内容超过 30 天自动删除
- 实验验证通过后，移动到正式目录

## 📅 备份

- 每天凌晨 3 点 Openclaw 自动备份
- 备份位置：`~/.openclaw-backups/`

---

_最后更新：2026-04-15_
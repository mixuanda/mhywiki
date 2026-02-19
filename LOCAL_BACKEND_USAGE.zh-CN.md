# HomDGCat 本地后台使用说明（启动 + 编辑 + 原始数据入库）

## 1. 启动方式

### 方式 A：双击启动（推荐）
1. 双击：`/Users/mixuanda/Library/CloudStorage/OneDrive-mixuanda/root/code/HomDGCat/start_local_backend.command`
2. 脚本会自动处理端口：
   - 如果 `9000` 已经是本项目后台在运行：直接复用
   - 如果 `9000` 被其他程序占用：自动切换到 `9001~9099` 的空闲端口
3. 启动成功后会自动打开：
   - 管理后台：`http://localhost:<端口>/__admin`
   - 网站预览：`http://localhost:<端口>/index/`

### 方式 B：终端启动
```bash
cd /Users/mixuanda/Library/CloudStorage/OneDrive-mixuanda/root/code/HomDGCat
python3 scripts/local_admin.py --port 9000
```

## 2. 启动后生成的文件

- 运行日志：`/Users/mixuanda/Library/CloudStorage/OneDrive-mixuanda/root/code/HomDGCat/easy_updates/local_backend.log`
- 后台 PID：`/Users/mixuanda/Library/CloudStorage/OneDrive-mixuanda/root/code/HomDGCat/easy_updates/local_backend.pid`
- 当前端口：`/Users/mixuanda/Library/CloudStorage/OneDrive-mixuanda/root/code/HomDGCat/easy_updates/local_backend.port`

可用下面命令停止：
```bash
cd /Users/mixuanda/Library/CloudStorage/OneDrive-mixuanda/root/code/HomDGCat
kill "$(cat easy_updates/local_backend.pid)"
```

## 3. 后台编辑流程（角色）

1. 打开 `__admin`
2. 左侧选目录（GI/SR + CH/EN + 角色）
3. 中间选角色条目
4. 右侧按网页目录 tab 编辑：
   - GI：基本信息 / 技能 / 被动 命之座 / 养成计算 / 改动汇总 / 妮可少女的研究 / 故事 / 语音
   - SR：基本信息 / 技能 / 行迹 星魂 / 养成计算 / 改动汇总 / 妮可少女的研究 / 故事 / 语音
5. 区块支持：
   - `保存当前区块`
   - `新增`（数组加项、对象加键）
   - `删除`（数组按下标删、对象按键删）

每次保存/新增/删除都会自动备份到：
`/Users/mixuanda/Library/CloudStorage/OneDrive-mixuanda/root/code/HomDGCat/easy_updates/entity_backups/`

## 4. 原始数据目前如何保存

原始数据是直接保存在 `site/` 目录里的源码文件，不走数据库。

主要路径：
- GI 角色总表：`/Users/mixuanda/Library/CloudStorage/OneDrive-mixuanda/root/code/HomDGCat/site/gi/CH/avatar.js`
- GI 角色详情：`/Users/mixuanda/Library/CloudStorage/OneDrive-mixuanda/root/code/HomDGCat/site/gi/CH/Avatar/<角色名>_1.js`、`<角色名>_2.js`
- SR 角色总表：`/Users/mixuanda/Library/CloudStorage/OneDrive-mixuanda/root/code/HomDGCat/site/data/CH/Avatar.js`
- SR 角色详情：`/Users/mixuanda/Library/CloudStorage/OneDrive-mixuanda/root/code/HomDGCat/site/data/CH/Avatar/<角色ID>.js`
- TextMap：`/Users/mixuanda/Library/CloudStorage/OneDrive-mixuanda/root/code/HomDGCat/site/TextMap/`
- 图片素材：`/Users/mixuanda/Library/CloudStorage/OneDrive-mixuanda/root/code/HomDGCat/site/images/`

## 5. 把原始数据上传到 Repo（你当前需求）

已完成的配置：
- `.gitignore` 已取消对 `site/` 的忽略
- 新增 `.gitattributes`，为大文件准备了 Git LFS 规则（例如 `site/TextMap/GI.json`）

### 你需要再执行（一次性）
当前环境提示 `git lfs` 尚未安装。请先安装 Git LFS，再推送大文件：
```bash
git lfs install
```

### 提交并上传
```bash
cd /Users/mixuanda/Library/CloudStorage/OneDrive-mixuanda/root/code/HomDGCat
git add .gitattributes .gitignore site
git commit -m "track raw site data"
git push
```

### 重要说明
- `site/TextMap/GI.json` 超过 100MB，普通 GitHub push 会被拒绝，必须用 Git LFS。
- 如果远程仓库不支持 LFS，需要改成分仓或仅上传 `releases/site_*.zip`。

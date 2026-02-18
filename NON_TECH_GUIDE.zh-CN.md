# 网站恢复与日常更新（零代码版）

这份指南适合不会写代码的使用方式。

## 一、你现在最常用的文件

1. `start_local_backend.command`：启动本地网站 + 全站可视化后台
2. `preview_site.command`：只预览网站
3. `init_textmap_shards.command`：首次把 TextMap 拆分成分片（推荐先做一次）
4. `rebuild_textmap_from_shards.command`：从分片重建 `GI.json/SR.json`
5. `make_release_package.command`：打包发布 zip，并更新校验文件 `releases/SHA256SUMS.txt`

> 旧的 `open_updates_file.command / apply_updates.command` 仍可用，但现在推荐优先使用可视化后台。

## 二、本地部署（最简单）

1. 双击 `start_local_backend.command`
2. 浏览器打开后台：`http://localhost:9000/__admin`
3. 网站预览地址：`http://localhost:9000/index/`
4. 停止服务：在终端窗口按 `Ctrl + C`

## 三、日常改内容（全站）

后台已经是三栏模式：

- 左栏：数据源目录（游戏/语言/模块/文件）
- 中栏：当前数据源记录列表（支持搜索/分页）
- 右栏：编辑器（字段模式 + 原始 JSON 模式）

推荐操作流程：

1. 左栏先选数据源（例如任务、怪物、活动、教程、TextMap、角色、武器等）
2. 中栏搜索并点开记录
3. 右栏先用“字段模式”改简单文本；复杂结构改“原始 JSON”
4. 点“预览差异”确认
5. 点“保存字段模式”或“保存原始JSON”
6. 打开网站预览检查页面
7. 如果改错，点“回滚最近一次保存”

## 四、TextMap 分片（推荐）

为什么要分片：`GI.json` / `SR.json` 太大，分片后更容易管理和回滚。

首次使用：

1. 双击 `init_textmap_shards.command`
2. 会生成：
   - `site/TextMap/GI_shards/00.json ... 3f.json`
   - `site/TextMap/SR_shards/00.json ... 3f.json`
3. 后台以后会优先编辑分片；保存时自动重建 `GI.json/SR.json`（兼容现有网站前端）

如果你手动改了分片文件，可双击 `rebuild_textmap_from_shards.command` 重新聚合。

## 五、重新部署（推荐）

1. 双击 `make_release_package.command`
2. 生成 `releases/site_时间戳.zip`
3. 同时更新 `releases/SHA256SUMS.txt`（用于校验包完整性）
4. 上传 zip 到服务器并解压，网站根目录指向解压后的 `site/`

Nginx 常用规则：

```nginx
location = / {
    return 302 /index/;
}

location = /home {
    return 302 /index/;
}

location / {
    try_files $uri $uri/ $uri/index.html =404;
}
```

## 六、重要提示

- 每次保存都会自动备份到：`easy_updates/entity_backups/`
- 后台遇到“只读”文件时会显示原因（例如异常源文件）
- 如果你只想保留代码仓库，不想跟踪超大网站内容，当前默认已经把 `site/` 作为本地内容目录处理

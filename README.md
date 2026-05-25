# xhs-travel-planner

基于真实小红书笔记生成手机端互动旅行计划页的 Codex Skill。

它会引导 Codex 先使用用户已登录的小红书浏览器会话采集真实笔记，提取地点、餐厅与避坑信息，再按顺路性整理每日路线，最终生成可直接部署到 GitHub Pages 的单文件 `travel-plan.html`。

## 安装

### 方式一：一行命令（推荐，跨 runtime）

打开你正在使用的 agent，例如 Claude Code、Codex、Cursor、OpenClaw、Hermes、CodeBuddy、WorkBuddy、Gemini CLI、OpenCode 等，然后告诉它：

```text
帮我安装这个 skill：https://github.com/SPUERSAIYAN/xhs-travel-planner
```

或者使用通用 CLI 安装器 [vercel-labs/skills](https://github.com/vercel-labs/skills)，它支持 Codex、Claude Code、Cursor 等 55+ agent runtime：

```bash
npx skills add SPUERSAIYAN/xhs-travel-planner
```

CLI 会识别可用的 agent 并将 skill 安装到相应目录。需要明确指定 agent 时使用 `-a`：

```bash
npx skills add SPUERSAIYAN/xhs-travel-planner -a codex
npx skills add SPUERSAIYAN/xhs-travel-planner -a claude-code
npx skills add SPUERSAIYAN/xhs-travel-planner -a cursor
npx skills add SPUERSAIYAN/xhs-travel-planner -a openclaw
```

如需安装到用户级全局目录，附加 `-g`：

```bash
npx skills add SPUERSAIYAN/xhs-travel-planner -g -a codex
```

## 能做什么

- 强制先打开小红书，由用户扫码登录后再开始调研。
- 只以实际打开并核验过的小红书笔记作为旅行推荐证据。
- 优先采集可见点赞/收藏较高、内容具体的笔记，并保留来源与互动数据。
- 提取景点、餐厅、夜市、交通建议、排队/预约/价格等避坑提醒。
- 使用高德地图为主、百度地图为备选，生成地点跳转链接。
- 生成 Tailwind H5 风格的手机页面：Day tabs、时间轴、地点详情、预算弹层和保存下载。
- 每个地点详情内提供对应的小红书来源跳转，不在页面末尾堆放长来源列表。
- 支持 `mobileShareUrl`，优先用小红书分享生成的手机链接打开笔记。

## 工作流程

```text
打开浏览器并扫码登录小红书
        ↓
搜索并打开多条真实、高质量笔记
        ↓
记录来源、互动量与手机分享链接
        ↓
提取地点 / 美食 / 避坑信息
        ↓
整理每日顺路行程并生成地图链接
        ↓
生成 travel-plan.html
        ↓
部署至 GitHub Pages，手机打开
```

## 调研规则

为了避免只靠一两条帖子得出行程结论，skill 默认要求：

| 行程长度 | 最少打开并保留的小红书笔记 |
| --- | ---: |
| 1 天或非常窄的主题 | 8 条 |
| 2-4 天 | 15 条 |
| 5 天及以上 | 20 条 |

采集时应覆盖路线、美食、避坑、交通、住宿区域和重点地点等不同搜索意图。点赞与收藏数用于优先选择内容，不等同于真实性证明；重要推荐与避坑结论仍应由不同作者的多条笔记交叉支持。

每条来源尽量记录：

- 标题、作者、发布日期、笔记网页地址与搜索词。
- 可见的点赞、收藏、评论数量。
- 可读摘要和可提取地点/风险。
- 通过笔记自身「分享 / 复制链接」取得的 `mobileShareUrl`。

`mobileShareUrl` 通常是 `xhslink.com` 分享链接，用于手机端按钮。PC 地址栏的 `xiaohongshu.com/explore/...` 链接仅作为网页备用，不能冒充手机跳转已验证。

## 使用方式

在 Codex 中使用此 skill，例如：

```text
使用 $xhs-travel-planner，帮我做一个 4 天长沙小红书美食旅行计划。

要求：
- 只使用小红书真实笔记作为来源。
- 第一步打开浏览器让我扫码登录小红书。
- 搜索并打开至少 15 条笔记，优先高赞/高收藏且内容具体的笔记。
- 每条来源保留可见点赞、收藏、评论，以及通过分享动作获得的手机分享链接。
- 输出手机端可打开的 travel-plan.html，要有避坑、高德地图跳转和每个地点对应的小红书来源。
```

也可以先填写 [assets/brief-template.md](assets/brief-template.md)，或参考 [references/prompt-templates.md](references/prompt-templates.md) 中的完整提示词。

## 输出页面

<img width="630" height="1368" alt="060f159ccd51477a09c1252711892358" src="https://github.com/user-attachments/assets/f6b3f3a5-f0f4-448f-836c-f89a6045c75c" />



## 发布到 GitHub Pages

将生成的页面作为站点入口发布：

1. 将 `travel-plan.html` 复制或重命名为 `index.html`。
2. 上传至 GitHub Pages 使用的仓库根目录或 `docs/` 目录。
3. 在仓库 Settings > Pages 中选择对应分支和发布目录。
4. 使用 GitHub Pages 提供的链接在手机浏览器中打开。


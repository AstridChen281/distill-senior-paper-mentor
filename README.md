# 蒸馏你的师兄帮你改稿

把你自己的参考论文整理成科研搭档：模拟审稿、讨论课题和实验、学习写作与叙事、按要求改稿、解答研究问题，以及日常交流。

公开仓库是通用模板，**不附带任何人的论文、人物资料、定制阅读笔记或预先蒸馏的档案**。你需要先提供自己的参考论文。这里的蒸馏是阅读与归纳，不是训练模型，也不会让 agent 成为作者本人。

## 安装

将仓库放入本机 Codex 的 skills 目录，目录名使用 `distill-senior-paper-mentor`。以默认 `~/.codex` 配置为例：

```bash
git clone https://github.com/AstridChen281/distill-senior-paper-mentor.git \
  ~/.codex/skills/distill-senior-paper-mentor
```

如果本机使用自定义 `CODEX_HOME`，将其放在该目录的 `skills/distill-senior-paper-mentor` 下。已有同名定制版时，使用独立的 Codex 配置目录，避免覆盖自己的资料。

## 第一次使用

在 Codex 中提供 PDF 附件或本地文件路径：

```text
$distill-senior-paper-mentor
参考论文在 /path/to/reference-papers/。
先学习这些论文的结构、术语、段落组织和讲故事方式，建立我的本地写作档案。
不要把原文、作者信息或阅读笔记上传到外部服务。
```

也可先在仓库目录导入文件：

```bash
python scripts/ingest_papers.py /path/to/first.pdf /path/to/second.md
```

目录输入会递归导入支持的文件。PDF 需要系统安装 `pdftotext`；HTML 需要 Python 的 `beautifulsoup4`。导入只负责保存和抽取，后续由 agent 阅读原文并建立档案。扫描 PDF 需要先 OCR。

## 建档后的请求

```text
$distill-senior-paper-mentor 审阅 /path/to/my-paper.pdf，重点检查贡献、叙事主线与实验支撑。先给意见。
```

```text
$distill-senior-paper-mentor 我的课题是……，已有结果是……，预算是……。提出可以检验的方向和最小实验。
```

```text
$distill-senior-paper-mentor 直接修改 /path/to/introduction.tex。按参考论文的叙事方法重组引言，保持事实、公式和引用键。
```

```text
$distill-senior-paper-mentor 解释这个实验设计为什么可能有混淆。
```

```text
$distill-senior-paper-mentor 今天实验失败了，我想先聊聊，暂时不要给我任务清单。
```

给建议不会自动改文件，明确要求“直接修改”才会执行改稿。个人论文与结果始终是事实依据，参考论文只提供可迁移的方法。

## 本地资料

`library/` 默认全部忽略，包含导入原文、抽取文本、索引、阅读卡片与写作档案。模板中的通用指引位于 `references/`，独立 agent 提示词位于 `agents/mentor.md`。公开分享模板时不要使用 `git add -f library`；分享定制资料应另建私有仓库并检查可见性。

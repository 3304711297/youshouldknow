#!/usr/bin/env bash
# 将根目录 Markdown 与 13 个中文分类复制到 docs/，满足 mkdocs 默认 docs_dir。
# build 与 deploy 两个 job 共用本脚本；新增分类只需在这里追加目录名。
set -euo pipefail

mkdir -p docs
cp README.md docs/index.md
for dir in "BIOS与固件" "CPU与延迟" "GPU与显示" "内存与存储" "内存超频" "显卡优化" "笔电相关" "系统知识" "系统调优与安全" "网络通信" "软件技巧" "项目导航" "验机相关"; do
  if [ -d "$dir" ]; then
    cp -r "$dir" "docs/$dir"
  fi
done

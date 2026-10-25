#!/usr/bin/env node
'use strict';

// 零依赖校验脚本：检查 README.md 选题简报结构与字段完整性，
// 并校验 docs/ROADMAP.md 的专题跟踪清单与 README 专题名称一一对应。

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const readmePath = path.join(root, 'README.md');
const roadmapPath = path.join(root, 'docs', 'ROADMAP.md');

const errors = [];

function fail(msg) {
  errors.push(msg);
}

function readFile(p) {
  try {
    return fs.readFileSync(p, 'utf8');
  } catch (e) {
    fail('无法读取文件: ' + p + ' (' + e.message + ')');
    return '';
  }
}

const readme = readFile(readmePath);
const roadmap = readFile(roadmapPath);

// 1. 必备二级小节
const requiredSections = ['选题简报', '专题跟踪', '来源与日期'];
for (const s of requiredSections) {
  if (!readme.includes('## ' + s)) {
    fail('README.md 缺少二级小节: ## ' + s);
  }
}

// 2. 选题条目不少于 5 条，且每条含四个字段
const topicBlocks = readme.split(/^### 选题 /m).slice(1);
if (topicBlocks.length < 5) {
  fail('选题条目不足 5 条，当前为 ' + topicBlocks.length + ' 条');
}

const fieldLabels = ['标题', '来源链接', '一句话摘要', '推荐理由'];
topicBlocks.forEach((block, i) => {
  const name = '选题 ' + (i + 1);
  for (const label of fieldLabels) {
    const re = new RegExp('^- ' + label + '：\\S', 'm');
    if (!re.test(block)) {
      fail(name + ' 缺少字段: ' + label);
    }
  }
  if (!/https?:\/\//.test(block)) {
    fail(name + ' 缺少来源链接 URL');
  }
});

// 3. 专题名称一致性：README 专题标题 vs ROADMAP 表格首列
function extractReadmeTopics(text) {
  const names = [];
  const re = /^### 专题[一二三四五六七八九十]+：(.+)$/gm;
  let m;
  while ((m = re.exec(text)) !== null) {
    names.push(m[1].trim());
  }
  return names;
}

function extractRoadmapTopics(text) {
  const names = [];
  const section = text.split('## 专题跟踪清单')[1];
  if (!section) return names;
  const lines = section.split('\n');
  for (const line of lines) {
    const m = line.match(/^\|\s*([^|]+?)\s*\|/);
    if (!m) continue;
    const cell = m[1].trim();
    if (cell === '专题名称' || /^-+$/.test(cell)) continue;
    names.push(cell);
  }
  return names;
}

const readmeTopics = extractReadmeTopics(readme);
const roadmapTopics = extractRoadmapTopics(roadmap);

if (readmeTopics.length === 0) {
  fail('README.md 未解析到任何专题名称');
}
if (roadmapTopics.length === 0) {
  fail('docs/ROADMAP.md 未解析到任何专题名称');
}

for (const t of readmeTopics) {
  if (!roadmapTopics.includes(t)) {
    fail('ROADMAP 缺少专题: ' + t);
  }
}
for (const t of roadmapTopics) {
  if (!readmeTopics.includes(t)) {
    fail('README 缺少专题: ' + t);
  }
}

if (errors.length > 0) {
  console.error('简报校验失败:');
  for (const e of errors) console.error('  - ' + e);
  process.exit(1);
}

console.log('简报校验通过: ' + topicBlocks.length + ' 条选题, ' + readmeTopics.length + ' 个专题');

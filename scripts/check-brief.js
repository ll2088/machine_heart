#!/usr/bin/env node
/**
 * 机器之心简报结构校验。
 *
 * 设计原则：期望值不硬编码，全部从单一事实来源动态读取，避免
 * 「README 25 条 vs 校验期望 22 条」「batch_index 15 条 vs BATCHES 12 条」
 * 这类漂移导致的确定性失败。
 *
 * 事实来源：
 * - 选题数：README.md 中 `### 选题 N：` 标题块数量。
 * - 去重键数：scripts/batch_index.py 的 ARTICLES 登记条数（正则解析）。
 * - BATCHES 第 2 节清单：docs/BATCHES.md 中 `- \`machine_heart:<mid>:<idx>\`` 行。
 *
 * 校验项：
 * 1. README 选题数与 batch_index.py 登记条数可核对（选题数 >= 去重键数）。
 * 2. BATCHES.md 第 2 节硬编码清单条数与 batch_index.py 登记条数一致。
 * 3. BATCHES.md 第 2 节清单内容与 batch_index.py 的 known_keys() 顺序一致。
 * 4. README 与 ROADMAP 的专题名称逐条对应，无孤立条目。
 * 5. 三篇新文章关键词在 BATCHES.md 与 README.md 中可命中。
 */

'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const README = path.join(ROOT, 'README.md');
const BATCHES = path.join(ROOT, 'docs', 'BATCHES.md');
const ROADMAP = path.join(ROOT, 'docs', 'ROADMAP.md');
const BATCH_INDEX = path.join(ROOT, 'scripts', 'batch_index.py');

const errors = [];

function readFileOrFail(file) {
  try {
    return fs.readFileSync(file, 'utf8');
  } catch (err) {
    errors.push(`无法读取 ${path.relative(ROOT, file)}: ${err.message}`);
    return null;
  }
}

/** 从 README.md 统计 `### 选题 N：` 标题块数量。 */
function countTopics(readme) {
  const matches = readme.match(/^### 选题 \d+：/gm);
  return matches ? matches.length : 0;
}

/** 从 batch_index.py 的 ARTICLES 元组统计 Article(...) 登记条数。 */
function countIndexedArticles(source) {
  const matches = source.match(/Article\(/g);
  return matches ? matches.length : 0;
}

/** 从 batch_index.py 的 ARTICLES 提取去重键，顺序与声明一致。 */
function extractIndexedKeys(source) {
  const keys = [];
  const re = /Article\(\s*'([0-9]+)'\s*,\s*(\d+)\s*,/g;
  let m;
  while ((m = re.exec(source)) !== null) {
    keys.push(`machine_heart:${m[1]}:${m[2]}`);
  }
  return keys;
}

/** 从 docs/BATCHES.md 第 2 节提取硬编码去重键清单。 */
function extractBatchesSectionTwoKeys(batches) {
  const marker = '## 2. 去重键契约';
  const start = batches.indexOf(marker);
  if (start === -1) {
    errors.push('docs/BATCHES.md 缺少「## 2. 去重键契约」小节');
    return [];
  }
  const rest = batches.slice(start + marker.length);
  const end = rest.indexOf('## 3.');
  const section = end === -1 ? rest : rest.slice(0, end);
  const keys = [];
  for (const line of section.split('\n')) {
    const m = line.match(/^\s*-\s*`(machine_heart:[0-9]+:[0-9]+)`\s*$/);
    if (m) {
      keys.push(m[1]);
    }
  }
  return keys;
}

/** 从 README.md 提取专题名称（`### 专题N：名称` 或 `### 专题N：名称`）。 */
function extractReadmeTopics(readme) {
  const names = [];
  const re = /^### 专题[一二三四五六七八九十]+：(.+)$/gm;
  let m;
  while ((m = re.exec(readme)) !== null) {
    names.push(m[1].trim());
  }
  return names;
}

/** 从 docs/ROADMAP.md 的专题跟踪清单表格提取专题名称。 */
function extractRoadmapTopics(roadmap) {
  const names = [];
  const marker = '## 专题跟踪清单';
  const start = roadmap.indexOf(marker);
  if (start === -1) {
    errors.push('docs/ROADMAP.md 缺少「## 专题跟踪清单」小节');
    return names;
  }
  const section = roadmap.slice(start);
  for (const line of section.split('\n')) {
    const m = line.match(/^\|\s*([^|]+?)\s*\|/);
    if (!m) continue;
    const name = m[1].trim();
    if (name === '专题名称' || name.startsWith('---') || name === '') continue;
    names.push(name);
  }
  return names;
}

function main() {
  const readme = readFileOrFail(README);
  const batches = readFileOrFail(BATCHES);
  const roadmap = readFileOrFail(ROADMAP);
  const batchIndex = readFileOrFail(BATCH_INDEX);

  if (readme === null || batches === null || roadmap === null || batchIndex === null) {
    report();
    return 1;
  }

  const topicCount = countTopics(readme);
  const indexedCount = countIndexedArticles(batchIndex);
  const indexedKeys = extractIndexedKeys(batchIndex);
  const sectionTwoKeys = extractBatchesSectionTwoKeys(batches);

  // 1. 选题数与登记条数可核对：选题数应不少于去重键数。
  if (topicCount < indexedCount) {
    errors.push(
      `选题条目数（${topicCount}）少于 batch_index.py 登记条数（${indexedCount}）`
    );
  }

  // 2. BATCHES 第 2 节清单条数与 batch_index.py 登记条数一致。
  if (sectionTwoKeys.length !== indexedCount) {
    errors.push(
      `batch_index.py 登记条数与 BATCHES 硬编码不一致: ${indexedCount} vs ${sectionTwoKeys.length}`
    );
    const indexedSet = new Set(indexedKeys);
    const sectionSet = new Set(sectionTwoKeys);
    const missingInBatches = indexedKeys.filter((key) => !sectionSet.has(key));
    const extraInBatches = sectionTwoKeys.filter((key) => !indexedSet.has(key));
    if (missingInBatches.length > 0) {
      errors.push(`BATCHES 第 2 节缺失的键: ${missingInBatches.join(', ')}`);
    }
    if (extraInBatches.length > 0) {
      errors.push(`BATCHES 第 2 节多余的键: ${extraInBatches.join(', ')}`);
    }
  }

  // 3. 第 2 节清单内容与 known_keys() 顺序一致。
  if (indexedKeys.length !== indexedCount) {
    errors.push(
      `batch_index.py 解析出的去重键数（${indexedKeys.length}）与 Article 登记数（${indexedCount}）不一致`
    );
  }
  if (sectionTwoKeys.length === indexedKeys.length) {
    for (let i = 0; i < indexedKeys.length; i += 1) {
      if (sectionTwoKeys[i] !== indexedKeys[i]) {
        errors.push(
          `BATCHES 第 2 节第 ${i + 1} 个去重键与 batch_index.py 顺序不一致: ${sectionTwoKeys[i]} vs ${indexedKeys[i]}`
        );
        break;
      }
    }
  }

  // 4. README 与 ROADMAP 专题名称逐条对应。
  const readmeTopics = extractReadmeTopics(readme);
  const roadmapTopics = extractRoadmapTopics(roadmap);
  if (readmeTopics.length === 0) {
    errors.push('README.md 未找到专题名称（### 专题N：名称）');
  }
  if (roadmapTopics.length === 0) {
    errors.push('docs/ROADMAP.md 未找到专题跟踪清单条目');
  }
  const readmeSet = new Set(readmeTopics);
  const roadmapSet = new Set(roadmapTopics);
  for (const name of readmeSet) {
    if (!roadmapSet.has(name)) {
      errors.push(`README 专题「${name}」在 ROADMAP 专题跟踪清单中缺失`);
    }
  }
  for (const name of roadmapSet) {
    if (!readmeSet.has(name)) {
      errors.push(`ROADMAP 专题「${name}」在 README 专题跟踪中缺失`);
    }
  }

  // 5. 三篇新文章关键词可命中。
  const keywords = ['Sage S2.1 Flash', 'DeepMind', 'AI音乐'];
  for (const kw of keywords) {
    if (!batches.includes(kw)) {
      errors.push(`docs/BATCHES.md 未命中关键词「${kw}」`);
    }
    if (!readme.includes(kw)) {
      errors.push(`README.md 未命中关键词「${kw}」`);
    }
  }

  report();
  return errors.length === 0 ? 0 : 1;
}

function report() {
  if (errors.length === 0) {
    console.log('简报校验通过');
    return;
  }
  console.error('简报校验失败:');
  for (const err of errors) {
    console.error(`  - ${err}`);
  }
}

process.exit(main());

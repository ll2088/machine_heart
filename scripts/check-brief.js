#!/usr/bin/env node
'use strict';

// 零依赖校验脚本：检查 README.md 选题简报结构与字段完整性，
// 并校验 docs/ROADMAP.md 的专题跟踪清单与 README 专题名称一一对应。
// MACHINE_HEART_ROOT 契约：仅接受 POSIX 风格相对路径；Windows 调用方使用 / 分隔。

const fs = require('fs');
const path = require('path');

const root = getValidatedRoot();
const readmePath = path.join(root, 'README.md');
const roadmapPath = path.join(root, 'docs', 'ROADMAP.md');
const batchPath = path.join(root, 'docs', 'BATCHES.md');
const verificationPath = path.join(root, 'docs', 'VERIFICATION.md');

const errors = [];

// 明确拒绝的隐藏/敏感目录清单；任何以点开头的路径段也一并拒绝。
const HIDDEN_OR_SENSITIVE_SEGMENTS = new Set([
  '.git',
  '.github',
  '.hg',
  '.svn',
  '.idea',
  '.vscode',
  'node_modules',
  '__pycache__',
]);

function fail(msg) {
  errors.push(msg);
}

function getValidatedRoot() {
  const actualRoot = fs.realpathSync(path.resolve(__dirname, '..'));
  const envRoot = process.env.MACHINE_HEART_ROOT;

  if (!envRoot) {
    return actualRoot;
  }

  if (path.isAbsolute(envRoot)) {
    fail('MACHINE_HEART_ROOT 必须是相对于仓库根目录的相对路径，不能是绝对路径: ' + envRoot);
    return actualRoot;
  }

  const normalized = path.normalize(envRoot);
  if (normalized === '..' || normalized.startsWith('..' + path.sep)) {
    fail('MACHINE_HEART_ROOT 不能使用 .. 逃逸仓库根目录: ' + envRoot);
    return actualRoot;
  }

  if (envRoot.includes('\\')) {
    fail('MACHINE_HEART_ROOT 只能使用 / 作为路径分隔符，不能包含反斜杠: ' + envRoot);
    return actualRoot;
  }

  const segments = normalized.split(path.sep);
  if (segments.some((segment) => segment.startsWith('.') || HIDDEN_OR_SENSITIVE_SEGMENTS.has(segment))) {
    fail('MACHINE_HEART_ROOT 不能指向隐藏目录或敏感路径: ' + envRoot);
    return actualRoot;
  }

  const candidate = path.resolve(actualRoot, envRoot);
  let realCandidate;
  try {
    realCandidate = fs.realpathSync(candidate);
  } catch (e) {
    fail('MACHINE_HEART_ROOT 无法解析: ' + envRoot + ' (' + e.message + ')');
    return actualRoot;
  }

  const relative = path.relative(actualRoot, realCandidate);
  if (relative !== '' && (relative.startsWith('..') || path.isAbsolute(relative))) {
    fail('MACHINE_HEART_ROOT 越界或符号链接逃逸: ' + envRoot + ' -> ' + realCandidate);
    return actualRoot;
  }

  const realSegments = relative === '' ? [] : relative.split(path.sep);
  if (realSegments.some((segment) => segment.startsWith('.') || HIDDEN_OR_SENSITIVE_SEGMENTS.has(segment))) {
    fail('MACHINE_HEART_ROOT 不能指向隐藏目录或敏感路径: ' + envRoot + ' -> ' + realCandidate);
    return actualRoot;
  }

  let realStat;
  try {
    realStat = fs.statSync(realCandidate);
  } catch (e) {
    fail('MACHINE_HEART_ROOT 解析后无法读取目录状态: ' + envRoot + ' -> ' + realCandidate + ' (' + e.message + ')');
    return actualRoot;
  }
  if (!realStat.isDirectory()) {
    fail('MACHINE_HEART_ROOT 必须指向目录而非文件: ' + envRoot + ' -> ' + realCandidate);
    return actualRoot;
  }

  return realCandidate;
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
const batches = readFile(batchPath);
const verification = readFile(verificationPath);

// 1. 必备二级小节
const requiredSections = ['选题简报', '专题跟踪', '来源与日期'];
for (const s of requiredSections) {
  if (!readme.includes('## ' + s)) {
    fail('README.md 缺少二级小节: ## ' + s);
  }
}

// 2. 选题条目数必须与 batch_index.py 实际登记条数一致（唯一数据源，避免硬编码漂移）。
const topicBlocks = readme.split(/^### 选题 /m).slice(1);
if (topicBlocks.length !== actualBatchKeys.length) {
  fail('选题条目数应为 ' + actualBatchKeys.length + ' 条（与 batch_index.py 登记一致），当前为 ' + topicBlocks.length + ' 条');
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

// 4. 读取 batch_index.py 的 ARTICLES，作为去重键与选题计数的唯一数据源。
const batchIndexPy = readFile(path.join(root, 'scripts', 'batch_index.py'));
const articleRe = /Article\('(\d+)',\s*(\d+),\s*'([^']*)',\s*'([^']*)',\s*'(https?:\/\/[^']+)'(?:,\s*'([^']*)')?\)/g;
const actualBatchKeys = [];
let match;
while ((match = articleRe.exec(batchIndexPy)) !== null) {
  const mid = match[1];
  const idx = Number(match[2]);
  const title = match[3];
  const url = match[5];
  const key = 'machine_heart:' + mid + ':' + idx;
  actualBatchKeys.push(key);
  if (!batches.includes(key)) {
    fail('docs/BATCHES.md 缺少 batch_index.py 中的去重键: ' + key);
  }
  if (!readme.includes(title)) {
    fail('README.md 缺少 batch_index.py 中的标题: ' + title);
  }
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') {
      fail('非法 URL 协议: ' + url);
    }
  } catch (e) {
    fail('非法 URL: ' + url + ' (' + e.message + ')');
  }
}
if (actualBatchKeys.length === 0) {
  fail('batch_index.py 未解析到任何去重键');
}
if (new Set(actualBatchKeys).size !== actualBatchKeys.length) {
  fail('batch_index.py 存在重复去重键');
}

// 6. 零第三方依赖自检：package.json 不得声明 dependencies/devDependencies。
const packageJsonText = readFile(path.join(root, 'package.json'));
try {
  const pkg = JSON.parse(packageJsonText);
  const deps = Object.keys(pkg.dependencies || {});
  const devDeps = Object.keys(pkg.devDependencies || {});
  if (deps.length > 0 || devDeps.length > 0) {
    fail('package.json 引入了第三方依赖: ' + deps.concat(devDeps).join(', '));
  }
} catch (e) {
  fail('package.json 解析失败: ' + e.message);
}

// 7. 文档一致性：VERIFICATION.md 必须包含可执行验收命令与性能不作结论声明。
const requiredVerificationSnippets = [
  'npm test',
  'npm run test:python',
  'MACHINE_HEART_ROOT',
  '不做性能结论',
  'CI 维度映射',
];
for (const snippet of requiredVerificationSnippets) {
  if (!verification.includes(snippet)) {
    fail('docs/VERIFICATION.md 缺少关键验收内容: ' + snippet);
  }
}

const requiredMainlines = ['具身智能与机器人', '前沿模型与架构', '产业与生态'];
for (const name of requiredMainlines) {
  if (!batches.includes(name)) {
    fail('docs/BATCHES.md 缺少主线: ' + name);
  }
}

const requiredAttributes = ['技术', '观点'];
for (const name of requiredAttributes) {
  if (!batches.includes(name)) {
    fail('docs/BATCHES.md 缺少属性: ' + name);
  }
}

if (errors.length > 0) {
  console.error('简报校验失败:');
  for (const e of errors) console.error('  - ' + e);
  process.exit(1);
}

console.log('简报校验通过: ' + topicBlocks.length + ' 条选题, ' + readmeTopics.length + ' 个专题, ' + actualBatchKeys.length + ' 个去重键, 文档一致性通过');

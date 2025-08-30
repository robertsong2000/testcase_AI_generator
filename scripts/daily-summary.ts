// scripts/daily-summary.ts
// 支持自动加载 .env 文件
// 运行前：确保已设置环境变量，或在项目根目录创建 .env 文件

import { execSync } from "node:child_process";
import https from "node:https";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

// 自动加载 .env 文件
function loadEnv() {
  try {
    const envPath = resolve(process.cwd(), '.env');
    const envContent = readFileSync(envPath, 'utf8');
    
    envContent.split('\n').forEach(line => {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        const [key, ...valueParts] = trimmed.split('=');
        if (key && valueParts.length > 0) {
          const value = valueParts.join('=').trim();
          if (!process.env[key]) {
            process.env[key] = value;
          }
        }
      }
    });
    console.log("✅ 已加载 .env 文件");
  } catch (error) {
    // .env 文件不存在时跳过
    console.log("ℹ️  未找到 .env 文件，使用系统环境变量");
  }
}

// 加载环境变量
loadEnv();

// ------- 环境变量 -------
const OPENAI_BASE_URL = process.env.OPENAI_BASE_URL || "https://api.openai.com";
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || "";
const LARK_WEBHOOK_URL = process.env.LARK_WEBHOOK_URL || "";
const REPO = process.env.REPO || ""; // e.g. "org/repo"
const REPO_PATH = process.env.REPO_PATH || "."; // 仓库路径配置
const MODEL_NAME = process.env.MODEL_NAME || "gpt-4.1-mini";
const PER_BRANCH_LIMIT = parseInt(process.env.PER_BRANCH_LIMIT || "200", 10);
const DIFF_CHUNK_MAX_CHARS = parseInt(
  process.env.DIFF_CHUNK_MAX_CHARS || "80000",
  10,
);

// 调试信息
const USE_COMMIT_INFO_ONLY = process.env.USE_COMMIT_INFO_ONLY === "true";
console.log(`🔍 调试信息:`);
console.log(`   工作目录: ${process.cwd()}`);
console.log(`   配置的仓库: ${REPO}`);
console.log(`   仓库路径: ${REPO_PATH}`);
console.log(`   回溯天数: ${process.env.DAYS_BACK || "1"}`);
console.log(`   使用提交信息模式: ${USE_COMMIT_INFO_ONLY ? '是' : '否'}`);
console.log(`   Git仓库存在: ${require("node:fs").existsSync('.git') ? '是' : '否'}`);

if (!OPENAI_API_KEY) {
  console.error("Missing OPENAI_API_KEY");
  process.exit(1);
}

// 切换到指定仓库路径
if (REPO_PATH !== ".") {
  const fullPath = require("node:path").resolve(process.cwd(), REPO_PATH);
  console.log(`🔍 切换到仓库路径: ${fullPath}`);
  
  if (!require("node:fs").existsSync(fullPath)) {
    console.error(`❌ 仓库路径不存在: ${fullPath}`);
    process.exit(1);
  }
  
  if (!require("node:fs").existsSync(require("node:path").join(fullPath, '.git'))) {
    console.error(`❌ 指定路径不是Git仓库: ${fullPath}`);
    process.exit(1);
  }
  
  process.chdir(fullPath);
  console.log(`✅ 已切换到仓库目录: ${process.cwd()}`);
}

// ------- 工具函数 -------
function sh(cmd: string) {
  return execSync(cmd, {
    stdio: ["ignore", "pipe", "pipe"],
    encoding: "utf8",
  }).trim();
}

function safeArray<T>(xs: T[] | undefined | null) {
  return Array.isArray(xs) ? xs : [];
}

// ------- 分支与提交收集（覆盖 origin/* 全分支）-------
// 支持自定义天数，通过 DAYS_BACK 环境变量设置
const DAYS_BACK = parseInt(process.env.DAYS_BACK || "1", 10);
const since = DAYS_BACK === 1 ? "midnight" : `${DAYS_BACK}.days.ago`;
const until = "now";
console.log(`🔍 时间范围: ${since} 到 ${until}`);

// 拉全远端（建议在 workflow 里执行：git fetch --all --prune --tags）
// 这里再次保险 fetch 一次，避免本地调试遗漏
try {
  sh(`git fetch --all --prune --tags`);
} catch {
  // ignore
}

// 列出所有 origin/* 远端分支，排除 origin/HEAD
console.log(`🔍 获取远程分支列表...`);
const remoteBranches = sh(
  `git for-each-ref --format="%(refname:short)" refs/remotes/origin | grep -v "^origin/HEAD$" || true`,
)
  .split("\n")
  .map((s) => s.trim())
  .filter(Boolean);
console.log(`   发现远程分支: ${remoteBranches.join(', ') || '无'}`);

// 分支白名单/黑名单（如需）：在此可用正则筛选 remoteBranches

type CommitMeta = {
  sha: string;
  title: string;
  author: string;
  url: string;
  branches: string[]; // 该提交归属的分支集合
};

const branchToCommits = new Map<string, string[]>();
console.log(`🔍 分析每个分支的提交...`);
for (const rb of remoteBranches) {
  const cmd = `git log ${rb} --no-merges --since="${since}" --until="${until}" --pretty=format:%H --reverse || true`;
  console.log(`   执行命令: ${cmd}`);
  const list = sh(cmd)
    .split("\n")
    .map((s) => s.trim())
    .filter(Boolean);
  console.log(`   分支 ${rb}: 找到 ${list.length} 个提交`);
  branchToCommits.set(rb, list.slice(-PER_BRANCH_LIMIT));
}

// 反向映射：提交 → 出现的分支集合
const shaToBranches = new Map<string, Set<string>>();
for (const [rb, shas] of branchToCommits) {
  for (const sha of shas) {
    if (!shaToBranches.has(sha)) shaToBranches.set(sha, new Set());
    shaToBranches.get(sha)!.add(rb);
  }
}

// 在所有分支联合视图中获取今天的提交，按时间从早到晚，再与 shaToBranches 交集过滤
const totalCmd = `git log --no-merges --since="${since}" --until="${until}" --all --pretty=format:%H --reverse || true`;
console.log(`🔍 执行总查询命令: ${totalCmd}`);
const allShasOrdered = sh(totalCmd)
  .split("\n")
  .map((s) => s.trim())
  .filter(Boolean);
console.log(`   所有分支共找到 ${allShasOrdered.length} 个提交`);

const seen = new Set<string>();
const commitShas = allShasOrdered.filter((sha) => {
  if (seen.has(sha)) return false;
  if (!shaToBranches.has(sha)) return false; // 仅统计出现在 origin/* 的提交
  seen.add(sha);
  return true;
});

if (commitShas.length === 0) {
  console.log(`📭 最近${DAYS_BACK}天所有分支均无有效提交。结束。`);
  process.exit(0);
}

const serverUrl = "https://github.com";

const commitMetas: CommitMeta[] = commitShas.map((sha) => {
  const title = sh(`git show -s --format=%s ${sha}`);
  const author = sh(`git show -s --format=%an ${sha}`);
  const url = REPO
    ? `${serverUrl}/${REPO}/commit/${sha}`
    : `${serverUrl}/commit/${sha}`;
  const branches = Array.from(shaToBranches.get(sha) || []).sort();
  return { sha, title, author, url, branches };
});

// ------- 仅使用commit信息（不包含diff） -------
function getCommitInfoOnly(sha: string): string {
  try {
    const title = sh(`git show -s --format=%s ${sha}`);
    const body = sh(`git show -s --format=%b ${sha}`);
    const author = sh(`git show -s --format=%an ${sha}`);
    const date = sh(`git show -s --format=%cd ${sha}`);
    const files = sh(`git show --name-only --format="" ${sha}`).split('\n').filter(Boolean).join(', ');
    
    return `提交标题: ${title}
作者: ${author}
日期: ${date}
涉及文件: ${files}

${body ? `提交说明:\n${body}` : ''}`;
  } catch (error) {
    return `获取提交信息失败: ${error}`;
  }
}

// ------- 原有diff处理函数（保留兼容性） -------
const FILE_EXCLUDES = [
  "package-lock.json",
  "yarn.lock",
  "pnpm-lock.yaml",
  "*.min.js",
  "*.min.css",
  "dist/",
  "build/",
  "node_modules/",
];

function getParentSha(sha: string): string {
  return sh(`git rev-parse ${sha}^`);
}

function getDiff(sha: string): string {
  const parent = getParentSha(sha);
  const excludeFlags = FILE_EXCLUDES.flatMap((pattern) => [
    "--",
    ":(exclude)" + pattern,
  ]).join(" ");
  return sh(`git diff ${parent} ${sha} --no-renames --binary ${excludeFlags}`);
}

function splitPatchByFile(patch: string): string[] {
  const parts: string[] = [];
  let current: string[] = [];
  for (const line of patch.split("\n")) {
    if (line.startsWith("diff --git")) {
      if (current.length) parts.push(current.join("\n"));
      current = [line];
    } else {
      current.push(line);
    }
  }
  if (current.length) parts.push(current.join("\n"));
  return parts;
}

// 简化分片处理（commit信息通常较短）
function chunkBySize(parts: string[], limit = DIFF_CHUNK_MAX_CHARS): string[] {
  return parts.length > 0 ? [parts.join('\n\n')] : [];
}

// ------- OpenAI Chat API -------
type ChatPayload = {
  model: string;
  messages: { role: "system" | "user" | "assistant"; content: string }[];
  temperature?: number;
  enable_thinking?: boolean;
  stream?: boolean;
};

async function chat(prompt: string): Promise<string> {
  const payload: ChatPayload = {
    model: MODEL_NAME,
    messages: [{ role: "user", content: prompt }],
    temperature: 0.2,
    enable_thinking: false, // 阿里通义千问要求非流式调用时禁用思考模式
    stream: false, // 使用非流式调用
  };
  const body = JSON.stringify(payload);

  return new Promise((resolve, reject) => {
    // 清理可能的零宽空格和其他不可见字符
    const cleanUrl = OPENAI_BASE_URL.replace(/[\u200B-\u200D\uFEFF]/g, '').trim();
    const url = new URL(cleanUrl);
    
    // 阿里通义千问兼容模式：DashScope使用/v1/chat/completions
    const path = '/compatible-mode/v1/chat/completions';
    
    const options = {
      hostname: url.hostname,
      port: url.protocol === 'https:' ? 443 : 80,
      path: path,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${OPENAI_API_KEY}`,
        "Content-Length": Buffer.byteLength(body),
      },
    };
    
    const req = https.request(options,
      (res) => {
        let data = "";
        res.on("data", (d) => (data += d));
        res.on("end", () => {
          try {
            if (
              res.statusCode &&
              res.statusCode >= 200 &&
              res.statusCode < 300
            ) {
              const json = JSON.parse(data);
              const content =
                json?.choices?.[0]?.message?.content?.trim() || "";
              resolve(content);
            } else {
              reject(new Error(`OpenAI HTTP ${res.statusCode}: ${data}`));
            }
          } catch (e) {
            reject(e);
          }
        });
      },
    );
    req.on("error", reject);
    req.write(body);
    req.end();
  });
}

// ------- 提示词 -------
function commitChunkPrompt(
  meta: CommitMeta,
  partIdx: number,
  total: number,
  content: string,
  useCommitInfoOnly: boolean
) {
  if (useCommitInfoOnly) {
    return `你是一名资深工程师与发布经理。请基于以下提交信息，用中文输出结构化摘要：

提交信息：
- SHA: ${meta.sha}
- 标题: ${meta.title}
- 作者: ${meta.author}
- 分支: ${meta.branches.join(", ")}
- 链接: ${meta.url}

提交详情：
${content}

要求输出：
1) 变更要点（面向工程师与产品）：基于提交信息总结主要改动与意图
2) 影响范围：模块/功能/配置等可能影响的部分
3) 风险&回滚点：基于改动内容评估潜在风险
4) 测试建议：针对此改动的测试重点
注意：基于提交信息合理推断，不要过度臆测；如果只是文档更新或配置调整也请明确指出。`;
  } else {
    return `你是一名资深工程师与发布经理。以下是提交 ${meta.sha.slice(0, 7)}（${meta.title}）的 diff 片段（第 ${partIdx}/${total} 段），请用中文输出结构化摘要：

提交信息：
- SHA: ${meta.sha}
- 标题: ${meta.title}
- 作者: ${meta.author}
- 分支: ${meta.branches.join(", ")}
- 链接: ${meta.url}

要求输出：
1) 变更要点（面向工程师与产品）：列出此片段涉及的主要改动与意图
2) 影响范围：模块/接口/关键文件
3) 风险&回滚点
4) 测试建议
注意：仅基于当前片段，不要臆测；不要贴长代码；如果只是格式化/重命名也请明确指出。

=== DIFF PART BEGIN ===
${content}
=== DIFF PART END ===`;
  }
}

function commitMergePrompt(meta: CommitMeta, parts: string[]) {
  const joined = parts.map((p, i) => `【片段${i + 1}】\n${p}`).join("\n\n");
  return `下面是提交 ${meta.sha.slice(0, 7)} 的各片段小结，请合并为**单条提交**的最终摘要（中文），输出以下小节：
- 变更概述（不超过5条要点）
- 影响范围（模块/接口/配置）
- 风险与回滚点
- 测试建议
- 面向用户的可见影响（如有）

请避免重复、合并同类项，标注“可能不完整”当某些片段缺失或被截断。

=== 片段小结集合 BEGIN ===
${joined}
=== 片段小结集合 END ===`;
}

function dailyMergePrompt(
  dateLabel: string,
  items: { meta: CommitMeta; summary: string }[],
  repo: string,
) {
  const body = items
    .map(
      (it) =>
        `[${it.meta.sha.slice(0, 7)}] ${it.meta.title} — ${it.meta.author} — ${it.meta.branches.join(", ")}
${it.summary}`,
    )
    .join("\n\n---\n\n");

  const periodText = parseInt(process.env.DAYS_BACK || "1", 10) === 1 ? "今日" : `最近${process.env.DAYS_BACK || "1"}天`;

  return `请将以下“各提交摘要”整合成**${periodText}开发变更日报（中文）**，输出结构如下：
# ${dateLabel} ${periodText}开发变更日报（${repo})
1. ${periodText}概览（不超过5条）
2. **按分支**的关键改动清单（每条含模块/影响、是否潜在破坏性）
3. 跨分支风险与回滚策略（如同一提交在多个分支、存在 cherry-pick/divergence）
4. 建议测试与验证清单
5. 其他备注（如重构/依赖升级/仅格式化）

=== 提交摘要 BEGIN ===
${body}
=== 提交摘要 END ===`;
}

// ------- 飞书 Webhook -------
async function postToLark(text: string) {
  if (!LARK_WEBHOOK_URL) {
    console.log("LARK_WEBHOOK_URL 未配置，以下为最终日报文本：\n\n" + text);
    return;
  }
  const payload = JSON.stringify({ msg_type: "text", content: { text } });
  await new Promise<void>((resolve, reject) => {
    const url = new URL(LARK_WEBHOOK_URL);
    const req = https.request(
      {
        hostname: url.hostname,
        path: url.pathname + url.search,
        method: "POST",
        headers: { "Content-Type": "application/json" },
      },
      (res) => {
        res.on("data", () => {});
        res.on("end", () => resolve());
      },
    );
    req.on("error", reject);
    req.write(payload);
    req.end();
  });
}

// ------- 主流程 -------
(async () => {
  const perCommitFinal: { meta: CommitMeta; summary: string }[] = [];

  for (const meta of commitMetas) {
    let content: string;
    let parts: string[];

    if (USE_COMMIT_INFO_ONLY) {
      // 使用commit信息模式
      content = getCommitInfoOnly(meta.sha);
      if (!content || !content.trim()) {
        perCommitFinal.push({
          meta,
          summary: `（无法获取提交信息或提交为空）`,
        });
        continue;
      }
      parts = chunkBySize([content], DIFF_CHUNK_MAX_CHARS);
    } else {
      // 使用diff模式（原有逻辑）
      try {
        const fullPatch = getDiff(meta.sha);
        if (!fullPatch.trim()) {
          content = "（无代码变更）";
          parts = [content];
        } else {
          const fileParts = splitPatchByFile(fullPatch);
          parts = chunkBySize(fileParts, DIFF_CHUNK_MAX_CHARS);
        }
      } catch (error) {
        content = `（获取diff失败：${error}）`;
        parts = [content];
      }
    }

    const partSummaries: string[] = [];
    for (let i = 0; i < parts.length; i++) {
      const prompt = commitChunkPrompt(meta, i + 1, parts.length, parts[i], USE_COMMIT_INFO_ONLY);
      try {
        const sum = await chat(prompt);
        partSummaries.push(sum || `（摘要为空）`);
      } catch (e: any) {
        partSummaries.push(`（调用失败：${String(e)}）`);
      }
    }

    // 合并为“单提交摘要”
    let merged = "";
    try {
      merged = await chat(commitMergePrompt(meta, partSummaries, USE_COMMIT_INFO_ONLY));
    } catch (e: any) {
      merged = partSummaries.join("\n\n");
    }

    perCommitFinal.push({ meta, summary: merged });
  }

  // 当地日期标签 YYYY-MM-DD
  const todayLabel = new Date().toLocaleDateString("en-CA", {
    timeZone: "America/Los_Angeles",
  });

  // 汇总“当日总览”
  let daily = "";
  try {
    daily = await chat(
      dailyMergePrompt(todayLabel, perCommitFinal, REPO || "repository"),
    );
  } catch (e: any) {
    daily =
      `（当日汇总失败，以下为逐提交原始小结拼接）\n\n` +
      perCommitFinal
        .map(
          (it) =>
            `[${it.meta.sha.slice(0, 7)}] ${it.meta.title} — ${it.meta.branches.join(", ")}\n${it.summary}`,
        )
        .join("\n\n---\n\n");
  }

  // 添加通知关键字并发送飞书
  const notificationKeyword = "【每日代码提交摘要】";
  const finalMessage = `${notificationKeyword}\n\n${daily}`;
  
  console.log("\n" + "=".repeat(50));
  console.log("📋 生成的日报内容：");
  console.log("=".repeat(50));
  console.log(finalMessage);
  console.log("=".repeat(50));
  
  await postToLark(finalMessage);
  console.log("✅ 已发送飞书日报。");
})().catch((err) => {
  console.error(err);
  process.exit(1);
});

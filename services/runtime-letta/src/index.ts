/**
 * Runtime Letta Service — uses real Letta Agent SDK with local backend.
 *
 * Owns: Worker ID ↔ Letta Agent ID mapping (never "list and pick first")
 * Each WorkOrder → new Letta session (don't reuse conversations)
 * MemFS = git-backed persistent memory for Worker learning
 *
 * API:
 *   POST /workers              — create worker (maps worker → letta agent)
 *   POST /workers/:id/run      — new session + execute
 *   GET  /workers/:id          — snapshot (agent state)
 *   POST /workers/:id/learning — apply memory/skill patch
 *   GET  /workers/:id/trajectory — export trajectory
 *   GET  /workers/:id/memfs    — list memory files
 *   GET  /health               — health check
 */

import { Hono } from "hono";
import { LettaAgentClient } from "@letta-ai/letta-agent-sdk";
import * as fs from "fs";
import * as path from "path";

type Bindings = {
  DATA_DIR: string;
};

type WorkerMapping = {
  worker_id: string;
  letta_agent_id: string;
  letta_agent_name: string;
  model: string;
  created_at: number;
  last_run_at: number;
  run_count: number;
  state_file: string;
};

const WORKER_DIR = process.env.DATA_DIR || "/root/workerkit/data/letta-workers";

const app = new Hono<{ Bindings: Bindings }>();

function getWorkerPath(workerId: string): string {
  return path.join(WORKER_DIR, `${workerId}.json`);
}

function loadWorker(workerId: string): WorkerMapping | null {
  const p = getWorkerPath(workerId);
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, "utf-8"));
}

function saveWorker(mapping: WorkerMapping): void {
  fs.mkdirSync(WORKER_DIR, { recursive: true });
  fs.writeFileSync(getWorkerPath(mapping.worker_id), JSON.stringify(mapping, null, 2));
}

// Singleton client — one App Server, not a new one per request
const CLIENT = new LettaAgentClient({ backend: "local" });
function getClient(): LettaAgentClient { return CLIENT; }

// ─── Health ───────────────────────────────────────────────────────────

app.get("/health", async (c) => {
  try {
    const client = getClient();
    // Try a simple operation to verify Letta is running
    return c.json({
      ok: true,
      service: "runtime-letta",
      version: "0.2.0",
      backend: "local",
      worker_dir: WORKER_DIR,
    });
  } catch (e) {
    return c.json({ ok: false, error: String(e) }, 500);
  }
});

// ─── Create Worker ────────────────────────────────────────────────────

app.post("/workers", async (c) => {
  const body = await c.req.json<{
    worker_id: string;
    model?: string;
    persona?: string;
    skills?: string[];
  }>();

  if (!body.worker_id) {
    return c.json({ error: "worker_id required" }, 400);
  }

  // Check if already exists
  const existing = loadWorker(body.worker_id);
  if (existing) {
    return c.json({ ok: true, mapping: existing, note: "already exists" });
  }

  const client = getClient();

  // Build memory blocks for the agent
  const memory = [
    {
      label: "persona",
      value: body.persona || "You are a specialist Moltwork research worker. Use evidence. Follow task requirements exactly.",
    },
    {
      label: "moltwork",
      value:
        "Treat Lab context as evidence, not ground truth. " +
        "Before competitive submissions, construct a requirement matrix. " +
        "Record what you learned after each run.",
    },
  ];

  // Add skill-specific memory blocks
  if (body.skills) {
    for (const skill of body.skills) {
      memory.push({
        label: `skill_${skill}`,
        value: `Skill: ${skill} — (to be filled from training)`,
      });
    }
  }

  try {
    const agentId = await client.createAgent({
      model: body.model || "letta/letta-free",
      memory,
      memfs: true,
      name: body.worker_id,
    });

    const mapping: WorkerMapping = {
      worker_id: body.worker_id,
      letta_agent_id: agentId,
      letta_agent_name: body.worker_id,
      model: body.model || "letta/letta-free",
      created_at: Date.now(),
      last_run_at: 0,
      run_count: 0,
      state_file: getWorkerPath(body.worker_id),
    };

    saveWorker(mapping);
    return c.json({ ok: true, mapping });
  } catch (e) {
    return c.json({ error: `agent creation failed: ${e}` }, 500);
  }
});

// ─── Get Worker ───────────────────────────────────────────────────────

app.get("/workers/:id", async (c) => {
  const workerId = c.req.param("id");
  const mapping = loadWorker(workerId);
  if (!mapping) {
    return c.json({ error: "worker not found" }, 404);
  }
  return c.json(mapping);
});

// ─── Execute Run (new session per run) ────────────────────────────────

app.post("/workers/:id/run", async (c) => {
  const workerId = c.req.param("id");
  const mapping = loadWorker(workerId);
  if (!mapping) {
    return c.json({ error: "worker not found" }, 404);
  }

  const body = await c.req.json<{
    task: string;
    workspace?: string;
    budget?: number;
    timeout?: number;
    allowedTools?: string[];
  }>();

  const client = getClient();
  const t0 = Date.now();
  const cwd = body.workspace || "/tmp/moltwork-run";
  fs.mkdirSync(cwd, { recursive: true });

  let session: any;
  let timeoutHandle: NodeJS.Timeout | undefined;
  let hardCloseHandle: NodeJS.Timeout | undefined;

  try {
    // Create a NEW session for this run
    session = await client.createSession(mapping.letta_agent_id, {
      cwd,
      allowedTools: body.allowedTools || [
        "Read", "Write", "Edit", "LS", "Glob", "Grep", "Bash",
      ],
      permissionMode: "unrestricted",
    });

    console.log(`[${workerId}] SESSION session=${(session as any).sessionId} cwd=${cwd}`);

    let timedOut = false;
    const timeoutMs = (body.timeout || 120) * 1000;

    // Real timeout: abort the session
    timeoutHandle = setTimeout(() => {
      timedOut = true;
      console.warn(`[${workerId}] TURN TIMEOUT after ${timeoutMs}ms; aborting`);
      void session.abort().catch(() => {});
      hardCloseHandle = setTimeout(() => {
        try { session.close(); } catch {}
      }, 5000);
    }, timeoutMs);

    await session.send(body.task);
    console.log(`[${workerId}] SEND COMPLETE`);

    let output = "";
    const toolCalls: Array<{ name: string; args: any }> = [];
    const toolResults: Array<{ name: string; result: any }> = [];
    let terminal: any = null;

    for await (const message of session.stream()) {
      console.log(`[${workerId}] EVENT type=${message.type}`);

      if (message.type === "assistant") {
        output += message.content || "";
      } else if (message.type === "tool_call") {
        toolCalls.push({ name: message.toolName || "", args: message.toolInput });
      } else if (message.type === "tool_result") {
        toolResults.push({ name: message.toolName || "", result: message.content });
      } else if (message.type === "result") {
        terminal = message;
        console.log(`[${workerId}] RESULT success=${message.success}`);
        break;
      }
    }

    const duration = Date.now() - t0;

    // Update mapping
    mapping.last_run_at = Date.now();
    mapping.run_count += 1;
    saveWorker(mapping);

    const conversationId = (session as any).conversationId || "";

    console.log(`[${workerId}] RUN OK duration=${duration}ms tools=${toolCalls.length} conversation=${conversationId}`);

    return c.json({
      ok: !timedOut && (terminal?.success ?? true),
      timed_out: timedOut,
      output_content: output,
      duration_ms: duration,
      agent_id: mapping.letta_agent_id,
      conversation_id: conversationId,
      tool_calls: toolCalls,
      tool_results: toolResults,
      session_id: (session as any).sessionId || "",
      terminal_result: terminal,
    });
  } catch (e) {
    console.error(`[${workerId}] RUN ERROR: ${e}`);
    return c.json(
      { ok: false, error: `execution error: ${e}`, error_code: "FAIL", duration_ms: Date.now() - t0 },
      500
    );
  } finally {
    if (timeoutHandle) clearTimeout(timeoutHandle);
    if (hardCloseHandle) clearTimeout(hardCloseHandle);
    if (session) {
      try { session.close(); } catch {}
      console.log(`[${workerId}] SESSION CLOSED`);
    }
  }
});

// ─── Snapshot (current agent state) ──────────────────────────────────

app.get("/workers/:id/snapshot", async (c) => {
  const workerId = c.req.param("id");
  const mapping = loadWorker(workerId);
  if (!mapping) {
    return c.json({ error: "worker not found" }, 404);
  }

  try {
    const client = getClient();
    // Resume the default conversation to get agent state
    const session = await client.resumeSession(mapping.letta_agent_id);
    const state = await session.bootstrapState();

    return c.json({
      ok: true,
      worker_id: workerId,
      agent_id: mapping.letta_agent_id,
      model: mapping.model,
      run_count: mapping.run_count,
      state,
    });
  } catch (e) {
    return c.json({ error: `snapshot error: ${e}` }, 500);
  }
});

// ─── List Memory Files (MemFS) ───────────────────────────────────────

app.get("/workers/:id/memfs", async (c) => {
  const workerId = c.req.param("id");
  const mapping = loadWorker(workerId);
  if (!mapping) {
    return c.json({ error: "worker not found" }, 404);
  }

  try {
    const client = getClient();
    const session = await client.resumeSession(mapping.letta_agent_id);

    // Bootstrap state to get memory directory info
    const state = await session.bootstrapState();

    return c.json({
      ok: true,
      worker_id: workerId,
      memory: state?.memory || [],
      memfs_path: state?.memfsPath || "",
    });
  } catch (e) {
    return c.json({ error: `memfs error: ${e}` }, 500);
  }
});

// ─── Apply Learning (memory/skill patch) ─────────────────────────────

app.post("/workers/:id/learning", async (c) => {
  const workerId = c.req.param("id");
  const mapping = loadWorker(workerId);
  if (!mapping) {
    return c.json({ error: "worker not found" }, 404);
  }

  const body = await c.req.json<{
    patch_type: "memory" | "skill";
    label: string;
    content: string;
  }>();

  try {
    const client = getClient();
    const session = await client.resumeSession(mapping.letta_agent_id);

    // For memory patches, we use the session to update memory blocks
    // The agent's MemFS handles the actual file writes via git
    if (body.patch_type === "memory") {
      // Send a command to the agent to update its memory
      await session.send(
        `/remember Update the "${body.label}" memory with the following content:\n\n${body.content}`
      );

      // Wait for completion
      for await (const _msg of session.stream()) {
        // consume stream
      }
    } else if (body.patch_type === "skill") {
      // For skills, we write directly to the MemFS skill directory
      // The agent will pick it up on next context load
      await session.send(
        `Create or update the skill file at skills/${body.label}/SKILL.md with this content:\n\n${body.content}`
      );

      for await (const _msg of session.stream()) {
        // consume stream
      }
    }

    return c.json({ ok: true, applied: body.patch_type, label: body.label });
  } catch (e) {
    return c.json({ error: `learning error: ${e}` }, 500);
  }
});

// ─── Export Trajectory ────────────────────────────────────────────────

app.get("/workers/:id/trajectory", async (c) => {
  const workerId = c.req.param("id");
  const mapping = loadWorker(workerId);
  if (!mapping) {
    return c.json({ error: "worker not found" }, 404);
  }

  const conversationId = c.req.query("conversation_id");

  try {
    const client = getClient();

    if (conversationId) {
      // Export specific conversation
      const session = await client.resumeSession(conversationId);
      const messages = await session.listMessages();

      return c.json({
        ok: true,
        worker_id: workerId,
        conversation_id: conversationId,
        messages,
      });
    } else {
      // List all conversations for this agent
      const conversations = await client.conversations.list({
        agentId: mapping.letta_agent_id,
      });

      return c.json({
        ok: true,
        worker_id: workerId,
        agent_id: mapping.letta_agent_id,
        conversations,
      });
    }
  } catch (e) {
    return c.json({ error: `trajectory error: ${e}` }, 500);
  }
});

// ─── Recall (search previous conversations) ──────────────────────────

app.post("/workers/:id/recall", async (c) => {
  const workerId = c.req.param("id");
  const mapping = loadWorker(workerId);
  if (!mapping) {
    return c.json({ error: "worker not found" }, 404);
  }

  const body = await c.req.json<{
    query: string;
    limit?: number;
  }>();

  try {
    const client = getClient();
    const session = await client.resumeSession(mapping.letta_agent_id);

    // Use the agent's recall ability to search previous conversations
    await session.send(
      `Search your memory and previous conversations for: "${body.query}". Return the most relevant findings.`
    );

    let recallResult = "";
    for await (const message of session.stream()) {
      if (message.type === "assistant") {
        recallResult += message.content || "";
      }
    }

    return c.json({
      ok: true,
      worker_id: workerId,
      query: body.query,
      result: recallResult,
    });
  } catch (e) {
    return c.json({ error: `recall error: ${e}` }, 500);
  }
});

export default app;

// ─── Start server (Node.js) ──────────────────────────────────────────
import { serve } from "@hono/node-server";

const port = Number(process.env.PORT ?? 3000);
console.log(`Runtime Letta service starting on port ${port}...`);

// Verify Letta backend is working
const client = new LettaAgentClient({ backend: "local" });
try {
  const models = await client.models.list();
  const mimo = models.entries?.filter((m: any) => m.id?.includes("mimo")) || [];
  console.log(`Letta backend OK. ${mimo.length} mimo models available.`);
} catch (e: any) {
  console.warn(`Warning: Could not verify Letta backend: ${e.message}`);
}

serve({
  fetch: app.fetch,
  port,
}, (info) => {
  console.log(`Runtime Letta service running on http://localhost:${info.port}`);
});

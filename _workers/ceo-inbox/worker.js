/**
 * SporlyWorks CEO Inbox — Cloudflare Worker
 *
 * Gives Lena Voss (lena.voss@sporlyworks.com) her own independent inbox.
 * - Receives inbound emails via Cloudflare Email Workers → stores in KV
 * - HTTP API for the board coordinator to read/manage/send emails
 * - Completely separate from the owner's personal Gmail
 *
 * KV Bindings: CEO_INBOX
 * Secrets: INBOX_SECRET (shared auth token with the board coordinator)
 */

export default {
  /**
   * Handle inbound emails to lena.voss@sporlyworks.com
   */
  async email(message, env, ctx) {
    try {
      // Read the raw email stream
      const rawEmail = await streamToText(message.raw);

      // Parse the email
      const parsed = parseEmail(rawEmail, message);

      // Generate unique ID
      const id = `msg:${Date.now()}:${Math.random().toString(36).substr(2, 8)}`;

      // Store in KV with 30-day TTL
      await env.CEO_INBOX.put(id, JSON.stringify({
        id,
        from: parsed.from,
        to: parsed.to,
        subject: parsed.subject,
        body: parsed.body,
        timestamp: new Date().toISOString(),
        read: false,
      }), { expirationTtl: 60 * 60 * 24 * 30 }); // 30 days

      console.log(`CEO Inbox: Stored email from ${parsed.from} — "${parsed.subject}"`);
    } catch (err) {
      console.error(`CEO Inbox: Failed to store email: ${err.message}`);
    }
  },

  /**
   * HTTP API for the board coordinator
   *
   * GET  /inbox         — List unread emails
   * GET  /inbox/all     — List all emails (read + unread)
   * POST /mark-read     — Mark emails as read { ids: [...] }
   * POST /send          — Send an email from Lena { to, subject, body }
   * GET  /health        — Health check
   */
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Health check (no auth needed)
    if (url.pathname === "/health") {
      return Response.json({ status: "ok", service: "ceo-inbox", ts: new Date().toISOString() });
    }

    // Auth check for all other endpoints
    const secret = request.headers.get("X-Inbox-Secret") || url.searchParams.get("secret");
    if (secret !== env.INBOX_SECRET) {
      return Response.json({ error: "Unauthorized" }, { status: 401 });
    }

    // --- GET /inbox — List unread emails ---
    if (url.pathname === "/inbox" && request.method === "GET") {
      return await handleListEmails(env, false);
    }

    // --- GET /inbox/all — List all emails ---
    if (url.pathname === "/inbox/all" && request.method === "GET") {
      return await handleListEmails(env, true);
    }

    // --- POST /mark-read — Mark emails as read ---
    if (url.pathname === "/mark-read" && request.method === "POST") {
      try {
        const { ids } = await request.json();
        if (!Array.isArray(ids)) {
          return Response.json({ error: "ids must be an array" }, { status: 400 });
        }
        let marked = 0;
        for (const id of ids) {
          const raw = await env.CEO_INBOX.get(id);
          if (raw) {
            const data = JSON.parse(raw);
            data.read = true;
            await env.CEO_INBOX.put(id, JSON.stringify(data), { expirationTtl: 60 * 60 * 24 * 30 });
            marked++;
          }
        }
        return Response.json({ success: true, marked });
      } catch (err) {
        return Response.json({ error: err.message }, { status: 500 });
      }
    }

    // --- POST /send — Queue an outbound email ---
    if (url.pathname === "/send" && request.method === "POST") {
      try {
        const { to, subject, body, replyTo } = await request.json();
        if (!to || !subject || !body) {
          return Response.json({ error: "to, subject, body required" }, { status: 400 });
        }
        // Store outbound email in KV for the coordinator to send via SMTP
        const id = `outbox:${Date.now()}:${Math.random().toString(36).substr(2, 8)}`;
        await env.CEO_INBOX.put(id, JSON.stringify({
          id, to, subject, body, replyTo,
          from: "lena.voss@sporlyworks.com",
          timestamp: new Date().toISOString(),
          sent: false,
        }), { expirationTtl: 60 * 60 * 24 * 7 }); // 7 days
        return Response.json({ success: true, id });
      } catch (err) {
        return Response.json({ error: err.message }, { status: 500 });
      }
    }

    return Response.json({ error: "Not Found", endpoints: ["/inbox", "/inbox/all", "/mark-read", "/send", "/health"] }, { status: 404 });
  }
};

// ── Helpers ──────────────────────────────────────────────────────────────

async function handleListEmails(env, includeRead) {
  try {
    const keys = await env.CEO_INBOX.list({ prefix: "msg:" });
    const emails = [];

    for (const key of keys.keys) {
      const raw = await env.CEO_INBOX.get(key.name);
      if (!raw) continue;
      try {
        const data = JSON.parse(raw);
        if (includeRead || !data.read) {
          emails.push(data);
        }
      } catch { /* skip corrupted entries */ }
    }

    // Sort newest first
    emails.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    return Response.json({
      count: emails.length,
      emails,
    });
  } catch (err) {
    return Response.json({ error: err.message }, { status: 500 });
  }
}

async function streamToText(stream) {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let result = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    result += decoder.decode(value, { stream: !done });
  }
  return result;
}

function parseEmail(raw, message) {
  // Extract plain text body from raw MIME email
  let body = "";
  const lines = raw.split("\n");
  let inBody = false;
  let isMultipart = false;
  let boundary = "";
  let inPlainText = false;
  let contentTransferEncoding = "";

  // Check for multipart boundary in headers
  for (const line of lines) {
    if (line.trim() === "") break; // End of headers
    const boundaryMatch = line.match(/boundary="?([^";\s]+)"?/i);
    if (boundaryMatch) {
      boundary = boundaryMatch[1];
      isMultipart = true;
    }
  }

  if (isMultipart && boundary) {
    // Parse multipart — extract text/plain part
    let currentPartIsPlain = false;
    let pastPartHeaders = false;

    for (const line of lines) {
      if (line.includes(boundary)) {
        currentPartIsPlain = false;
        pastPartHeaders = false;
        continue;
      }
      if (!pastPartHeaders) {
        if (line.toLowerCase().includes("content-type: text/plain")) {
          currentPartIsPlain = true;
        }
        if (line.toLowerCase().includes("content-transfer-encoding:")) {
          contentTransferEncoding = line.split(":")[1].trim().toLowerCase();
        }
        if (line.trim() === "") {
          pastPartHeaders = true;
        }
        continue;
      }
      if (currentPartIsPlain) {
        body += line + "\n";
      }
    }
  } else {
    // Simple single-part email
    for (const line of lines) {
      if (!inBody && line.trim() === "") {
        inBody = true;
        continue;
      }
      if (inBody) {
        body += line + "\n";
      }
    }
  }

  // Handle base64 encoding
  if (contentTransferEncoding === "base64") {
    try {
      body = atob(body.replace(/\s/g, ""));
    } catch { /* leave as-is if decode fails */ }
  }

  // Handle quoted-printable
  if (contentTransferEncoding === "quoted-printable") {
    body = body.replace(/=\r?\n/g, "").replace(/=([0-9A-Fa-f]{2})/g, (_, hex) =>
      String.fromCharCode(parseInt(hex, 16))
    );
  }

  // Trim and limit body size
  body = body.trim().substring(0, 3000);

  return {
    from: message.from,
    to: message.to,
    subject: message.headers.get("subject") || "(no subject)",
    body,
  };
}

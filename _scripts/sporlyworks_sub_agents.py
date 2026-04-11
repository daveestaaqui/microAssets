#!/usr/bin/env python3
"""
SporlyWorks Department Agents v8.0
===================================
8 specialized department agents that execute CEO directives.
Each agent performs real work: API calls, file mutations, health checks.

Agents:
  1. MarketingAgent     — SEO landing pages, blog content generation
  2. DevOpsAgent        — CWS packaging, build pipeline, API queue
  3. ComplianceAgent    — Privacy declarations, policy audit generation
  4. InfrastructureAgent — Cloudflare/Railway health checks + mutations
  5. QAAgent            — Targeted quality audits
  6. FinanceAgent       — Stripe revenue monitoring, refund detection
  7. SecurityAgent      — Credential rotation tracking, dependency audit
  8. CustomerSuccessAgent — KV support ticket monitoring
"""

import os
import json
import logging
import urllib.request
import urllib.error
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

logging.basicConfig(
    format='%(asctime)s | Dept Agent | [%(levelname)s] %(message)s',
    level=logging.INFO
)


# ── Helper: Safe OpenAI call ────────────────────────────────────────────

def _call_llm(prompt, api_key, max_tokens=2000):
    """Make a single OpenAI call. Returns raw string content."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": prompt}],
        "temperature": 0.6,
        "max_tokens": max_tokens
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
        content = result["choices"][0]["message"]["content"].strip()
        # Strip markdown code fences
        if content.startswith("```html"):
            content = content[7:]
        elif content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()


def _check_url_status(url, timeout=10):
    """Quick HTTP health check. Returns (status_code, None) or (0, error_msg)."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "SporlyWorks-Agent/1.0")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, None
    except urllib.error.HTTPError as e:
        return e.code, str(e)
    except Exception as e:
        return 0, str(e)


# ── 1. Marketing Agent ──────────────────────────────────────────────────

def handle_marketing_agent(payload, api_key):
    """Generate SEO landing pages, blog posts, or outreach content."""
    task = payload.get("task", "generate_landing_page")
    app_id = payload.get("app_id", "unknown-app")
    angle = payload.get("angle", "general-saas")

    logging.info(f"Marketing: {task} for '{app_id}' (angle: {angle})")

    if task == "generate_landing_page":
        prompt = f"""You are the Chief Marketing Officer for SporlyWorks.
Generate a high-conversion, responsive HTML landing page for '{app_id}'.
Marketing Angle: {angle}.

LEGAL: Strictly comply with CAN-SPAM, GDPR/CCPA. No trademark infringement.
Use ethical persuasion only. All claims must be truthful.

DESIGN: Ultra-premium Tech-meets-Nature aesthetic. Use Google Fonts (Inter).
Include: hero section, features grid, testimonials placeholder, CTA button,
SEO meta tags, structured data (JSON-LD), responsive design.

Return ONLY the raw HTML code."""

        html = _call_llm(prompt, api_key, max_tokens=4000)
        output_dir = os.path.join(REPO_ROOT, "marketing", app_id)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "landing_page.html")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        # Validate the output has basic HTML structure
        if "<html" not in html.lower() or "<body" not in html.lower():
            logging.warning(f"Generated HTML may be malformed for {app_id}")
            return False

        logging.info(f"✅ Wrote landing page: {output_path} ({len(html)} chars)")
        return True

    elif task == "generate_blog_post":
        prompt = f"""Write a 600-word SEO blog post for the '{app_id}' browser extension.
Angle: {angle}. Include a compelling title, meta description, and 3 sections.
Target keywords naturally. Format as clean HTML with semantic tags.
LEGAL: All claims must be truthful. No competitor disparagement."""

        html = _call_llm(prompt, api_key, max_tokens=3000)
        output_dir = os.path.join(REPO_ROOT, "marketing", app_id)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "blog_post.html")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        logging.info(f"✅ Wrote blog post: {output_path}")
        return True

    logging.warning(f"Unknown marketing task: {task}")
    return False


# ── 2. DevOps Agent ─────────────────────────────────────────────────────

def handle_devops_agent(payload, api_key):
    """Build pipeline tasks: manifest audits, package validation, version bumps."""
    task = payload.get("task", "audit_manifests")
    logging.info(f"DevOps: {task}")

    if task == "audit_manifests":
        # Scan all extensions for MV2 → MV3 migration needs
        results = {"mv2": [], "mv3": [], "missing_icons": []}
        for item in sorted(os.listdir(REPO_ROOT)):
            manifest_path = os.path.join(REPO_ROOT, item, "manifest.json")
            if not os.path.isfile(manifest_path):
                continue
            if item.startswith(("_", ".")) or "-firefox" in item:
                continue
            try:
                with open(manifest_path) as f:
                    data = json.load(f)
                mv = data.get("manifest_version", 0)
                if mv == 2:
                    results["mv2"].append(item)
                elif mv == 3:
                    results["mv3"].append(item)
                # Check for icon
                icons = data.get("icons", {})
                if not icons or "128" not in str(icons):
                    results["missing_icons"].append(item)
            except Exception:
                pass

        report_path = os.path.join(REPO_ROOT, "marketing", "devops_manifest_audit.json")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2)

        logging.info(f"✅ Manifest audit: MV2={len(results['mv2'])}, MV3={len(results['mv3'])}, Missing icons={len(results['missing_icons'])}")
        return True

    elif task == "version_bump":
        target = payload.get("target")
        if not target:
            logging.error("version_bump requires 'target' in payload")
            return False
        manifest_path = os.path.join(REPO_ROOT, target, "manifest.json")
        if not os.path.isfile(manifest_path):
            logging.error(f"No manifest found at {manifest_path}")
            return False
        with open(manifest_path) as f:
            data = json.load(f)
        version = data.get("version", "1.0.0")
        parts = version.split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        data["version"] = ".".join(parts)
        with open(manifest_path, "w") as f:
            json.dump(data, f, indent=2)
        logging.info(f"✅ Bumped {target}: {version} → {data['version']}")
        return True

    logging.info(f"DevOps task '{task}' acknowledged. No automated action available.")
    return True


# ── 3. Compliance Agent ─────────────────────────────────────────────────

def handle_compliance_agent(payload, api_key):
    """Generate privacy declarations and audit compliance."""
    task = payload.get("task", "audit_privacy")
    logging.info(f"Compliance: {task}")

    if task == "audit_privacy":
        # Check each extension's manifest for required CWS privacy fields
        findings = []
        for item in sorted(os.listdir(REPO_ROOT)):
            manifest_path = os.path.join(REPO_ROOT, item, "manifest.json")
            if not os.path.isfile(manifest_path) or item.startswith(("_", ".")):
                continue
            if "-firefox" in item:
                continue
            try:
                with open(manifest_path) as f:
                    data = json.load(f)
                # Check for overly broad permissions
                perms = data.get("permissions", []) + data.get("host_permissions", [])
                if "<all_urls>" in perms or "*://*/*" in perms:
                    findings.append(f"BROAD_PERMS: {item} requests <all_urls>")
                if "tabs" in perms and "activeTab" in perms:
                    findings.append(f"REDUNDANT_PERMS: {item} has both 'tabs' and 'activeTab'")
            except Exception:
                pass

        report_path = os.path.join(REPO_ROOT, "marketing", "compliance_audit.json")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w") as f:
            json.dump({"timestamp": datetime.utcnow().isoformat() + "Z", "findings": findings}, f, indent=2)

        logging.info(f"✅ Compliance audit: {len(findings)} findings")
        return True

    logging.info(f"Compliance task '{task}' acknowledged.")
    return True


# ── 4. Infrastructure Agent ─────────────────────────────────────────────

def handle_infrastructure_agent(payload, api_key):
    """Monitor and manage Cloudflare and Railway infrastructure."""
    task = payload.get("task", "health_check")
    provider = payload.get("provider", "all").lower()
    logging.info(f"Infrastructure: {task} on {provider}")

    results = {}

    if task == "health_check" or task == "monitor":
        # Check Cloudflare worker health
        cf_status, cf_err = _check_url_status(
            "https://sporlyworks-support.sporlyworks.workers.dev/health"
        )
        results["cloudflare_worker"] = {
            "status": "HEALTHY" if cf_status == 200 else "DOWN",
            "http_code": cf_status,
            "error": cf_err
        }

        # Check landing page
        lp_status, lp_err = _check_url_status("https://sporlyworks.com")
        results["landing_page"] = {
            "status": "HEALTHY" if lp_status == 200 else "DOWN",
            "http_code": lp_status,
            "error": lp_err
        }

        # Check GitHub Release
        gh_status, gh_err = _check_url_status(
            "https://github.com/daveestaaqui/micro-assets-landing-page/releases/tag/v1.0.0"
        )
        results["github_release"] = {
            "status": "HEALTHY" if gh_status == 200 else "DOWN",
            "http_code": gh_status,
            "error": gh_err
        }

        report_path = os.path.join(REPO_ROOT, "marketing", "infra_health.json")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w") as f:
            json.dump({
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "checks": results
            }, f, indent=2)

        all_healthy = all(r["status"] == "HEALTHY" for r in results.values())
        logging.info(f"✅ Infrastructure health: {'ALL HEALTHY' if all_healthy else 'ISSUES DETECTED'}")
        for name, check in results.items():
            if check["status"] != "HEALTHY":
                logging.error(f"  ❌ {name}: HTTP {check['http_code']} — {check['error']}")
        return all_healthy

    if task == "cloudflare_kv_read":
        cf_token = os.environ.get("CLOUDFLARE_API_TOKEN")
        cf_acc = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        if not cf_token or not cf_acc:
            logging.error("Missing Cloudflare credentials.")
            return False
        logging.info("Cloudflare KV read capability confirmed (credentials present).")
        return True

    logging.info(f"Infrastructure task '{task}' acknowledged.")
    return True


# ── 5. QA Agent ─────────────────────────────────────────────────────────

def handle_qa_agent(payload, api_key):
    """Run targeted QA audits as directed by the CEO."""
    import sporlyworks_qa_agent
    target = payload.get("target", "full")
    logging.info(f"QA: Running {target} audit")

    if target == "portfolio":
        result = sporlyworks_qa_agent.audit_portfolio_integrity()
    elif target == "landing_page":
        result = sporlyworks_qa_agent.audit_landing_page()
    elif target == "releases":
        result = sporlyworks_qa_agent.audit_github_release()
    else:
        result = sporlyworks_qa_agent.run_full_audit()

    logging.info(f"✅ QA {target}: {json.dumps(result, indent=2)}")
    return True


# ── 6. Finance Agent ────────────────────────────────────────────────────

def handle_finance_agent(payload, api_key):
    """Monitor Stripe revenue, refunds, and billing health."""
    task = payload.get("task", "revenue_snapshot")
    logging.info(f"Finance: {task}")

    stripe_key = os.environ.get("STRIPE_SECRET_KEY")
    if not stripe_key:
        logging.warning("STRIPE_SECRET_KEY not set. Finance agent running in read-only mode.")
        # Still produce a placeholder report so the CEO knows the status
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "NO_CREDENTIALS",
            "note": "Stripe API key not configured. Finance monitoring unavailable.",
            "recommendation": "Set STRIPE_SECRET_KEY in GitHub Actions secrets."
        }
        report_path = os.path.join(REPO_ROOT, "marketing", "finance_report.json")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        return True

    # If we have Stripe key, fetch recent charges
    try:
        url = "https://api.stripe.com/v1/charges?limit=10"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {stripe_key}")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            charges = data.get("data", [])
            total = sum(c.get("amount", 0) for c in charges if c.get("paid"))
            refunds = sum(1 for c in charges if c.get("refunded"))

            report = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "recent_charges": len(charges),
                "total_revenue_cents": total,
                "refunds": refunds,
                "status": "HEALTHY" if refunds < 3 else "WARNING_HIGH_REFUNDS"
            }

            report_path = os.path.join(REPO_ROOT, "marketing", "finance_report.json")
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

            logging.info(f"✅ Finance: {len(charges)} charges, ${total / 100:.2f} revenue, {refunds} refunds")
            return True
    except Exception as e:
        logging.error(f"Finance agent error: {e}")
        return False


# ── 7. Security Agent ───────────────────────────────────────────────────

def handle_security_agent(payload, api_key):
    """Track credential rotation, scan for exposed secrets, audit deps."""
    task = payload.get("task", "credential_audit")
    logging.info(f"Security: {task}")

    findings = []

    if task == "credential_audit":
        # Check that critical secrets are set
        required_secrets = [
            "OPENAI_API_KEY", "GITHUB_TOKEN", "SENDER_EMAIL",
            "SENDER_APP_PASSWORD", "CLOUDFLARE_API_TOKEN",
            "CLOUDFLARE_ACCOUNT_ID", "RAILWAY_API_TOKEN"
        ]
        for secret in required_secrets:
            if not os.environ.get(secret):
                findings.append(f"MISSING_SECRET: {secret} is not set")

        # Scan repo for accidentally committed secrets
        dangerous_patterns = [
            "AKIA",  # AWS key prefix
            "sk_live_",  # Stripe live key
            "sk_test_",  # Stripe test key
            "ghp_",  # GitHub PAT
            "gho_",  # GitHub OAuth
        ]
        for item in os.listdir(REPO_ROOT):
            item_path = os.path.join(REPO_ROOT, item)
            if not os.path.isdir(item_path) or item.startswith(("_", ".")):
                continue
            for root, dirs, files in os.walk(item_path):
                dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "__pycache__")]
                for fname in files:
                    if not fname.endswith((".js", ".py", ".json", ".html", ".ts")):
                        continue
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, "r", errors="ignore") as f:
                            content = f.read()
                        for pattern in dangerous_patterns:
                            if pattern in content:
                                rel = os.path.relpath(fpath, REPO_ROOT)
                                findings.append(f"EXPOSED_SECRET: {rel} contains '{pattern}...'")
                                break
                    except Exception:
                        pass

        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "findings": findings,
            "status": "PASS" if not findings else "FAIL"
        }

        report_path = os.path.join(REPO_ROOT, "marketing", "security_audit.json")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logging.info(f"✅ Security audit: {len(findings)} findings")
        return len(findings) == 0

    logging.info(f"Security task '{task}' acknowledged.")
    return True


# ── 8. Customer Success Agent ───────────────────────────────────────────

def handle_customer_success_agent(payload, api_key):
    """Monitor support tickets from Cloudflare KV, track response times."""
    task = payload.get("task", "ticket_summary")
    logging.info(f"Customer Success: {task}")

    cf_token = os.environ.get("CLOUDFLARE_API_TOKEN")
    cf_acc = os.environ.get("CLOUDFLARE_ACCOUNT_ID")

    if not cf_token or not cf_acc:
        logging.warning("Cloudflare credentials missing. Customer Success running offline.")
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "OFFLINE",
            "note": "Cannot access KV without Cloudflare credentials."
        }
        report_path = os.path.join(REPO_ROOT, "marketing", "customer_success.json")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        return True

    # Query Cloudflare KV for recent tickets
    kv_namespace = "137c647bbe23458ca3fc4d15b0a1c90c"
    try:
        url = f"https://api.cloudflare.com/client/v4/accounts/{cf_acc}/storage/kv/namespaces/{kv_namespace}/keys?limit=20"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {cf_token}")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            keys = data.get("result", [])
            ticket_keys = [k for k in keys if k.get("name", "").startswith("ticket:")]
            rejection_keys = [k for k in keys if k.get("name", "").startswith("rejection:")]

            report = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "total_kv_keys": len(keys),
                "open_tickets": len(ticket_keys),
                "pending_rejections": len(rejection_keys),
                "status": "HEALTHY" if len(rejection_keys) == 0 else "ATTENTION_NEEDED"
            }

            report_path = os.path.join(REPO_ROOT, "marketing", "customer_success.json")
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

            logging.info(f"✅ Customer Success: {len(ticket_keys)} tickets, {len(rejection_keys)} rejections")
            return True
    except Exception as e:
        logging.error(f"Customer Success agent error: {e}")
        return False


# ── Master Router ────────────────────────────────────────────────────────

def route_payload(dispatch, api_key):
    """Route CEO dispatches to the appropriate department agent."""
    target = dispatch.get("target_agent")
    payload = dispatch.get("payload", {})

    handlers = {
        "MarketingAgent": handle_marketing_agent,
        "DevOpsAgent": handle_devops_agent,
        "ComplianceAgent": handle_compliance_agent,
        "InfrastructureAgent": handle_infrastructure_agent,
        "QAAgent": handle_qa_agent,
        "FinanceAgent": handle_finance_agent,
        "SecurityAgent": handle_security_agent,
        "CustomerSuccessAgent": handle_customer_success_agent,
    }

    handler = handlers.get(target)
    if handler:
        return handler(payload, api_key)

    logging.warning(f"Unknown Agent: {target}")
    return False

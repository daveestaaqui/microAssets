"""
Autonomous Updater
==================
Reads bugs captured by the AI Support Agent,
pulls the relevant source code, and uses Gemini 2.5 Pro 
to automatically patch the codebase and commit the fix.
"""
import os
import json
import logging
import asyncio
import datetime
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Rely on local workspace if GITHUB_TOKEN is not strictly used for source code
WORKSPACE_DIR = os.environ.get("MICROASSETS_DIR", os.path.expanduser("~/Desktop/microAssets"))

async def fix_extension_code(client: genai.Client, ext_slug: str, bug_details: str, current_files: dict):
    """Feed the existing codebase and the bug to the AI to rewrite and fix."""
    prompt = f"""
    You are an autonomous engineering agent patching a production Google Chrome extension.
    
    Extension Slug: {ext_slug}
    User Bug Report: "{bug_details}"
    
    Below is a JSON dump of the CURRENT source files:
    {json.dumps(current_files, indent=2)}
    
    INSTRUCTIONS:
    1. Identify the root cause of the bug described by the user.
    2. Rewrite ONLY the files that need fixing. Keep the same structure.
    3. Return a SINGLE JSON object where keys are the file paths, and values are the new, raw file content string.
    No backticks, pure JSON dictionary.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text.strip())
    except Exception as e:
        logger.error(f"[UPDATER] Failed to generate code fix: {e}")
        return None

ALLOWED_EXTENSIONS = {'.js', '.html', '.css', '.json'}

def write_fixed_code_locally(ext_dir: str, new_files: dict):
    """Write the patched files back to the filesystem with strict security checks."""
    for relative_path, new_content in new_files.items():
        # SECURITY: Strip traversal attempts
        clean_path = relative_path.lstrip("./")
        
        # SECURITY: Block path traversal patterns
        if '..' in clean_path or clean_path.startswith('/'):
            logger.warning(f"[UPDATER] 🛡️ BLOCKED path traversal attempt: '{relative_path}'")
            continue
        
        # SECURITY: Block dotfiles (e.g., .bashrc, .env)
        if any(part.startswith('.') for part in clean_path.split(os.sep)):
            logger.warning(f"[UPDATER] 🛡️ BLOCKED dotfile write attempt: '{relative_path}'")
            continue
            
        # SECURITY: Extension whitelist
        _, ext = os.path.splitext(clean_path)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            logger.warning(f"[UPDATER] 🛡️ BLOCKED non-whitelisted extension: '{relative_path}' ({ext})")
            continue
        
        full_path = os.path.join(ext_dir, clean_path)
        
        # SECURITY: Verify resolved path is strictly within the extension directory
        real_full = os.path.realpath(full_path)
        real_ext_dir = os.path.realpath(ext_dir)
        if not real_full.startswith(real_ext_dir + os.sep):
            logger.warning(f"[UPDATER] 🛡️ BLOCKED symlink/realpath escape: '{relative_path}' resolved to '{real_full}'")
            continue
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(new_content)
                
    logger.info(f"[UPDATER] Successfully patched files in {ext_dir}")

async def run():
    logger.info("[UPDATER] Waking up to review pending bug tickets...")
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    ledger_path = os.path.join(data_dir, "pending_bugs.json")
    
    if not os.path.exists(ledger_path):
        logger.info("[UPDATER] No bug ledger found. Sleeping.")
        return
        
    with open(ledger_path, "r") as f:
        try:
            ledger = json.load(f)
        except Exception:
            logger.warning("[UPDATER] Corrupt bug ledger. Aborting.")
            return

    pending_bugs = [b for b in ledger if b.get("status") == "PENDING_AUTONOMOUS_FIX"]
    if not pending_bugs:
        logger.info("[UPDATER] 0 pending bugs detected. All systems green.")
        return
        
    logger.info(f"[UPDATER] Processing {len(pending_bugs)} pending bug(s)...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("[UPDATER] Missing GEMINI_API_KEY. Aborting fix loop.")
        return
        
    client = genai.Client(api_key=api_key)
    
    for bug in pending_bugs:
        slug = bug["slug"]
        ext_dir = os.path.join(WORKSPACE_DIR, slug)
        
        if not os.path.isdir(ext_dir):
            logger.error(f"[UPDATER] Could not locate source code for '{slug}' at {ext_dir}. Marking bug as FAILED.")
            bug["status"] = "FAILED_NO_SOURCE_FOUND"
            continue
            
        # Compile existing source files to memory
        current_files = {}
        for root, dirs, files in os.walk(ext_dir):
            # Exclude massive or unnecessary directories
            if "icons" in root.split(os.sep) or "store" in root.split(os.sep): 
                continue
            for file in files:
                if file.endswith((".js", ".html", ".css", ".json")):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, ext_dir)
                    try:
                        with open(file_path, "r") as f:
                            current_files[rel_path] = f.read()
                    except Exception as e:
                        pass
        
        logger.info(f"[UPDATER] Analyzing {len(current_files)} files for '{slug}'...")
        
        # Rewrite the broken code
        new_files = await fix_extension_code(client, slug, bug["issue"], current_files)
        
        if new_files:
            # Structurally validate the fix using our standard QA gate
            try:
                from jobs.autonomous_factory import validate_extension_code
                safe_files = {**current_files, **new_files} # simulated state
                validate_extension_code(safe_files)
                
                # Validation passed -> Write to disk!
                write_fixed_code_locally(ext_dir, new_files)
                
                logger.info(f"✅ Self-Healing Complete: Patched '{slug}' successfully.")
                bug["status"] = "FIXED_WAITING_FOR_REVIEW"
                bug["resolved_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                
                # Note this software update for system-wide changelog syncing
                try:
                    from services.audit_log import log_event
                    log_event("SOFTWARE_FIXED", {
                        "slug": slug,
                        "issue_resolved": bug["issue"]
                    }, source="autonomous_updater")
                except Exception as log_err:
                    logger.warning(f"Failed to log SOFTWARE_FIXED event: {log_err}")
            except Exception as qc_err:
                logger.error(f"❌ Patch for '{slug}' failed Quality Control Gate: {qc_err}")
                bug["status"] = "FAILED_QC_GATE"
        else:
            bug["status"] = "FAILED_LLM_REWRITE"
            
    # Save back the updated ledger
    with open(ledger_path, "w") as f:
        json.dump(ledger, f, indent=2)
    
    logger.info("[UPDATER] Autonomously patched pending bugs. Sleeping.")

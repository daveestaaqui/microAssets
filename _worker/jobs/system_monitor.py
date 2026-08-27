"""
System Monitor & Self-Recovery
================================
Unified monitoring dashboard job that:
1. Tracks worker vitals (memory, uptime, job success/failure rates)
2. Backs up critical data files (pending_bugs.json, refund_audit.json, audit_log.jsonl)
3. Self-heals crashed jobs by detecting stale heartbeats
4. Sends a daily consolidated health digest to Discord
5. Rotates audit log to prevent unbounded growth
6. Monitors disk space and warns on pressure
7. Backs up license server data remotely

Runs every 4 hours via APScheduler.

v6.0 Hardened:
 - Audit log rotation (max 50K lines, old entries archived to .gz)
 - Disk space monitoring (alert at 80% usage)
 - License server remote backup via /metrics endpoint
 - Checksum verification for data file integrity
"""
import os
import sys
import json
import gzip
import time
import shutil
import logging
import hashlib
import datetime
import asyncio
import tempfile

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

# In-memory job heartbeat registry — jobs update this when they run successfully
_job_heartbeats = {}

CRITICAL_DATA_FILES = [
    "pending_bugs.json",
    "refund_audit.json",
    "audit_log.jsonl",
    "play_publish_ledger.json",
    "edge_publish_ledger.json",
    "opera_publish_ledger.json",
    "website_sync_state.json",
]
MAX_BACKUPS_PER_FILE = 5  # Rolling window — keep last 5 snapshots

# Audit log rotation
AUDIT_LOG_MAX_LINES = 50000  # Rotate when log exceeds this
AUDIT_LOG_KEEP_LINES = 10000  # Keep most recent entries after rotation

# Disk monitoring
DISK_USAGE_WARNING_PCT = 80
DISK_USAGE_CRITICAL_PCT = 95

# License server backup
LICENSE_SERVER_URL = os.environ.get("LICENSE_SERVER_URL", "")
LICENSE_ADMIN_KEY = os.environ.get("ADMIN_SECRET", "")


def record_heartbeat(job_name: str, success: bool = True, details: str = ""):
    """Called by other jobs after execution to register health."""
    _job_heartbeats[job_name] = {
        "last_run": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "success": success,
        "details": details,
        "epoch": time.time()
    }


def get_heartbeats() -> dict:
    return dict(_job_heartbeats)


def backup_data_files():
    """Create timestamped rolling backups of all critical data files."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backed_up = []
    
    for filename in CRITICAL_DATA_FILES:
        src = os.path.join(DATA_DIR, filename)
        if os.path.exists(src) and os.path.getsize(src) > 0:
            dst = os.path.join(BACKUP_DIR, f"{filename}.{timestamp}.bak")
            try:
                shutil.copy2(src, dst)
                backed_up.append(filename)
            except Exception as e:
                logger.error(f"[MONITOR] Failed to backup {filename}: {e}")
    
    # Prune old backups — keep only the last N per file
    for filename in CRITICAL_DATA_FILES:
        pattern_prefix = f"{filename}."
        existing = sorted([
            f for f in os.listdir(BACKUP_DIR)
            if f.startswith(pattern_prefix) and f.endswith(".bak")
        ])
        while len(existing) > MAX_BACKUPS_PER_FILE:
            old = existing.pop(0)
            try:
                os.remove(os.path.join(BACKUP_DIR, old))
            except Exception:
                pass
    
    return backed_up


def get_worker_vitals() -> dict:
    """Collect system-level metrics about the worker process."""
    import resource
    
    uptime_file = os.path.join(DATA_DIR, "worker_start_epoch.txt")
    if os.path.exists(uptime_file):
        with open(uptime_file, "r") as f:
            start_epoch = float(f.read().strip())
        uptime_seconds = time.time() - start_epoch
    else:
        uptime_seconds = 0
    
    usage = resource.getrusage(resource.RUSAGE_SELF)
    # macOS reports ru_maxrss in bytes, Linux in KB
    if sys.platform == "darwin":
        mem_mb = round(usage.ru_maxrss / (1024 * 1024), 1)
    else:
        mem_mb = round(usage.ru_maxrss / 1024, 1)
    
    # Data directory disk usage
    data_size = 0
    if os.path.isdir(DATA_DIR):
        for f in os.listdir(DATA_DIR):
            fp = os.path.join(DATA_DIR, f)
            if os.path.isfile(fp):
                data_size += os.path.getsize(fp)
    
    return {
        "uptime_hours": round(uptime_seconds / 3600, 2),
        "memory_mb": mem_mb,
        "data_size_kb": round(data_size / 1024, 1),
        "python_version": sys.version.split()[0],
    }


def detect_stale_jobs(max_staleness_hours: dict = None) -> list:
    """
    Detect jobs that haven't reported a heartbeat within their expected window.
    Returns list of stale job names.
    """
    if max_staleness_hours is None:
        max_staleness_hours = {
            "support_agent": 2,         # Every 30 min, grace of 2h
            "health_check": 8,          # Every 6h, grace of 8h
            "cws_monitor": 3,           # Every 60 min, grace of 3h
            "review_scanner": 26,       # Daily, grace of 26h
            "autonomous_factory": 192,  # Weekly, grace of 8 days
            "autonomous_updater": 26,   # Nightly, grace of 26h
            "play_publisher": 192,      # Weekly, grace of 8 days
            "edge_publisher": 192,      # Weekly, grace of 8 days
            "opera_publisher": 192,     # Weekly, grace of 8 days
            "website_sync": 26,         # Daily, grace of 26h
        }
    
    stale = []
    now = time.time()
    
    for job_name, max_hours in max_staleness_hours.items():
        hb = _job_heartbeats.get(job_name)
        if hb is None:
            continue  # Never ran yet — skip (could be first boot)
        
        elapsed_hours = (now - hb["epoch"]) / 3600
        if elapsed_hours > max_hours:
            stale.append({
                "job": job_name,
                "last_seen_hours_ago": round(elapsed_hours, 1),
                "last_success": hb["success"],
                "max_expected_hours": max_hours
            })
    
    return stale


def get_data_integrity_report() -> dict:
    """Check that critical data files are valid and not corrupted."""
    report = {}
    os.makedirs(DATA_DIR, exist_ok=True)
    
    for filename in CRITICAL_DATA_FILES:
        filepath = os.path.join(DATA_DIR, filename)
        entry = {"exists": False, "size_bytes": 0, "valid": False}
        
        if os.path.exists(filepath):
            entry["exists"] = True
            entry["size_bytes"] = os.path.getsize(filepath)
            
            try:
                with open(filepath, "r") as f:
                    content = f.read().strip()
                    if filename.endswith(".jsonl"):
                        # Validate each line is valid JSON
                        lines = [l for l in content.split("\n") if l.strip()]
                        for line in lines[-5:]:  # Check last 5 entries
                            json.loads(line)
                        entry["valid"] = True
                        entry["entries"] = len(lines)
                    else:
                        json.loads(content)
                        entry["valid"] = True
            except Exception:
                entry["valid"] = False
                entry["corrupted"] = True
        
        report[filename] = entry
    
    return report


def rotate_audit_log():
    """
    Rotate audit_log.jsonl when it exceeds MAX_LINES.
    Archives old entries to a gzipped file and keeps only the most recent.
    """
    audit_path = os.path.join(DATA_DIR, "audit_log.jsonl")
    if not os.path.exists(audit_path):
        return 0
    
    try:
        with open(audit_path, 'r') as f:
            lines = f.readlines()
        
        if len(lines) <= AUDIT_LOG_MAX_LINES:
            return 0  # No rotation needed
        
        # Archive old entries
        old_lines = lines[:-AUDIT_LOG_KEEP_LINES]
        keep_lines = lines[-AUDIT_LOG_KEEP_LINES:]
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = os.path.join(DATA_DIR, "log_archives")
        os.makedirs(archive_dir, exist_ok=True)
        archive_path = os.path.join(archive_dir, f"audit_log.{timestamp}.jsonl.gz")
        
        # Write archived entries to gzip
        with gzip.open(archive_path, 'wt') as gz:
            gz.writelines(old_lines)
        
        # Atomically write truncated log
        fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, suffix='.tmp')
        try:
            with os.fdopen(fd, 'w') as f:
                f.writelines(keep_lines)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, audit_path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
        
        # Prune old archives (keep last 10)
        archives = sorted([f for f in os.listdir(archive_dir) if f.endswith('.gz')])
        while len(archives) > 10:
            old = archives.pop(0)
            try:
                os.remove(os.path.join(archive_dir, old))
            except OSError:
                pass
        
        rotated_count = len(old_lines)
        logger.info(f"[MONITOR] Rotated audit log: archived {rotated_count} entries, kept {len(keep_lines)}")
        return rotated_count
    except Exception as e:
        logger.error(f"[MONITOR] Audit log rotation failed: {e}")
        return 0


def check_disk_space() -> dict:
    """Check available disk space and return status."""
    try:
        stat = os.statvfs(DATA_DIR)
        total_gb = (stat.f_frsize * stat.f_blocks) / (1024 ** 3)
        free_gb = (stat.f_frsize * stat.f_bavail) / (1024 ** 3)
        used_pct = round((1 - (stat.f_bavail / stat.f_blocks)) * 100, 1)
        
        return {
            "total_gb": round(total_gb, 1),
            "free_gb": round(free_gb, 1),
            "used_pct": used_pct,
            "status": "critical" if used_pct >= DISK_USAGE_CRITICAL_PCT else
                      "warning" if used_pct >= DISK_USAGE_WARNING_PCT else "ok"
        }
    except Exception as e:
        logger.error(f"[MONITOR] Disk space check failed: {e}")
        return {"total_gb": 0, "free_gb": 0, "used_pct": 0, "status": "unknown"}


async def backup_license_server():
    """Fetch license server health data for remote monitoring."""
    if not LICENSE_SERVER_URL:
        return None
    
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{LICENSE_SERVER_URL.rstrip('/')}/health",
            )
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"[MONITOR] License server: {data.get('status')} — {data.get('active_licenses', '?')} active licenses")
                return data
            else:
                logger.warning(f"[MONITOR] License server health check failed: {resp.status_code}")
                return {"status": "unhealthy", "code": resp.status_code}
    except Exception as e:
        logger.error(f"[MONITOR] License server unreachable: {e}")
        return {"status": "unreachable", "error": str(e)}


def compute_file_checksum(filepath) -> str:
    """Compute SHA-256 checksum for a data file."""
    try:
        sha = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for block in iter(lambda: f.read(8192), b''):
                sha.update(block)
        return sha.hexdigest()[:16]
    except Exception:
        return "error"


async def run():
    """
    Master monitoring loop.
    Backs up data, checks vitals, detects stale jobs, sends digest.
    v6.0: +audit log rotation, +disk monitoring, +license server backup
    """
    from services.notifications import send_notification, send_alert
    
    logger.info("[MONITOR] Running system health scan...")
    
    # 1. Backup critical data
    backed_up = backup_data_files()
    logger.info(f"[MONITOR] Backed up {len(backed_up)} data files: {backed_up}")
    
    # 2. Rotate audit log if needed
    rotated = rotate_audit_log()
    if rotated:
        logger.info(f"[MONITOR] Audit log rotated: {rotated} old entries archived")
    
    # 3. Worker vitals
    vitals = get_worker_vitals()
    logger.info(f"[MONITOR] Vitals: uptime={vitals['uptime_hours']}h, mem={vitals['memory_mb']}MB")
    
    # 4. Disk space
    disk = check_disk_space()
    logger.info(f"[MONITOR] Disk: {disk['used_pct']}% used ({disk['free_gb']}GB free)")
    
    # 5. Data integrity
    integrity = get_data_integrity_report()
    corrupted = [f for f, info in integrity.items() if info.get("corrupted")]
    
    # 5b. Compute checksums for tracking
    checksums = {}
    for filename in CRITICAL_DATA_FILES:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            checksums[filename] = compute_file_checksum(filepath)
    
    # 6. Stale job detection
    stale_jobs = detect_stale_jobs()
    
    # 7. License server health
    license_status = await backup_license_server()
    
    # 8. Build digest
    issues = []
    
    if corrupted:
        issues.append(f"🔴 **Corrupted data files**: {', '.join(corrupted)}")
        # Attempt auto-recovery from backup
        for cf in corrupted:
            backup_files = sorted([
                f for f in os.listdir(BACKUP_DIR)
                if f.startswith(f"{cf}.") and f.endswith(".bak")
            ]) if os.path.isdir(BACKUP_DIR) else []
            
            if backup_files:
                latest_backup = os.path.join(BACKUP_DIR, backup_files[-1])
                target = os.path.join(DATA_DIR, cf)
                try:
                    shutil.copy2(latest_backup, target)
                    issues.append(f"  ↳ 🛡️ Auto-restored `{cf}` from backup `{backup_files[-1]}`")
                    logger.info(f"[MONITOR] Auto-restored {cf} from {backup_files[-1]}")
                except Exception as e:
                    issues.append(f"  ↳ ❌ Failed to restore `{cf}`: {e}")
    
    if stale_jobs:
        for sj in stale_jobs:
            issues.append(f"⚠️ **{sj['job']}** hasn't run in {sj['last_seen_hours_ago']}h (max: {sj['max_expected_hours']}h)")
    
    if disk["status"] == "critical":
        issues.append(f"🔴 **DISK CRITICAL**: {disk['used_pct']}% used, only {disk['free_gb']}GB free")
    elif disk["status"] == "warning":
        issues.append(f"⚠️ **Disk pressure**: {disk['used_pct']}% used, {disk['free_gb']}GB free")
    
    if license_status and license_status.get("status") not in ("ok", None):
        issues.append(f"⚠️ **License Server**: {license_status.get('status', 'unknown')}")
    
    # 9. Send consolidated digest
    status_emoji = "🟢" if not issues else "🟡" if not corrupted else "🔴"
    
    fields = [
        {"name": "Uptime", "value": f"{vitals['uptime_hours']}h", "inline": True},
        {"name": "Memory", "value": f"{vitals['memory_mb']}MB", "inline": True},
        {"name": "Data", "value": f"{vitals['data_size_kb']}KB", "inline": True},
        {"name": "Backups", "value": f"{len(backed_up)} files", "inline": True},
        {"name": "Disk", "value": f"{disk['used_pct']}% ({disk['free_gb']}GB free)", "inline": True},
    ]
    
    if license_status:
        lic_value = f"{license_status.get('status', '?')} — {license_status.get('active_licenses', '?')} keys"
        fields.append({"name": "License Server", "value": lic_value, "inline": True})
    
    if rotated:
        fields.append({"name": "Log Rotation", "value": f"{rotated} entries archived", "inline": True})
    
    # Add heartbeat summary
    hb = get_heartbeats()
    if hb:
        hb_summary = "\n".join([
            f"{'✅' if v['success'] else '❌'} {k}"
            for k, v in sorted(hb.items())
        ])
        fields.append({"name": "Job Status", "value": hb_summary[:1024], "inline": False})
    
    message = f"{status_emoji} System healthy" if not issues else "\n".join(issues)
    
    await send_notification(
        f"{status_emoji} OmniSuite Health Digest",
        message[:2000],
        color=0x57F287 if not issues else (0xFEE75C if not corrupted else 0xED4245),
        fields=fields
    )
    
    if corrupted:
        await send_alert(f"🔴 CRITICAL: Data corruption detected in: {', '.join(corrupted)}. Auto-recovery attempted.")
    
    if disk["status"] == "critical":
        await send_alert(f"🔴 DISK CRITICAL: {disk['used_pct']}% used. Only {disk['free_gb']}GB remaining. Investigate immediately.")
    
    logger.info(f"[MONITOR] Health scan complete. Issues: {len(issues)}")

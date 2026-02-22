# -*- coding: utf-8 -*-
"""
API Routes for log retrieval
"""

from flask import jsonify, request
import uuid

from app import app
from jobs import _log_retrieval_jobs, run_log_retrieval_job, launch_dispatch_for_job
from snapshots import get_all_snapshots, delete_log_snapshot, save_snapshots_to_disk
import os


@app.route("/api/logs/retrieve", methods=["POST"])
def api_logs_retrieve():
    """Start a background job to retrieve log files from NFS and launch dispatch"""
    data = request.json
    project = data.get("project", "")
    date = data.get("date", "")
    
    if not project or not date:
        return jsonify({"success": False, "error": "project and date required"}), 400
    
    job_id = str(uuid.uuid4())
    target_dir = os.path.dirname(os.path.abspath(__file__))
    
    _log_retrieval_jobs[job_id] = {
        "status": "starting",
        "progress": "Looking up hostname for " + project + "...",
        "project": project,
        "date": date,
        "created_at": import_time.time(),
        "copied": 0,
        "total_files": 0,
        "dispatch_launched": False,
        "error": None
    }
    
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor(max_workers=5)
    executor.submit(run_log_retrieval_job, job_id, project, date, target_dir)
    
    return jsonify({
        "success": True,
        "job_id": job_id,
        "status": "starting",
        "project": project,
        "date": date
    })


@app.route("/api/logs/retrieve/status/<job_id>")
def api_logs_retrieve_status(job_id):
    """Get status of a log retrieval job"""
    if job_id not in _log_retrieval_jobs:
        return jsonify({"success": False, "error": "Job not found"}), 404
    
    job = _log_retrieval_jobs[job_id]
    return jsonify({
        "success": True,
        "job_id": job_id,
        **job
    })


@app.route("/api/logs/local")
def api_logs_local():
    """List log files currently in the local import_logs directory"""
    try:
        import glob
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")
        
        log_files = glob.glob(os.path.join(logs_dir, "**/log_*.log*"), recursive=True)
        
        files_info = []
        dates = set()
        projects = set()
        
        for f in log_files:
            basename = os.path.basename(f)
            rel_path = os.path.relpath(f, logs_dir)
            
            import re
            match = re.match(r'log_(\d{4}_\d{2}_\d{2})', basename)
            date_str = match.group(1).replace('_', '-') if match else "unknown"
            dates.add(date_str)
            
            path_parts = rel_path.split(os.sep)
            if len(path_parts) > 1 and path_parts[0] == "Logger":
                projects.add(path_parts[1])
            
            files_info.append({
                "name": basename,
                "path": rel_path,
                "size": os.path.getsize(f),
                "date": date_str,
                "compressed": basename.endswith(".bz2")
            })

        files_info.sort(key=lambda x: x["name"], reverse=True)
        
        return jsonify({
            "success": True,
            "logs_dir": logs_dir,
            "total_files": len(files_info),
            "dates": sorted(dates, reverse=True),
            "projects": sorted(projects),
            "files": files_info
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/logs/snapshots")
def api_logs_snapshots():
    """List all available log snapshots"""
    snapshots = get_all_snapshots()
    return jsonify({
        "success": True,
        "count": len(snapshots),
        "snapshots": snapshots
    })


@app.route("/api/logs/snapshots/<project>/<date>")
def api_logs_snapshot_detail(project, date):
    """Get details of a specific snapshot"""
    from snapshots import get_log_snapshot
    key = f"{project}_{date}"
    snapshot = get_log_snapshot(project, date)

    if not snapshot:
        return jsonify({"success": False, "error": f"Snapshot not found for {project} on {date}"}), 404

    return jsonify({
        "success": True,
        "key": key,
        **snapshot
    })


@app.route("/api/logs/snapshots/<project>/<date>", methods=["DELETE"])
def api_logs_snapshot_delete(project, date):
    """Delete a specific snapshot"""
    key = f"{project}_{date}"

    if not delete_log_snapshot(key):
        return jsonify({"success": False, "error": f"Snapshot not found for {project} on {date}"}), 404

    save_snapshots_to_disk()

    return jsonify({
        "success": True,
        "message": f"Snapshot deleted for {project} on {date}"
    })


@app.route("/api/logs/snapshots/cleanup", methods=["POST"])
def api_logs_snapshots_cleanup():
    """Clean up old snapshots (>2 hours - same as dispatch)"""
    from snapshots import cleanup_old_snapshots
    count = cleanup_old_snapshots(max_age_days=0.083)
    return jsonify({
        "success": True,
        "message": f"Cleaned up {count} old snapshots"
    })


import time as import_time

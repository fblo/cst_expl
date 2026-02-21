# -*- coding: utf-8 -*-
"""
Jobs module - Background tasks for log retrieval and dispatch management
"""

import os
import glob
import subprocess
import shutil
import time as time_mod
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from config import NFS_CONFIG, SSH_CONFIG
from dispatch import (
    register_dispatch,
    cleanup_stale_dispatches,
    _dispatch_info,
    _dispatch_ports_by_date
)
from snapshots import (
    get_log_snapshot,
    save_log_snapshot
)
from paths import (
    get_nfs_log_path,
    get_hostnames_for_project,
    get_local_hostnames_for_project,
    get_ssh_hostname_for_project
)
from mysql_queries import _get_project_hostname_from_mysql

# Job executor
_job_executor = ThreadPoolExecutor(max_workers=5)

# Log retrieval jobs storage
_log_retrieval_jobs = {}


def run_log_retrieval_job(job_id: str, project: str, date: str, target_dir: str):
    """Background job: copy log files from NFS or SSH to local directory, then launch dispatch"""
    try:
        _log_retrieval_jobs[job_id]["status"] = "running"

        today_str = time_mod.strftime("%Y-%m-%d")
        is_today = (date == today_str)
        
        # Check existing snapshot
        existing_snapshot = get_log_snapshot(project, date)

        if existing_snapshot:
            snapshot_port = existing_snapshot.get("port")
            snapshot_dir = existing_snapshot.get("directory")
            snapshot_files_count = existing_snapshot.get("files_count", 0)

            if snapshot_port and snapshot_port in _dispatch_info:
                info = _dispatch_info.get(snapshot_port, {})
                process = info.get("process")
                if process and process.poll() is None:
                    _log_retrieval_jobs[job_id]["progress"] = f"✅ Snapshot: dispatch actif sur port {snapshot_port}"
                    _log_retrieval_jobs[job_id]["cached"] = True
                    _log_retrieval_jobs[job_id]["dispatch_port"] = snapshot_port
                    _log_retrieval_jobs[job_id]["directory"] = snapshot_dir
                    _log_retrieval_jobs[job_id]["status"] = "done"
                    _log_retrieval_jobs[job_id]["copied"] = snapshot_files_count
                    _log_retrieval_jobs[job_id]["snapshot_used"] = True

                    if date not in _dispatch_ports_by_date:
                        _dispatch_ports_by_date[date] = snapshot_port
                    return

            # Check local logs
            if os.path.exists(snapshot_dir):
                existing_logs = glob.glob(os.path.join(snapshot_dir, "**", "log_*.log"), recursive=True)
                existing_logs_compressed = glob.glob(os.path.join(snapshot_dir, "**", "log_*.bz2"), recursive=True)

                if existing_logs or existing_logs_compressed:
                    _log_retrieval_jobs[job_id]["progress"] = "📁 Logs locaux détectés, lancement dispatch..."
                    _log_retrieval_jobs[job_id]["cached"] = True
                    _log_retrieval_jobs[job_id]["directory"] = snapshot_dir
                    _log_retrieval_jobs[job_id]["files_source"] = "local"

                    cleanup_stale_dispatches(7200)
                    launch_dispatch_for_job(job_id, project, date, snapshot_dir)
                    return

        # No snapshot - proceed with retrieval
        cleanup_stale_dispatches(7200)

        if is_today:
            # For today's logs, first get svc_hostname to connect to
            _log_retrieval_jobs[job_id]["progress"] = f"🔍 Recherche du hostname SSH pour {project}..."
            svc_hostname = get_ssh_hostname_for_project(project)

            if not svc_hostname:
                _log_retrieval_jobs[job_id]["status"] = "error"
                _log_retrieval_jobs[job_id]["error"] = f"ERREUR: Aucun hostname SSH trouvé pour {project}"
                return

            # Connect to svc_hostname to get the actual ps_hostname
            _log_retrieval_jobs[job_id]["progress"] = f"🔍 Connexion à {svc_hostname} pour obtenir le ps_hostname..."
            logger.info(f"[SSH] Connecting to {svc_hostname} to get ps_hostname")

            ssh_cmd = [
                "sshpass", "-p", SSH_CONFIG["password"],
                "ssh", "-o", "StrictHostKeyChecking=no",
                "-o", "PubkeyAcceptedAlgorithms=+ssh-rsa",
                "-o", "HostKeyAlgorithms=+ssh-rsa",
                "-o", "KexAlgorithms=+diffie-hellman-group1-sha1",
                f"{SSH_CONFIG['user']}@{svc_hostname}",
                "hostname"
            ]

            logger.info(f"[SSH] Command: {' '.join(ssh_cmd)}")

            ssh_result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=60)

            logger.info(f"[SSH] Return code: {ssh_result.returncode}")
            logger.info(f"[SSH] Stdout: {ssh_result.stdout}")
            logger.info(f"[SSH] Stderr: {ssh_result.stderr}")

            if ssh_result.returncode != 0:
                _log_retrieval_jobs[job_id]["status"] = "error"
                _log_retrieval_jobs[job_id]["error"] = f"ERREUR: Impossible de se connecter à {svc_hostname} pour obtenir le ps_hostname"
                return

            hostname = ssh_result.stdout.strip()
            logger.info(f"[SSH] Obtenu ps_hostname: {hostname}")
        else:
            # For past days, use NFS hostname
            _log_retrieval_jobs[job_id]["progress"] = f"🔍 Recherche des hostnames pour {project} dans MySQL..."
            valid_hostnames = get_hostnames_for_project(project)

            if not valid_hostnames:
                _log_retrieval_jobs[job_id]["status"] = "error"
                _log_retrieval_jobs[job_id]["error"] = f"ERREUR, NFS vers ccc_logs non monté ! ({NFS_CONFIG['mount_directory']})"
                return

            hostname = valid_hostnames[0]
        date_based_dir = os.path.join(target_dir, "import_logs", f"{project}_{date}")

        if is_today:
            # SSH retrieval for today's logs
            _log_retrieval_jobs[job_id]["progress"] = "🔍 Récupération des logs du jour via SSH..."
            
            logger_dir = os.path.join(date_based_dir, "Logger", project, "_", "ccenter_ccxml", "Ccxml", hostname)
            os.makedirs(logger_dir, exist_ok=True)
            
            date_pattern = date.replace('-', '_')
            remote_dir = os.path.join(SSH_CONFIG["remote_base_path"], project, "Logger", project, "_", "ccenter_ccxml", "Ccxml", hostname)
            remote_pattern = f"log_{date_pattern}_*.log"
            
            _log_retrieval_jobs[job_id]["progress"] = f"📥 SCP: copie des logs {date} depuis {hostname}..."

            logger.info(f"[SCP] Starting SCP from {hostname} for project {project} on {date}")
            logger.info(f"[SCP] Remote path: {remote_dir}/{remote_pattern}")
            logger.info(f"[SCP] Local path: {logger_dir}")

            sshpass_cmd = [
                "sshpass", "-p", SSH_CONFIG["password"],
                "scp", "-o", "StrictHostKeyChecking=no",
                "-o", "PubkeyAcceptedAlgorithms=+ssh-rsa",
                "-o", "HostKeyAlgorithms=+ssh-rsa",
                "-o", "KexAlgorithms=+diffie-hellman-group1-sha1",
                f"{SSH_CONFIG['user']}@{hostname}:{remote_dir}/{remote_pattern}",
                logger_dir + "/"
            ]

            # logger.info(f"[SCP] Command: {' '.join(sshpass_cmd)}")

            scp_result = subprocess.run(sshpass_cmd, capture_output=True, text=True, timeout=300)

            logger.info(f"[SCP] Return code: {scp_result.returncode}")
            logger.info(f"[SCP] Stdout: {scp_result.stdout}")
            logger.info(f"[SCP] Stderr: {scp_result.stderr}")

            if scp_result.returncode != 0:
                if "sshpass" in scp_result.stderr or "not found" in scp_result.stderr.lower():
                    _log_retrieval_jobs[job_id]["error"] = "ERREUR: sshpass non installé"
                    _log_retrieval_jobs[job_id]["status"] = "error"
                    return

            copied_logs = glob.glob(os.path.join(logger_dir, "log_*.log"))
            copied = len(copied_logs)

            if copied == 0:
                _log_retrieval_jobs[job_id]["error"] = f"Aucun fichier log_{date_pattern}_*.log trouvé"
                _log_retrieval_jobs[job_id]["status"] = "error"
                return

            _log_retrieval_jobs[job_id]["progress"] = f"✅ {copied} fichiers copiés via SSH"
            _log_retrieval_jobs[job_id]["copied"] = copied
            _log_retrieval_jobs[job_id]["files_source"] = "ssh"
            
            _log_retrieval_jobs[job_id]["progress"] = "🚀 Lancement du dispatch..."
            cleanup_stale_dispatches(7200)
            launch_dispatch_for_job(job_id, project, date, date_based_dir)
            return

        # NFS retrieval for past days
        nfs_path = get_nfs_log_path(hostname, project)

        if not nfs_path or not os.path.exists(nfs_path):
            _log_retrieval_jobs[job_id]["status"] = "error"
            _log_retrieval_jobs[job_id]["error"] = f"Répertoire NFS introuvable: {nfs_path}"
            return

        logger_dir = os.path.join(date_based_dir, "Logger", project, "_", "ccenter_ccxml", "Ccxml", hostname)
        os.makedirs(logger_dir, exist_ok=True)

        existing_logs = glob.glob(os.path.join(logger_dir, "log_*.log"))
        existing_logs_compressed = glob.glob(os.path.join(logger_dir, "log_*.bz2"))

        if existing_logs or existing_logs_compressed:
            total_files = len(existing_logs) + len(existing_logs_compressed)
            _log_retrieval_jobs[job_id]["progress"] = f"✅ Logs déjà récupérés ({total_files} fichiers)"
            _log_retrieval_jobs[job_id]["copied"] = total_files
            _log_retrieval_jobs[job_id]["cached"] = True
            is_cached = True
        else:
            is_cached = False
            date_pattern = date.replace('-', '_')
            pattern = os.path.join(nfs_path, f"log_{date_pattern}*")
            nfs_files = glob.glob(pattern)
            
            if not nfs_files:
                _log_retrieval_jobs[job_id]["status"] = "error"
                _log_retrieval_jobs[job_id]["error"] = f"Aucun fichier log_{date_pattern}* trouvé"
                return

            total_files = len(nfs_files)
            _log_retrieval_jobs[job_id]["total_files"] = total_files
            _log_retrieval_jobs[job_id]["progress"] = f"📥 {total_files} fichiers trouvés sur NFS"

            copied = 0
            decompressed = 0
            errors = []

            for f in nfs_files:
                basename = os.path.basename(f)
                dest = os.path.join(logger_dir, basename)

                try:
                    shutil.copy2(f, dest)
                    copied += 1

                    if dest.endswith(".bz2"):
                        _log_retrieval_jobs[job_id]["progress"] = f"🗜️ Décompression {basename}..."
                        decompressed_path = dest[:-4]
                        import bz2
                        with bz2.open(dest, 'rb') as bz_file:
                            with open(decompressed_path, 'wb') as out_file:
                                shutil.copyfileobj(bz_file, out_file)
                        os.remove(dest)
                        decompressed += 1

                    _log_retrieval_jobs[job_id]["copied"] = copied
                except Exception as e:
                    errors.append(f"Copie {basename}: {str(e)}")

        # Launch dispatch
        _log_retrieval_jobs[job_id]["progress"] = "🚀 Lancement du dispatch..."
        launch_dispatch_for_job(job_id, project, date, date_based_dir, is_cached=is_cached)

    except Exception as e:
        _log_retrieval_jobs[job_id]["status"] = "error"
        _log_retrieval_jobs[job_id]["error"] = str(e)


def launch_dispatch_for_job(job_id: str, project: str, date: str, logs_dir: str, is_cached: bool = False):
    """Launch dispatch after log retrieval"""
    try:
        from get_users_and_calls import RlogDispatcher
        RlogDispatcher.reset()

        dispatcher = RlogDispatcher(logs_dir)

        # Find available port
        import socket
        for port in range(35000, 35200):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                if result != 0:
                    dispatcher.port = port
                    break
            except:
                pass

        logs_path = os.path.join(logs_dir, "Logger")
        
        env = os.environ.copy()
        env["PATH"] = env.get("PATH", "") + ":/opt/lampp/bin"

        interface_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_interface.xml")
        if not os.path.exists(interface_path):
            interface_path = os.path.join(logs_dir, "debug_interface.xml")

        cmd = [
            dispatcher.DISPATCH_BIN,
            "-slave", str(dispatcher.port),
            "-logs", logs_path,
            "-interface", interface_path,
            "-stderr"
        ]

        dispatcher.process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )

        time_mod.sleep(10)

        if dispatcher.process.poll() is not None:
            stderr = dispatcher.process.stderr.read().decode() if dispatcher.process.stderr else ""
            raise RuntimeError(f"Dispatch arrêté: {stderr}")

        dispatcher._last_activity = time_mod.time()
        day = date.replace("-", "_")
        dispatcher._load_day(day)
        time_mod.sleep(2)

        register_dispatch(date, dispatcher.port, dispatcher.process, project)

        files_count = len(glob.glob(os.path.join(logs_dir, "**", "log_*.log*"), recursive=True))
        save_log_snapshot(project, date, dispatcher.port, logs_dir, files_count)

        _log_retrieval_jobs[job_id]["status"] = "done"
        _log_retrieval_jobs[job_id]["progress"] = f"✅ Terminé. Dispatch sur port {dispatcher.port}"
        _log_retrieval_jobs[job_id]["dispatch_port"] = dispatcher.port
        _log_retrieval_jobs[job_id]["directory"] = logs_dir

    except Exception as e:
        _log_retrieval_jobs[job_id]["status"] = "error"
        _log_retrieval_jobs[job_id]["error"] = str(e)
        _log_retrieval_jobs[job_id]["progress"] = f"❌ Erreur: {str(e)}"


# Logging setup
import logging
logger = logging.getLogger("cccp")

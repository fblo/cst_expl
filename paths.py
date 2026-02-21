# -*- coding: utf-8 -*-
"""
NFS and SSH paths module
Handles paths for NFS and SSH log retrieval
"""

import os
import glob
import logging
from typing import List, Optional
from config import NFS_CONFIG, SSH_CONFIG

logger = logging.getLogger("cccp")


def get_nfs_hostnames() -> List[str]:
    """Get all hostnames available in NFS mount"""
    nfs_dir = NFS_CONFIG["mount_directory"]
    if not os.path.exists(nfs_dir):
        return []
    
    hostnames = []
    try:
        for item in os.listdir(nfs_dir):
            if os.path.isdir(os.path.join(nfs_dir, item)) and not item.startswith('.'):
                hostnames.append(item)
    except Exception as e:
        logger.warning(f"Error listing NFS hostnames: {e}")
    
    return hostnames


def get_nfs_projects_for_hostname(hostname: str) -> List[str]:
    """Get all projects available for a hostname in NFS"""
    base_path = os.path.join(NFS_CONFIG["mount_directory"], hostname, "opt", "consistent", "logs")
    if not os.path.exists(base_path):
        return []
    
    projects = []
    try:
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path):
                projects.append(item)
    except Exception as e:
        logger.warning(f"Error listing NFS projects for {hostname}: {e}")
    
    return projects


def get_nfs_log_path(hostname: str, project: str) -> Optional[str]:
    """Get the full path to logs for a given hostname and project"""
    nfs_dir = NFS_CONFIG["mount_directory"]
    
    # Path structure: {mount}/interact-iv/{hostname}/opt/consistent/logs/{project}/Logger/{project}/_/ccenter_ccxml/Ccxml/{hostname}
    ccxml_base = os.path.join(
        nfs_dir, "interact-iv", hostname, "opt", "consistent", "logs", project,
        "Logger", project, "_", "ccenter_ccxml", "Ccxml"
    )
    
    if not os.path.exists(ccxml_base):
        return None
        
    try:
        exact_path = os.path.join(ccxml_base, hostname)
        if os.path.exists(exact_path):
            return exact_path
            
        subdirs = [d for d in os.listdir(ccxml_base) if d.startswith(hostname)]
        if subdirs:
            return os.path.join(ccxml_base, subdirs[0])
    except Exception:
        pass
        
    return None


def get_local_hostnames_for_project(project: str) -> List[str]:
    """Find hostnames for a project in local import_logs directory"""
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")
    
    hostnames = set()
    
    # Look for date-based structure: {PROJECT}_{DATE}/Logger/{PROJECT}/_/ccenter_ccxml/Ccxml/HOSTNAME
    date_pattern = os.path.join(logs_dir, f"{project}_*", "Logger", project, "_", "ccenter_ccxml", "Ccxml", "*")
    for path in glob.glob(date_pattern):
        hostname = os.path.basename(path)
        if hostname and not hostname.startswith('.') and '_' not in hostname:
            hostnames.add(hostname)
    
    # Also check old structure: Logger/PROJECT/*/ccenter_ccxml/Ccxml/HOSTNAME
    old_pattern = os.path.join(logs_dir, "Logger", project, "*", "ccenter_ccxml", "Ccxml", "*")
    for path in glob.glob(old_pattern):
        hostname = os.path.basename(path)
        if hostname and not hostname.startswith('.') and '_' not in hostname:
            hostnames.add(hostname)
    
    if hostnames:
        logger.info(f"Local hostnames found for {project}: {list(hostnames)}")
    
    return list(hostnames)


def get_local_log_path(hostname: str, project: str) -> str:
    """Get the local log path for a given hostname and project"""
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")
    return os.path.join(logs_dir, "Logger", project, "_", "ccenter_ccxml", "Ccxml", hostname)


def get_hostnames_for_project(project: str) -> List[str]:
    """Get hostnames for a project - checks both NFS and local logs"""
    # First check local logs
    local_hostnames = get_local_hostnames_for_project(project)
    if local_hostnames:
        logger.info(f"Local hostnames found for {project}: {local_hostnames}")
        return local_hostnames

    # Then check NFS via MySQL
    from mysql_queries import _get_project_hostname_from_mysql
    mysql_result = _get_project_hostname_from_mysql(project)

    if mysql_result:
        ps_hostname = mysql_result.get("ps_hostname")
        svc_hostname = mysql_result.get("svc_hostname")

        if ps_hostname:
            path = get_nfs_log_path(ps_hostname, project)
            logger.info(f"MySQL for {project}: ps_hostname={ps_hostname}, svc_hostname={svc_hostname}")
            logger.info(f"NFS path check: {path} (exists: {os.path.exists(path) if path else False})")

            if path and os.path.exists(path):
                return [ps_hostname]
            else:
                if svc_hostname and svc_hostname != ps_hostname:
                    path2 = get_nfs_log_path(svc_hostname, project)
                    if path2 and os.path.exists(path2):
                        logger.info(f"Using svc_hostname {svc_hostname} instead of ps_hostname {ps_hostname}")
                        return [svc_hostname]

    return []


def get_ssh_hostname_for_project(project: str) -> Optional[str]:
    """Get SSH hostname for a project - uses svc_hostname or cccip for today's logs"""
    from mysql_queries import _get_project_hostname_from_mysql
    mysql_result = _get_project_hostname_from_mysql(project)

    if mysql_result:
        # First try svc_hostname
        svc_hostname = mysql_result.get("svc_hostname")
        if svc_hostname:
            return svc_hostname

        # Then try cccip
        cccip = mysql_result.get("cccip")
        if cccip:
            return cccip

        # Fallback to ps_hostname
        ps_hostname = mysql_result.get("ps_hostname")
        if ps_hostname:
            return ps_hostname

    return None


def get_ssh_remote_path(hostname: str, project: str) -> str:
    """Get the SSH remote path for today's logs"""
    return os.path.join(
        SSH_CONFIG["remote_base_path"],
        project,
        "Logger",
        project,
        "_",
        "ccenter_ccxml",
        "Ccxml",
        hostname
    )

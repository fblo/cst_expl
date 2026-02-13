# -*- coding: utf-8 -*-
"""
MySQL queries module
Handles all database queries
"""

import mysql.connector
from typing import List, Dict, Optional
import logging
from config import MYSQL_CONFIG

logger = logging.getLogger("cccp")


def get_servers_from_mysql() -> List[Dict]:
    """Fetch servers from MySQL database"""
    query = """
        SELECT
            p.name AS project, 
            v.cccip, 
            g.ccc_dispatch_port, 
            g.ccc_proxy_port,
            v.vocalnode AS vocal_node
        FROM 
            interactivportal.Global_referential g
        JOIN 
            interactivportal.Projects p ON g.customer_id = p.id
        JOIN 
            interactivdbmaster.master_vocalnodes v ON g.cst_node = v.vocalnode
        WHERE p.active = 1
    """
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"MySQL query error: {e}")
        return []


def _get_project_hostname_from_mysql(project_name: str) -> Optional[Dict]:
    """Resolve project name to vocal hostname using MySQL"""
    query = """
        SELECT
            v.cccip,
            g.cst_node,
            v.hostname AS svc_hostname
        FROM
            interactivportal.Global_referential g
        JOIN
            interactivportal.Projects p ON g.customer_id = p.id
        JOIN
            interactivdbmaster.master_vocalnodes v ON g.cst_node = v.vocalnode
        WHERE p.name = %s
    """
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (project_name,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            cst_node = result.get("cst_node")
            svc_hostname = result.get("svc_hostname")

            if svc_hostname:
                ps_hostname = svc_hostname.replace("svc-", "ps-", 1)
            elif cst_node:
                ps_hostname = cst_node
                svc_hostname = None
            else:
                return None

            return {
                "cst_node": cst_node,
                "svc_hostname": svc_hostname,
                "ps_hostname": ps_hostname,
            }
    except Exception as e:
        logger.error(f"MySQL query error for {project_name}: {e}")
    return None


def get_nfs_projects_from_mysql() -> List[str]:
    """Get all projects that have NFS logs in MySQL"""
    query = """
        SELECT DISTINCT p.name AS project
        FROM interactivportal.Projects p
        JOIN interactivportal.Global_referential g ON p.id = g.customer_id
        WHERE p.active = 1
    """
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute(query)
        results = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"MySQL query error: {e}")
        return []

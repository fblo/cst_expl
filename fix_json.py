            except json.JSONDecodeError:
                return {"connected": False, "sessions": [], "error": "JSON decode error"}
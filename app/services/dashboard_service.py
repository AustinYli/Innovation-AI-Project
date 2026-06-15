from app.db.repository import (
    get_dashboard_summary,
    list_flagged_wallets,
    list_recent_wallets,
)


def get_dashboard_summary_response() -> dict:
    summary = get_dashboard_summary()
    return {
        **summary,
        "message": "Dashboard summary loaded.",
    }


def get_recent_wallets_response(limit: int = 20) -> dict:
    result = list_recent_wallets(limit=limit)
    return {
        **result,
        "count": len(result["wallets"]),
        "message": "Recent wallets loaded.",
    }


def get_flagged_wallets_response(limit: int = 20) -> dict:
    result = list_flagged_wallets(limit=limit)
    return {
        **result,
        "count": len(result["wallets"]),
        "message": "Flagged wallets loaded.",
    }

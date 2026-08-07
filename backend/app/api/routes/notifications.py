from typing import List, Optional

from fastapi import APIRouter, Depends

from app.config.settings import settings
from app.models.topbar import Notification
from app.services.graph_query_service import GraphQueryService


def get_query_service():
    if not settings.NEO4J_URI:
        yield None
        return

    service = None
    try:
        service = GraphQueryService(
            uri=settings.NEO4J_URI, user=settings.NEO4J_USERNAME, password=settings.NEO4J_PASSWORD
        )
    except Exception:
        service = None

    try:
        yield service
    finally:
        if service is not None:
            try:
                service.close()
            except Exception:
                pass


from app.core.security import User, get_current_user_strict

router = APIRouter()


@router.get("/all", response_model=List[Notification])
def get_notifications(
    query_service: Optional[GraphQueryService] = Depends(get_query_service),
    user: User = Depends(get_current_user_strict),
) -> List[Notification]:

    aggs = {}
    if query_service:
        try:
            aggs = query_service.get_dashboard_aggregations()
        except Exception:
            aggs = {}

    alerts = aggs.get("alerts", [])

    notifications = []

    # Add a static success notification
    notifications.append(
        Notification(
            id="notif-system-1",
            title="Scan Completed",
            message="Acme Bank core-banking-monorepo scan finished successfully.",
            time="2 hours ago",
            read=True,
            type="success",
        )
    )

    # Add alerts as notifications
    for idx, alert in enumerate(alerts):
        notifications.append(
            Notification(
                id=f"notif-alert-{idx}",
                title=str(alert["title"]),
                message=str(alert["reason"]),
                time="Just now" if idx == 0 else "1 hour ago",
                read=False,
                type="alert",
            )
        )

    return notifications

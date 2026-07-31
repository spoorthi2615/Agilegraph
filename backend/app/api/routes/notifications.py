from fastapi import APIRouter, Depends
from typing import List
from app.models.topbar import Notification
from app.services.graph_query_service import GraphQueryService
from app.config.settings import settings

def get_query_service():
    service = GraphQueryService(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USERNAME,
        password=settings.NEO4J_PASSWORD
    )
    try:
        yield service
    finally:
        service.close()
from datetime import datetime

router = APIRouter()

@router.get("/all", response_model=List[Notification])
def get_notifications(
    query_service: GraphQueryService = Depends(get_query_service)
) -> List[Notification]:
    
    # We will simulate the notification feed using the Critical Alerts from the Dashboard aggregations
    aggs = query_service.get_dashboard_aggregations()
    alerts = aggs.get("alerts", [])
    
    notifications = []
    
    # Add a static success notification
    notifications.append(Notification(
        id="notif-system-1",
        title="Scan Completed",
        message="Acme Bank core-banking-monorepo scan finished successfully.",
        time="2 hours ago",
        read=True,
        type="success"
    ))

    # Add alerts as notifications
    for idx, alert in enumerate(alerts):
        notifications.append(Notification(
            id=f"notif-alert-{idx}",
            title=str(alert["title"]),
            message=str(alert["reason"]),
            time="Just now" if idx == 0 else "1 hour ago",
            read=False,
            type="alert"
        ))
        
    return notifications

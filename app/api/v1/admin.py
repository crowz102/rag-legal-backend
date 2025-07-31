from fastapi import APIRouter, Request, Depends, HTTPException, status
from user_agents import parse as parse_user_agent
from app.core.dependencies import get_current_user
from app.schemas.user import User

router = APIRouter()

def is_admin(user: User = Depends(get_current_user)):
    print("DEBUG role:", user.role)
    if user.role.name.lower().strip().lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only"
        )
    return user

@router.get("/admin-info", tags=["Admin"])
async def get_client_info(
    request: Request,
    user: User = Depends(is_admin) 
):
    client_ip = request.client.host
    user_agent_str = request.headers.get("user-agent", "")
    user_agent = parse_user_agent(user_agent_str)

    return {
        "ip": client_ip,
        "user_agent": user_agent_str,
        "os": user_agent.os.family,
        "os_version": user_agent.os.version_string,
        "browser": user_agent.browser.family,
        "browser_version": user_agent.browser.version_string,
        "device": user_agent.device.family,
        "is_mobile": user_agent.is_mobile,
        "is_tablet": user_agent.is_tablet,
        "is_pc": user_agent.is_pc,
        "is_bot": user_agent.is_bot,
        "user": {
            "email": user.email,
            "role": user.role
        }
    }

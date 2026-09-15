from pydantic import BaseModel, EmailStr


class CurrentUser(BaseModel):
    id: int
    email: EmailStr
    is_staff: bool

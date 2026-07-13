from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
import uuid

# ========== Enums ==========
class UserRole(str, Enum):
    CUSTOMER = "customer"
    SERVICE_PROVIDER = "service_provider"

class ContractStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    DISPUTED = "disputed"

class MilestoneStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class Currency(str, Enum):
    USD = "USD"
    INR = "INR"

# ========== User Models ==========
class UserCreate(BaseModel):
    email: str
    phone_number: str
    full_name: str
    password: str
    user_role: UserRole = UserRole.CUSTOMER

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    phone_number: str
    full_name: str
    user_role: str
    vouch_score: float = 100.0
    total_contracts: int = 0

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class APIResponse(BaseModel):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[Dict[str, Any]] = None

# ========== Contract Models ==========
class Milestone(BaseModel):
    id: str = Field(default_factory=lambda: f"MS-{uuid.uuid4().hex[:8]}")
    title: str
    description: str = ""
    amount: float
    deadline: str  # ISO date string
    status: MilestoneStatus = MilestoneStatus.PENDING

class ContractCreate(BaseModel):
    title: str
    description: str = ""
    provider_phone: str
    total_amount: float
    currency: Currency = Currency.USD
    milestones: List[Milestone] = []

class ContractResponse(BaseModel):
    id: str
    title: str
    description: str = ""
    customer_id: str
    provider_id: Optional[str] = None
    provider_phone: str
    total_amount: float
    currency: str = "USD"
    status: str = "draft"
    milestones: List[Milestone] = []
    created_at: str = ""
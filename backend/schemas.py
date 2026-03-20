from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ---- Auth ----
class RegisterRequest(BaseModel):
    username: str = Field(min_length=6)
    full_name: str
    email: str
    contact_number: str
    address_line: str = ""
    pincode: str
    district: str = ""
    state: str = ""
    country: str = ""
    password: str = Field(min_length=8)
    company_name: str = ""


class LoginRequest(BaseModel):
    identifier: str  # username, email, or phone
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


# ---- User ----
class UserResponse(BaseModel):
    id: str
    username: str
    full_name: str
    email: str
    contact_number: str
    address_line: str
    pincode: str
    district: str
    state: str
    country: str
    company_name: str
    role: str
    plan_id: Optional[str]
    credits: float
    plan_expiry: Optional[str]
    created_at: str


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    contact_number: Optional[str] = None
    address_line: Optional[str] = None
    pincode: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    company_name: Optional[str] = None


# ---- Plans ----
class PlanResponse(BaseModel):
    id: str
    name: str
    credits: float
    price: float
    validity_months: int
    is_active: bool
    is_default_signup: bool
    description: str
    features: list[str]


class CreatePlanRequest(BaseModel):
    name: str
    credits: float
    price: float
    validity_months: int  # 0 = unlimited
    is_active: bool = True
    is_default_signup: bool = False
    description: str = ""
    features: list[str] = []


class UpdatePlanRequest(BaseModel):
    name: Optional[str] = None
    credits: Optional[float] = None
    price: Optional[float] = None
    validity_months: Optional[int] = None
    is_active: Optional[bool] = None
    is_default_signup: Optional[bool] = None
    description: Optional[str] = None
    features: Optional[list[str]] = None


# ---- Conversion ----
class ConversionHistoryResponse(BaseModel):
    id: str
    file_name: str
    date: str
    voucher_count: int
    credits_used: float
    xml_available: bool


class VoucherItem(BaseModel):
    date: str
    description: str
    debit: float
    credit: float
    type: str
    ledger: str


class GenerateXMLRequest(BaseModel):
    vouchers: list[VoucherItem]
    file_name: str


# ---- Feedback ----
class FeedbackRequest(BaseModel):
    full_name: str
    email: str
    contact: str
    message: str = Field(min_length=30)


class FeedbackResponse(BaseModel):
    id: str
    full_name: str
    email: str
    contact: str
    message: str
    created_at: str
    status: str


# ---- Admin ----
class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    credits_adjustment: Optional[float] = None
    plan_expiry: Optional[str] = None  # ISO date or null for unlimited


class AdminStatsResponse(BaseModel):
    total_users: int
    total_conversions: int
    total_vouchers: int
    total_credits_used: float


class DashboardStatsResponse(BaseModel):
    total_statements: int
    total_vouchers: int
    credits_used: float
    remaining_credits: float
    plan_expiry: Optional[str]
    recent_activity: list[ConversionHistoryResponse]


# ---- Generic ----
class MessageResponse(BaseModel):
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

from pydantic import BaseModel
from datetime import date
from typing import Optional
from datetime import datetime

class LeaveBalanceBase(BaseModel):
    total_days: int
    used_days: int


class VacationLeaveResponse(LeaveBalanceBase):
    vacation_id: int
    user_id: int
    last_updated: date

    class Config:
        from_attributes = True


class SickLeaveResponse(LeaveBalanceBase):
    sick_id: int
    user_id: int
    last_updated: date

    class Config:
        from_attributes = True


class EmergencyLeaveResponse(LeaveBalanceBase):
    emergency_id: int
    user_id: int
    last_updated: date

    class Config:
        from_attributes = True


class AllLeaveBalanceResponse(BaseModel):
    """Combined response for all leave types"""
    vacation_leave: VacationLeaveResponse
    sick_leave: SickLeaveResponse
    emergency_leave: EmergencyLeaveResponse


class UpdateLeaveRequest(BaseModel):
    """Request to update used days"""
    used_days: int
    reason: str

class LeaveRequestBase(BaseModel):
    used_days: int
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True


class VacationLeaveHistoryResponse(BaseModel):
    history: list[LeaveRequestBase]


class SickLeaveHistoryResponse(BaseModel):
    history: list[LeaveRequestBase]


class EmergencyLeaveHistoryResponse(BaseModel):
    history: list[LeaveRequestBase]

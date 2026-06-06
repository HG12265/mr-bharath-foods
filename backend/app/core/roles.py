from enum import Enum


class UserRole(str, Enum):
    CUSTOMER = "customer"
    PARTNER = "partner"
    WAREHOUSE = "warehouse"
    ADMIN = "admin"

# Access groups definitions for RBAC validation helpers
ROLE_HIERARCHY = {
    UserRole.CUSTOMER: {UserRole.CUSTOMER},
    UserRole.PARTNER: {UserRole.CUSTOMER, UserRole.PARTNER},
    UserRole.WAREHOUSE: {UserRole.CUSTOMER, UserRole.WAREHOUSE},
    UserRole.ADMIN: {UserRole.CUSTOMER, UserRole.PARTNER, UserRole.WAREHOUSE, UserRole.ADMIN},
}

def get_role_permissions(role: UserRole) -> set[UserRole]:
    return ROLE_HIERARCHY.get(role, {UserRole.CUSTOMER})

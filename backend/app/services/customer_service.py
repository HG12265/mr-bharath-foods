import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.exceptions import BaseAppException, NotFoundException
from app.core.validators import validate_phone_number, validate_pincode
from app.models.customer import Customer, CustomerAddress
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import AddressCreate, AddressUpdate, ProfileUpdate
from app.services.audit_service import AuditService


class CustomerService:
    def __init__(self, repository: CustomerRepository, audit_service: AuditService):
        self.repository = repository
        self.audit_service = audit_service

    async def get_profile(self, user_id: str) -> Customer:
        customer = await self.repository.get_by_id(user_id)
        if not customer:
            raise NotFoundException("Customer profile not found.")
        return customer

    async def update_profile(
        self,
        user_id: str,
        request: ProfileUpdate,
        ip_address: str | None = None
    ) -> Customer:
        customer = await self.get_profile(user_id)

        update_data: dict[str, Any] = {}
        if "first_name" in request.model_fields_set:
            if request.first_name is None:
                raise BaseAppException("First name cannot be null.", status_code=400)
            update_data["personal_details.first_name"] = request.first_name
        if "last_name" in request.model_fields_set:
            if request.last_name is None:
                raise BaseAppException("Last name cannot be null.", status_code=400)
            update_data["personal_details.last_name"] = request.last_name
        if "avatar_url" in request.model_fields_set:
            update_data["personal_details.avatar_url"] = request.avatar_url

        if update_data:
            update_data["updated_at"] = datetime.now(UTC)
            updated = await self.repository.update(user_id, update_data)
            if not updated:
                raise BaseAppException("Profile update execution failed.")

            await self.audit_service.log_action(
                action="UPDATE_PROFILE",
                target_collection="customers",
                user_id=user_id,
                target_id=user_id,
                ip_address=ip_address
            )
            return updated

        return customer

    async def add_address(
        self,
        user_id: str,
        request: AddressCreate,
        ip_address: str | None = None
    ) -> Customer:
        customer = await self.get_profile(user_id)
        validate_phone_number(request.phone)
        validate_pincode(request.pincode)

        address_id = str(uuid.uuid4())
        new_address = CustomerAddress(
            address_id=address_id,
            name=request.name,
            phone=request.phone,
            street=request.street,
            landmark=request.landmark,
            pincode=request.pincode,
            city=request.city,
            state=request.state,
            is_default_shipping=request.is_default_shipping,
            is_default_billing=request.is_default_billing
        )

        addresses = customer.addresses

        # If default settings are requested, unset prior flags first
        if request.is_default_shipping:
            for addr in addresses:
                addr.is_default_shipping = False
        if request.is_default_billing:
            for addr in addresses:
                addr.is_default_billing = False

        addresses.append(new_address)

        # Map to dict list for direct Mongo updates
        updated_list = [addr.model_dump() for addr in addresses]
        updated = await self.repository.update(
            user_id,
            {"addresses": updated_list, "updated_at": datetime.now(UTC)}
        )
        if not updated:
            raise BaseAppException("Add address operation failed.")

        await self.audit_service.log_action(
            action="ADD_ADDRESS",
            target_collection="customers",
            user_id=user_id,
            target_id=address_id,
            ip_address=ip_address
        )
        return updated

    async def update_address(
        self,
        user_id: str,
        address_id: str,
        request: AddressUpdate,
        ip_address: str | None = None
    ) -> Customer:
        customer = await self.get_profile(user_id)

        addresses = customer.addresses
        target_index = -1
        for i, addr in enumerate(addresses):
            if addr.address_id == address_id:
                target_index = i
                break

        if target_index == -1:
            raise NotFoundException(f"Address with identifier {address_id} not found.")

        addr_to_update = addresses[target_index]

        # Merge values
        if "name" in request.model_fields_set:
            if request.name is None:
                raise BaseAppException("Address name cannot be null.", status_code=400)
            addr_to_update.name = request.name
        if "phone" in request.model_fields_set:
            if request.phone is None:
                raise BaseAppException("Phone number cannot be null.", status_code=400)
            validate_phone_number(request.phone)
            addr_to_update.phone = request.phone
        if "street" in request.model_fields_set:
            if request.street is None:
                raise BaseAppException("Street cannot be null.", status_code=400)
            addr_to_update.street = request.street
        if "landmark" in request.model_fields_set:
            addr_to_update.landmark = request.landmark
        if "pincode" in request.model_fields_set:
            if request.pincode is None:
                raise BaseAppException("Pincode cannot be null.", status_code=400)
            validate_pincode(request.pincode)
            addr_to_update.pincode = request.pincode
        if "city" in request.model_fields_set:
            if request.city is None:
                raise BaseAppException("City cannot be null.", status_code=400)
            addr_to_update.city = request.city
        if "state" in request.model_fields_set:
            if request.state is None:
                raise BaseAppException("State cannot be null.", status_code=400)
            addr_to_update.state = request.state

        if "is_default_shipping" in request.model_fields_set:
            if request.is_default_shipping is None:
                raise BaseAppException("is_default_shipping cannot be null.", status_code=400)
            if request.is_default_shipping:
                for addr in addresses:
                    addr.is_default_shipping = False
            addr_to_update.is_default_shipping = request.is_default_shipping

        if "is_default_billing" in request.model_fields_set:
            if request.is_default_billing is None:
                raise BaseAppException("is_default_billing cannot be null.", status_code=400)
            if request.is_default_billing:
                for addr in addresses:
                    addr.is_default_billing = False
            addr_to_update.is_default_billing = request.is_default_billing

        updated_list = [addr.model_dump() for addr in addresses]
        updated = await self.repository.update(
            user_id,
            {"addresses": updated_list, "updated_at": datetime.now(UTC)}
        )
        if not updated:
            raise BaseAppException("Update address operation failed.")

        await self.audit_service.log_action(
            action="UPDATE_ADDRESS",
            target_collection="customers",
            user_id=user_id,
            target_id=address_id,
            ip_address=ip_address
        )
        return updated

    async def delete_address(
        self,
        user_id: str,
        address_id: str,
        ip_address: str | None = None
    ) -> Customer:
        customer = await self.get_profile(user_id)

        addresses = customer.addresses
        initial_len = len(addresses)
        filtered = [addr for addr in addresses if addr.address_id != address_id]

        if len(filtered) == initial_len:
            raise NotFoundException(f"Address with identifier {address_id} not found.")

        updated_list = [addr.model_dump() for addr in filtered]
        updated = await self.repository.update(
            user_id,
            {"addresses": updated_list, "updated_at": datetime.now(UTC)}
        )
        if not updated:
            raise BaseAppException("Delete address operation failed.")

        await self.audit_service.log_action(
            action="DELETE_ADDRESS",
            target_collection="customers",
            user_id=user_id,
            target_id=address_id,
            ip_address=ip_address
        )
        return updated

    async def set_default_address(
        self,
        user_id: str,
        address_id: str,
        default_type: str,
        ip_address: str | None = None
    ) -> Customer:
        customer = await self.get_profile(user_id)

        if default_type not in ["shipping", "billing", "both"]:
            raise BaseAppException("Invalid default type classification parameter.")

        addresses = customer.addresses
        found = False
        for addr in addresses:
            if addr.address_id == address_id:
                found = True
                break

        if not found:
            raise NotFoundException(f"Address with identifier {address_id} not found.")

        for addr in addresses:
            if default_type in ["shipping", "both"] and addr.is_default_shipping:
                addr.is_default_shipping = False
            if default_type in ["billing", "both"] and addr.is_default_billing:
                addr.is_default_billing = False

        for addr in addresses:
            if addr.address_id == address_id:
                if default_type in ["shipping", "both"]:
                    addr.is_default_shipping = True
                if default_type in ["billing", "both"]:
                    addr.is_default_billing = True
                break

        updated_list = [addr.model_dump() for addr in addresses]
        updated = await self.repository.update(
            user_id,
            {"addresses": updated_list, "updated_at": datetime.now(UTC)}
        )
        if not updated:
            raise BaseAppException("Toggle default address flag operation failed.")

        await self.audit_service.log_action(
            action=f"SET_DEFAULT_{default_type.upper()}_ADDRESS",
            target_collection="customers",
            user_id=user_id,
            target_id=address_id,
            ip_address=ip_address
        )
        return updated

    async def update_email(
        self,
        user_id: str,
        email: str,
        ip_address: str | None = None
    ) -> Customer:
        # Check if email is already taken
        existing = await self.repository.get_by_email(email)
        if existing and existing.id != user_id:
            raise BaseAppException("Email address is already in use by another account.", code="EMAIL_IN_USE", status_code=400)

        updated = await self.repository.update(
            user_id,
            {"auth.email": email, "updated_at": datetime.now(UTC)}
        )
        if not updated:
            raise BaseAppException("Email parameter update failed.")

        await self.audit_service.log_action(
            action="UPDATE_EMAIL",
            target_collection="customers",
            user_id=user_id,
            target_id=user_id,
            ip_address=ip_address
        )
        return updated

    async def update_phone(
        self,
        user_id: str,
        phone: str,
        ip_address: str | None = None
    ) -> Customer:
        validate_phone_number(phone)
        # Check if phone is already taken
        existing = await self.repository.get_by_phone(phone)
        if existing and existing.id != user_id:
            raise BaseAppException("Phone number is already in use by another account.", code="PHONE_IN_USE", status_code=400)

        updated = await self.repository.update(
            user_id,
            {"auth.phone": phone, "updated_at": datetime.now(UTC)}
        )
        if not updated:
            raise BaseAppException("Phone parameter update failed.")

        await self.audit_service.log_action(
            action="UPDATE_PHONE",
            target_collection="customers",
            user_id=user_id,
            target_id=user_id,
            ip_address=ip_address
        )
        return updated

    async def soft_delete_customer(
        self,
        user_id: str,
        ip_address: str | None = None
    ) -> bool:
        # Enforce profile deactivation
        success = await self.repository.soft_delete(user_id)
        if success:
            await self.audit_service.log_action(
                action="DEACTIVATE_ACCOUNT",
                target_collection="customers",
                user_id=user_id,
                target_id=user_id,
                ip_address=ip_address
            )
        return success

    async def update_customer_status(
        self,
        admin_user_id: str,
        target_user_id: str,
        status: str,
        ip_address: str | None = None
    ) -> Customer:
        if status not in ["active", "suspended", "inactive"]:
            raise BaseAppException("Invalid status coordinate.")

        updated = await self.repository.update(
            target_user_id,
            {"auth.status": status, "updated_at": datetime.now(UTC)}
        )
        if not updated:
            raise NotFoundException("Customer profile not found.")

        await self.audit_service.log_action(
            action=f"ADMIN_STATUS_CHANGE_{status.upper()}",
            target_collection="customers",
            user_id=admin_user_id,
            target_id=target_user_id,
            ip_address=ip_address
        )
        return updated

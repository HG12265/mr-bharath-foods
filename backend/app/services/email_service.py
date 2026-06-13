import base64
from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import settings
from app.models.order import Order
from app.models.shipment import Shipment
from app.services.audit_service import AuditService


class EmailService:
    def __init__(self, audit_service: AuditService):
        self.audit_service = audit_service
        self.brevo_url = "https://api.brevo.com/v3/smtp/email"

    def _get_base_template(self, title: str, content_html: str) -> str:
        """
        Returns a premium branded HTML wrapper matching Bharath Delight Foods aesthetics
        (Deep Green #0F3D2E and Gold accents).
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    background-color: #FAF9F6;
                    color: #1C2321;
                    margin: 0;
                    padding: 0;
                    -webkit-font-smoothing: antialiased;
                }}
                .wrapper {{
                    width: 100%;
                    background-color: #FAF9F6;
                    padding: 40px 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #FFFFFF;
                    border: 1px solid rgba(217, 164, 65, 0.15);
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(15, 61, 46, 0.05);
                }}
                .header {{
                    background-color: #0F3D2E;
                    padding: 30px;
                    text-align: center;
                    border-bottom: 3px solid #C89B3C;
                }}
                .header-title {{
                    color: #FAF9F6;
                    font-size: 24px;
                    font-weight: bold;
                    margin: 0;
                    letter-spacing: 1.5px;
                }}
                .header-tagline {{
                    color: #C89B3C;
                    font-size: 9px;
                    text-transform: uppercase;
                    letter-spacing: 3px;
                    margin-top: 5px;
                    font-weight: bold;
                }}
                .body {{
                    padding: 35px 30px;
                    line-height: 1.6;
                    font-size: 14px;
                }}
                .h2 {{
                    color: #0F3D2E;
                    font-size: 18px;
                    font-weight: bold;
                    margin-top: 0;
                    margin-bottom: 15px;
                }}
                .footer {{
                    background-color: #FAF9F6;
                    padding: 20px 30px;
                    text-align: center;
                    font-size: 11px;
                    color: #6B7280;
                    border-top: 1px solid rgba(217, 164, 65, 0.1);
                }}
                .btn {{
                    display: inline-block;
                    background-color: #0F3D2E;
                    color: #FAF9F6 !important;
                    text-decoration: none;
                    padding: 12px 24px;
                    font-weight: bold;
                    border-radius: 4px;
                    margin-top: 15px;
                    font-size: 12px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    border: 1px solid #C89B3C;
                }}
                .details-box {{
                    background-color: #FAF9F6;
                    border: 1px solid rgba(217, 164, 65, 0.15);
                    border-radius: 4px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .details-box table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .details-box th, .details-box td {{
                    text-align: left;
                    font-size: 13px;
                    padding: 6px 0;
                }}
                .details-box th {{
                    color: #0F3D2E;
                    width: 120px;
                }}
            </style>
        </head>
        <body>
            <div class="wrapper">
                <div class="container">
                    <div class="header">
                        <div class="header-title">BHARATH DELIGHT FOODS</div>
                        <div class="header-tagline">Food Done Right</div>
                    </div>
                    <div class="body">
                        {content_html}
                    </div>
                    <div class="footer">
                        &copy; {datetime.now(UTC).year} Bharath Delight Foods. All rights reserved.<br/>
                        Sourced responsibly. FSSAI & GST Certified.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    async def send_transactional_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        attachments: list[dict[str, Any]] | None = None,
        order_id: str | None = None,
    ) -> bool:
        """
        Performs POST request to Brevo Transactional Email REST endpoint.
        Logs audit EMAIL_SENT/EMAIL_FAILED.
        If key is dummy/missing, logs request details locally and mocks success.
        """
        api_key = settings.BREVO_API_KEY
        sender_email = settings.BREVO_SENDER_EMAIL or "no-reply@bharathdelightfoods.in"
        sender_name = settings.BREVO_SENDER_NAME

        import sys
        is_test = "pytest" in sys.modules or settings.ENVIRONMENT == "test"
        is_mock = is_test or not api_key or "dummy" in api_key.lower() or api_key.strip() == ""

        # Prepare attachments
        brevo_attachments = []
        if attachments:
            for attach in attachments:
                brevo_attachments.append({
                    "content": attach["content"],  # base64 encoded string
                    "name": attach["name"]
                })

        payload = {
            "sender": {"name": sender_name, "email": sender_email},
            "to": [{"email": to_email, "name": to_name}],
            "subject": subject,
            "htmlContent": html_content,
        }
        if brevo_attachments:
            payload["attachment"] = brevo_attachments

        if is_mock:
            # Mock mode - log details locally to stdout
            print(f"[MOCK EMAIL SERVICE] Sending email to {to_email} ({to_name})")
            print(f"Subject: {subject}")
            print(f"Sender: {sender_name} <{sender_email}>")
            print(f"Attachments count: {len(brevo_attachments)}")

            # Log sent audit log
            await self.audit_service.log_action(
                action="EMAIL_SENT",
                target_collection="orders",
                user_id="system",
                target_id=order_id,
                details={"to": to_email, "subject": subject, "mock": True}
            )
            return True

        # Live Brevo API POST
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.brevo_url, json=payload, headers=headers, timeout=10.0)
                if response.status_code in (200, 201, 202):
                    await self.audit_service.log_action(
                        action="EMAIL_SENT",
                        target_collection="orders",
                        user_id="system",
                        target_id=order_id,
                        details={"to": to_email, "subject": subject, "brevo_message_id": response.json().get("messageId")}
                    )
                    return True
                else:
                    error_msg = f"Brevo API error {response.status_code}: {response.text}"
                    await self.audit_service.log_action(
                        action="EMAIL_FAILED",
                        target_collection="orders",
                        user_id="system",
                        target_id=order_id,
                        details={"to": to_email, "subject": subject, "error": error_msg}
                    )
                    return False
        except Exception as exc:
            await self.audit_service.log_action(
                action="EMAIL_FAILED",
                target_collection="orders",
                user_id="system",
                target_id=order_id,
                details={"to": to_email, "subject": subject, "error": str(exc)}
            )
            return False

    async def send_order_confirmed_email(self, order: Order, pdf_bytes: bytes) -> bool:
        """
        Sends order confirmed email to customer with invoice attached.
        """
        cust_name = f"{order.customer_snapshot.first_name or ''} {order.customer_snapshot.last_name or ''}".strip()
        if not cust_name:
            cust_name = order.shipping_address_snapshot.full_name

        subject = f"Your Order Confirmed! - #{order.order_number}"
        content_html = f"""
        <div class="h2">Thank You for Your Order!</div>
        <p>Dear {cust_name},</p>
        <p>We are pleased to inform you that we have received and verified your payment. Your order <b>#{order.order_number}</b> has been confirmed and is now being packaged for dispatch.</p>

        <p>Your official invoice has been generated and is attached to this email as a PDF document for your records.</p>

        <div class="details-box">
            <h4 style="margin-top:0; color:#0F3D2E;">Order Summary</h4>
            <table>
                <tr>
                    <th>Order Number:</th>
                    <td>#{order.order_number}</td>
                </tr>
                <tr>
                    <th>Invoice Number:</th>
                    <td>{order.invoice_number or 'N/A'}</td>
                </tr>
                <tr>
                    <th>Grand Total:</th>
                    <td>INR {order.pricing.grand_total:,.2f}</td>
                </tr>
                <tr>
                    <th>Shipping To:</th>
                    <td>{order.shipping_address_snapshot.full_name}, {order.shipping_address_snapshot.city}</td>
                </tr>
            </table>
        </div>

        <p>Once your order leaves our warehouse, we will email you with the carrier details and tracking numbers so you can follow its transit.</p>
        <p>If you have any questions or require support, reply to this email or contact our customer team.</p>
        """

        # Encode PDF bytes to base64
        base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        attachments = [{
            "content": base64_pdf,
            "name": f"invoice-{order.invoice_number or order.order_number}.pdf"
        }]

        html_body = self._get_base_template("Order Confirmed", content_html)
        return await self.send_transactional_email(
            to_email=order.customer_snapshot.email,
            to_name=cust_name,
            subject=subject,
            html_content=html_body,
            attachments=attachments,
            order_id=order.id
        )

    async def send_payment_rejected_email(self, order: Order, reason: str) -> bool:
        """
        Sends email notifying that payment proof was rejected.
        """
        cust_name = f"{order.customer_snapshot.first_name or ''} {order.customer_snapshot.last_name or ''}".strip()
        if not cust_name:
            cust_name = order.shipping_address_snapshot.full_name

        subject = f"Action Required: Payment Verification Unsuccessful - #{order.order_number}"
        content_html = f"""
        <div class="h2" style="color: #C62828;">Payment Verification Unsuccessful</div>
        <p>Dear {cust_name},</p>
        <p>Thank you for submitting your payment proof screenshot for order <b>#{order.order_number}</b>. Unfortunately, our warehouse verification team was unable to verify the transfer.</p>

        <div class="details-box" style="border-left: 4px solid #C62828; background-color: #FEF2F2;">
            <h4 style="margin-top:0; color:#C62828;">Rejection Reason</h4>
            <p style="margin: 0; font-size: 13px;">{reason}</p>
        </div>

        <p><b>What you need to do:</b></p>
        <p>Please double-check your banking application or UPI transfer details. Make sure to capture a clear screenshot of the successful transaction showing the transaction ID and amount matching <b>INR {order.pricing.grand_total:,.2f}</b>, and re-submit it on the order details page.</p>

        <p style="text-align: center;">
            <a href="/order/{order.id}" class="btn" style="background-color:#C62828;">Upload Correct Proof</a>
        </p>

        <p>If you believe this is in error or require support, please contact our support team immediately.</p>
        """

        html_body = self._get_base_template("Payment Proof Verification Action Required", content_html)
        return await self.send_transactional_email(
            to_email=order.customer_snapshot.email,
            to_name=cust_name,
            subject=subject,
            html_content=html_body,
            order_id=order.id
        )

    async def send_shipment_created_email(self, order: Order, shipment: Shipment) -> bool:
        """
        Sends email when shipment is dispatched with carrier and tracking info.
        """
        cust_name = f"{order.customer_snapshot.first_name or ''} {order.customer_snapshot.last_name or ''}".strip()
        if not cust_name:
            cust_name = order.shipping_address_snapshot.full_name

        subject = f"Your Order has been Dispatched! - #{order.order_number}"

        delivery_date_str = (
            shipment.estimated_delivery_date.strftime("%d-%b-%Y")
            if shipment.estimated_delivery_date else
            "3-5 business days"
        )

        content_html = f"""
        <div class="h2">Your Order has been Dispatched!</div>
        <p>Dear {cust_name},</p>
        <p>Great news! Your order <b>#{order.order_number}</b> has been sealed and dispatched from our co-packer center. It is now on its way to you.</p>

        <div class="details-box">
            <h4 style="margin-top:0; color:#0F3D2E;">Delivery Tracking Details</h4>
            <table>
                <tr>
                    <th>Courier Partner:</th>
                    <td>{shipment.carrier_name}</td>
                </tr>
                <tr>
                    <th>Tracking Number:</th>
                    <td><code>{shipment.tracking_number}</code></td>
                </tr>
                {f"<tr><th>AWB Number:</th><td>{shipment.awb_number}</td></tr>" if shipment.awb_number else ""}
                <tr>
                    <th>Est. Delivery:</th>
                    <td>{delivery_date_str}</td>
                </tr>
            </table>
        </div>

        <p>You can follow the progress of your shipment using the tracking number on the courier partner's portal.</p>
        <p>Thank you for choosing Bharath Delight Foods. We hope you enjoy the purity of our responsibly sourced products!</p>
        """

        html_body = self._get_base_template("Order Dispatched", content_html)
        return await self.send_transactional_email(
            to_email=order.customer_snapshot.email,
            to_name=cust_name,
            subject=subject,
            html_content=html_body,
            order_id=order.id
        )

    async def send_shipment_delivered_email(self, order: Order, shipment: Shipment) -> bool:
        """
        Sends delivery confirmation email to customer.
        """
        cust_name = f"{order.customer_snapshot.first_name or ''} {order.customer_snapshot.last_name or ''}".strip()
        if not cust_name:
            cust_name = order.shipping_address_snapshot.full_name

        subject = f"Delivery Confirmed - #{order.order_number}"
        content_html = f"""
        <div class="h2">Delivery Confirmed</div>
        <p>Dear {cust_name},</p>
        <p>Your order <b>#{order.order_number}</b> has been marked as successfully delivered. We hope it reached you in perfect condition.</p>

        <p><b>Verify Batch Authenticity:</b></p>
        <p>For your trust and safety, you can verify your product batch test reports directly in our trust center. Simply enter the batch code printed on the product packaging.</p>

        <p style="text-align: center;">
            <a href="/trust" class="btn">Verify Batch Purity</a>
        </p>

        <p>If you did not receive this delivery or noticed any packaging leaks, please contact our support team immediately so we can assist you.</p>
        """

        html_body = self._get_base_template("Order Delivered", content_html)
        return await self.send_transactional_email(
            to_email=order.customer_snapshot.email,
            to_name=cust_name,
            subject=subject,
            html_content=html_body,
            order_id=order.id
        )

    async def send_contact_inquiry_email(
        self,
        full_name: str,
        customer_email: str,
        phone: str,
        inquiry_type: str,
        message: str,
    ) -> bool:
        """
        Sends a contact inquiry notification email to the admin.
        Triggered when a user submits the 'Send Us a Message' form on the Contact page.
        """
        admin_email = settings.ADMIN_EMAIL or settings.BREVO_SENDER_EMAIL or "bharathdelightfoods@gmail.com"
        subject = f"New Contact Inquiry: {inquiry_type} — from {full_name}"

        content_html = f"""
        <div class="h2">New Customer Inquiry Received</div>
        <p>A new message has been submitted through the <b>Contact Us</b> form on the Bharath Delight Foods storefront.</p>

        <div class="details-box">
            <h4 style="margin-top:0; color:#0F3D2E;">Inquiry Details</h4>
            <table>
                <tr>
                    <th>Name:</th>
                    <td>{full_name}</td>
                </tr>
                <tr>
                    <th>Email:</th>
                    <td><a href="mailto:{customer_email}" style="color:#0F3D2E;">{customer_email}</a></td>
                </tr>
                <tr>
                    <th>Phone:</th>
                    <td>{phone}</td>
                </tr>
                <tr>
                    <th>Inquiry Type:</th>
                    <td><b>{inquiry_type}</b></td>
                </tr>
            </table>
        </div>

        <div class="details-box" style="border-left: 4px solid #C89B3C; background-color: #FFFDF0;">
            <h4 style="margin-top:0; color:#0F3D2E;">Message</h4>
            <p style="margin: 0; font-size: 13px; line-height: 1.7; white-space: pre-wrap;">{message}</p>
        </div>

        <p style="font-size: 12px; color: #6B7280;">
            Reply directly to this email or reach the customer at
            <a href="mailto:{customer_email}" style="color:#0F3D2E;">{customer_email}</a>
            or call <b>{phone}</b>.
        </p>
        """

        html_body = self._get_base_template("New Contact Inquiry", content_html)
        return await self.send_transactional_email(
            to_email=admin_email,
            to_name="Admin — Bharath Delight Foods",
            subject=subject,
            html_content=html_body,
        )


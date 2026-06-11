import os
from datetime import UTC, datetime
from io import BytesIO
from decimal import Decimal

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from app.models.order import Order
from app.models.settings import Settings
from app.repositories.order_repository import OrderRepository
from app.services.audit_service import AuditService


class InvoiceService:
    def __init__(self, order_repository: OrderRepository, audit_service: AuditService):
        self.order_repository = order_repository
        self.audit_service = audit_service

    async def ensure_invoice_metadata(
        self, order: Order, operator_id: str = "system", ip_address: str | None = None
    ) -> tuple[str, datetime]:
        """
        Ensures that the order has an invoice number and generation timestamp.
        If they do not exist, they are generated, persisted in the DB, and audit-logged.
        """
        if order.invoice_number and order.invoice_generated_at:
            return order.invoice_number, order.invoice_generated_at

        # Format: INV-YYYYMMDD-ORDERNUMBER
        date_str = datetime.now(UTC).strftime("%Y%m%d")
        invoice_number = f"INV-{date_str}-{order.order_number}"
        invoice_generated_at = datetime.now(UTC)

        update_payload = {
            "invoice_number": invoice_number,
            "invoice_generated_at": invoice_generated_at,
            "updated_at": datetime.now(UTC),
        }

        # Persist to database
        await self.order_repository.update(order.id, update_payload)

        # Update order in-memory fields
        order.invoice_number = invoice_number
        order.invoice_generated_at = invoice_generated_at

        # Log audit action
        await self.audit_service.log_action(
            action="INVOICE_GENERATED",
            target_collection="orders",
            user_id=operator_id,
            target_id=order.id,
            ip_address=ip_address,
        )

        return invoice_number, invoice_generated_at

    def generate_invoice_pdf(self, order: Order, settings: Settings) -> BytesIO:
        """
        Generates a premium styled A4 invoice PDF in memory and returns the BytesIO buffer.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Define custom styles with safe defaults
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0F3D2E'),  # Deep Forest Green
            spaceAfter=6
        )
        tagline_style = ParagraphStyle(
            'InvoiceTagline',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#C89B3C'),  # Rich Gold
            spaceAfter=15
        )
        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=12,
            textColor=colors.HexColor('#0F3D2E'),
            spaceAfter=4,
            spaceBefore=6
        )
        text_style = ParagraphStyle(
            'InvoiceText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#1C2321')
        )
        text_bold_style = ParagraphStyle(
            'InvoiceTextBold',
            parent=text_style,
            fontName='Helvetica-Bold'
        )
        table_text_style = ParagraphStyle(
            'TableText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#1C2321')
        )
        table_header_style = ParagraphStyle(
            'TableHeaderText',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=12,
            textColor=colors.white
        )

        story = []

        # Header section (Company Name + Tagline & FSSAI/GSTIN metadata)
        story.append(Paragraph(settings.brand_name or "Mr. Bharath Foods", title_style))
        story.append(Paragraph("FOOD DONE RIGHT.", tagline_style))

        # Company Compliance Info
        compliance_lines = []
        if settings.gst_number:
            compliance_lines.append(f"<b>GSTIN:</b> {settings.gst_number}")
        if settings.fssai_number:
            compliance_lines.append(f"<b>FSSAI Lic. No:</b> {settings.fssai_number}")
        if settings.business_address:
            compliance_lines.append(f"<b>Address:</b> {settings.business_address}")
        
        compliance_text = "<br/>".join(compliance_lines)
        story.append(Paragraph(compliance_text, text_style))
        story.append(Spacer(1, 15))

        # Horizontal separator line
        sep_table = Table([[""]], colWidths=[523], rowHeights=[1])
        sep_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#C89B3C')),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(sep_table)
        story.append(Spacer(1, 15))

        # Left/Right Info Grid (Customer Profile & Shipping vs Invoice Metadata)
        cust_name = f"{order.customer_snapshot.first_name or ''} {order.customer_snapshot.last_name or ''}".strip()
        if not cust_name:
            cust_name = order.shipping_address_snapshot.full_name

        cust_info_html = (
            f"<b>Name:</b> {cust_name}<br/>"
            f"<b>Email:</b> {order.customer_snapshot.email}<br/>"
            f"<b>Phone:</b> {order.customer_snapshot.phone or order.shipping_address_snapshot.phone}"
        )

        ship_addr_html = (
            f"{order.shipping_address_snapshot.full_name}<br/>"
            f"{order.shipping_address_snapshot.address_line1}<br/>"
            f"{order.shipping_address_snapshot.address_line2 or ''}<br/>"
            f"{order.shipping_address_snapshot.city}, {order.shipping_address_snapshot.state} - {order.shipping_address_snapshot.pincode}<br/>"
            f"{order.shipping_address_snapshot.country}"
        ).replace("<br/><br/>", "<br/>")

        invoice_date_str = (
            order.invoice_generated_at.strftime("%d-%b-%Y")
            if order.invoice_generated_at else
            datetime.now(UTC).strftime("%d-%b-%Y")
        )

        invoice_meta_html = (
            f"<b>Invoice Number:</b> {order.invoice_number or 'PENDING'}<br/>"
            f"<b>Invoice Date:</b> {invoice_date_str}<br/>"
            f"<b>Order Number:</b> #{order.order_number}<br/>"
            f"<b>Payment Status:</b> <font color='#2E7D32'><b>PAID</b></font>"
        )

        left_col = [
            Paragraph("CUSTOMER INFORMATION", section_heading),
            Paragraph(cust_info_html, text_style),
            Spacer(1, 10),
            Paragraph("SHIPPING ADDRESS", section_heading),
            Paragraph(ship_addr_html, text_style)
        ]

        right_col = [
            Paragraph("INVOICE METADATA", section_heading),
            Paragraph(invoice_meta_html, text_style)
        ]

        grid_table = Table([[left_col, right_col]], colWidths=[270, 253])
        grid_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(grid_table)
        story.append(Spacer(1, 20))

        # Items Table
        table_data = [
            [
                Paragraph("SKU", table_header_style),
                Paragraph("Product Details", table_header_style),
                Paragraph("Qty", table_header_style),
                Paragraph("Unit Price", table_header_style),
                Paragraph("Total", table_header_style)
            ]
        ]

        # Populate rows
        for item in order.items:
            table_data.append([
                Paragraph(item.sku, table_text_style),
                Paragraph(f"{item.product_name} ({item.variant_title})", table_text_style),
                Paragraph(str(item.quantity), table_text_style),
                Paragraph(f"INR {item.unit_price:,.2f}", table_text_style),
                Paragraph(f"INR {item.line_total:,.2f}", table_text_style)
            ])

        items_table = Table(table_data, colWidths=[90, 210, 40, 93, 90])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F3D2E')),
            ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 15))

        # Totals calculation display
        subtotal_str = f"INR {order.pricing.subtotal:,.2f}"
        tax_str = f"INR {order.pricing.tax_total:,.2f}"
        shipping_str = "FREE" if order.pricing.shipping_fee == Decimal('0.00') else f"INR {order.pricing.shipping_fee:,.2f}"
        grand_total_str = f"INR {order.pricing.grand_total:,.2f}"

        totals_data = [
            [Paragraph("Subtotal", text_style), Paragraph(subtotal_str, text_style)],
            [Paragraph("GST (5%)", text_style), Paragraph(tax_str, text_style)],
            [Paragraph("Shipping Fee", text_style), Paragraph(shipping_str, text_style)],
            [Paragraph("<b>Grand Total</b>", text_bold_style), Paragraph(f"<b>{grand_total_str}</b>", text_bold_style)]
        ]

        totals_table = Table(totals_data, colWidths=[110, 100])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('LINEBELOW', (0,2), (1,2), 0.5, colors.HexColor('#E5E7EB')),
        ]))

        # Wrap totals in a table grid to push to the right
        totals_container = Table([["", totals_table]], colWidths=[313, 210])
        totals_container.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(totals_container)
        story.append(Spacer(1, 30))

        # Footer Seal & Message
        footer_style = ParagraphStyle(
            'InvoiceFooter',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#6B7280'),
            alignment=1  # Centered
        )
        story.append(Paragraph(
            "Thank you for shopping with Mr. Bharath Foods. Sourced responsibly.<br/>"
            "This is a computer-generated document. No signature is required.",
            footer_style
        ))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

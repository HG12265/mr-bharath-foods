from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.order import Order


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to calculate total page count and draw clean professional footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6B7280"))
        
        # Footer text: Left brand note, Right page numbering
        self.drawString(36, 20, "Bharath Delight Foods • Administrative Operations Report • Strictly Confidential")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(842 - 36, 20, page_str)
        
        # Thin footer rule
        self.setStrokeColor(colors.HexColor("#E5E7EB"))
        self.setLineWidth(0.5)
        self.line(36, 32, 842 - 36, 32)
        
        self.restoreState()


class ReportService:
    """
    Service for generating executive Orders & Sales reports in PDF and Excel (.xlsx) formats.
    """

    @staticmethod
    def filter_orders(
        orders: list[Order],
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Order]:
        """
        Filters orders based on status (pending, delivered, paid, etc.) and date range.
        """
        filtered = orders

        if status and status.lower() != "all":
            s = status.strip().lower()
            if s == "pending":
                filtered = [
                    o for o in filtered
                    if o.order_status == "pending_payment" or o.fulfillment_status == "pending" or o.payment_status == "pending"
                ]
            elif s == "pending_payment":
                filtered = [o for o in filtered if o.order_status == "pending_payment"]
            elif s == "paid":
                filtered = [o for o in filtered if o.payment_status == "paid"]
            elif s == "confirmed":
                filtered = [o for o in filtered if o.order_status == "confirmed"]
            elif s == "delivered":
                filtered = [o for o in filtered if o.fulfillment_status == "delivered"]
            elif s == "shipped":
                filtered = [o for o in filtered if o.fulfillment_status == "shipped"]
            elif s == "packed":
                filtered = [o for o in filtered if o.fulfillment_status == "packed"]
            elif s == "cancelled":
                filtered = [
                    o for o in filtered
                    if o.order_status == "cancelled" or o.fulfillment_status == "cancelled"
                ]
            else:
                filtered = [
                    o for o in filtered
                    if o.order_status == s or o.fulfillment_status == s or o.payment_status == s
                ]

        if start_date:
            filtered = [o for o in filtered if o.created_at >= start_date]

        if end_date:
            filtered = [o for o in filtered if o.created_at <= end_date]

        return filtered

    @staticmethod
    def generate_excel_report(
        orders: list[Order],
        filter_label: str = "All Orders",
        brand_name: str = "Bharath Delight Foods",
    ) -> BytesIO:
        """
        Generates a styled, executive Excel (.xlsx) report using openpyxl.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Orders Report"
        ws.views.sheetView[0].showGridLines = True

        # Styles
        forest_dark = "0F3D2E"
        gold_accent = "C89B3C"
        cream_bg = "FAF9F6"
        zebra_bg = "F4F6F4"
        border_color = "D1D5DB"

        title_font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
        title_fill = PatternFill(start_color=forest_dark, end_color=forest_dark, fill_type="solid")

        meta_font = Font(name="Calibri", size=10, italic=True, color="1C2321")
        meta_fill = PatternFill(start_color=cream_bg, end_color=cream_bg, fill_type="solid")

        header_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color=forest_dark, end_color=forest_dark, fill_type="solid")

        kpi_label_font = Font(name="Calibri", size=9, bold=True, color="6B7280")
        kpi_val_font = Font(name="Calibri", size=12, bold=True, color="0F3D2E")
        kpi_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

        data_font = Font(name="Calibri", size=9, color="1C2321")
        total_font = Font(name="Calibri", size=10, bold=True, color="0F3D2E")
        total_fill = PatternFill(start_color="E8EFEA", end_color="E8EFEA", fill_type="solid")

        thin_side = Side(style="thin", color=border_color)
        grid_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
        double_bottom = Border(
            left=thin_side, right=thin_side, top=thin_side,
            bottom=Side(style="double", color=forest_dark)
        )

        align_center = Alignment(horizontal="center", vertical="center")
        align_left = Alignment(horizontal="left", vertical="center")
        align_right = Alignment(horizontal="right", vertical="center")

        # 1. Main Banner (Row 1)
        ws.merge_cells("A1:N1")
        banner_cell = ws["A1"]
        banner_cell.value = f"{brand_name.upper()} — ORDERS & SALES OPERATIONS REPORT"
        banner_cell.font = title_font
        banner_cell.fill = title_fill
        banner_cell.alignment = align_center
        ws.row_dimensions[1].height = 40

        # 2. Metadata Subtitle (Row 2)
        total_revenue = sum((o.pricing.grand_total for o in orders), Decimal("0.00"))
        now_str = datetime.now(UTC).strftime("%d-%b-%Y %I:%M %p UTC")
        
        ws.merge_cells("A2:N2")
        meta_cell = ws["A2"]
        meta_cell.value = (
            f"Generated: {now_str}  |  Filter: {filter_label}  |  "
            f"Total Orders: {len(orders)}  |  Total Revenue: INR {total_revenue:,.2f}"
        )
        meta_cell.font = meta_font
        meta_cell.fill = meta_fill
        meta_cell.alignment = align_center
        ws.row_dimensions[2].height = 24

        # 3. KPI Summary Cards (Row 4)
        paid_orders = [o for o in orders if o.payment_status == "paid"]
        delivered_orders = [o for o in orders if o.fulfillment_status == "delivered"]
        pending_orders = [o for o in orders if o.order_status == "pending_payment" or o.payment_status == "pending"]

        kpi_metrics = [
            ("TOTAL ORDERS", len(orders), "A", "C"),
            ("TOTAL REVENUE", f"INR {total_revenue:,.2f}", "D", "F"),
            ("PAID ORDERS", f"{len(paid_orders)} orders", "G", "I"),
            ("DELIVERED ORDERS", f"{len(delivered_orders)} orders", "J", "L"),
            ("PENDING ORDERS", f"{len(pending_orders)} orders", "M", "N"),
        ]

        for label, val, start_col, end_col in kpi_metrics:
            # Row 4 Label
            ws.merge_cells(f"{start_col}4:{end_col}4")
            c_label = ws[f"{start_col}4"]
            c_label.value = label
            c_label.font = kpi_label_font
            c_label.fill = meta_fill
            c_label.alignment = align_center
            
            # Row 5 Value
            ws.merge_cells(f"{start_col}5:{end_col}5")
            c_val = ws[f"{start_col}5"]
            c_val.value = val
            c_val.font = kpi_val_font
            c_val.fill = kpi_fill
            c_val.alignment = align_center
            
            # Borders for KPI boxes
            for col_idx in range(openpyxl.utils.column_index_from_string(start_col), openpyxl.utils.column_index_from_string(end_col) + 1):
                col_letter = get_column_letter(col_idx)
                ws[f"{col_letter}4"].border = grid_border
                ws[f"{col_letter}5"].border = grid_border

        ws.row_dimensions[4].height = 18
        ws.row_dimensions[5].height = 24

        # 4. Table Column Headers (Row 7)
        headers = [
            ("Order #", 16, align_left),
            ("Date & Time", 18, align_center),
            ("Customer Name", 22, align_left),
            ("Customer Email", 26, align_left),
            ("Phone", 15, align_center),
            ("Delivery City", 16, align_left),
            ("State", 16, align_left),
            ("Items Summary", 32, align_left),
            ("Order Status", 16, align_center),
            ("Fulfillment", 15, align_center),
            ("Payment", 15, align_center),
            ("Subtotal", 14, align_right),
            ("Tax (GST)", 12, align_right),
            ("Grand Total", 16, align_right),
        ]

        header_row = 7
        ws.row_dimensions[header_row].height = 28

        for col_idx, (col_name, col_width, alignment) in enumerate(headers, start=1):
            cell = ws.cell(row=header_row, column=col_idx)
            cell.value = col_name
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = align_center
            cell.border = grid_border
            ws.column_dimensions[get_column_letter(col_idx)].width = col_width

        # 5. Populate Data Rows
        current_row = header_row + 1
        for idx, order in enumerate(orders):
            date_str = order.created_at.strftime("%d-%b-%Y %I:%M %p")
            cust_name = f"{order.customer_snapshot.first_name or ''} {order.customer_snapshot.last_name or ''}".strip()
            if not cust_name:
                cust_name = order.shipping_address_snapshot.full_name or "Guest"

            phone = order.customer_snapshot.phone or order.shipping_address_snapshot.phone or "-"
            city = order.shipping_address_snapshot.city or "-"
            state = order.shipping_address_snapshot.state or "-"

            # Items summary: e.g. "Pure Cow Ghee (500ml) x 2, Buffalo Ghee x 1"
            items_str = ", ".join(f"{it.product_name} x {it.quantity}" for it in order.items)
            if len(items_str) > 120:
                items_str = items_str[:117] + "..."

            row_fill = PatternFill(
                start_color=zebra_bg if idx % 2 == 1 else "FFFFFF",
                end_color=zebra_bg if idx % 2 == 1 else "FFFFFF",
                fill_type="solid"
            )

            row_data = [
                (order.order_number, align_left, "@"),
                (date_str, align_center, None),
                (cust_name, align_left, None),
                (order.customer_snapshot.email, align_left, None),
                (phone, align_center, None),
                (city, align_left, None),
                (state, align_left, None),
                (items_str, align_left, None),
                (order.order_status.replace("_", " ").upper(), align_center, None),
                (order.fulfillment_status.replace("_", " ").upper(), align_center, None),
                (order.payment_status.upper(), align_center, None),
                (float(order.pricing.subtotal), align_right, "₹#,##0.00"),
                (float(order.pricing.tax_total), align_right, "₹#,##0.00"),
                (float(order.pricing.grand_total), align_right, "₹#,##0.00"),
            ]

            ws.row_dimensions[current_row].height = 20
            for col_idx, (val, alignment, num_fmt) in enumerate(row_data, start=1):
                cell = ws.cell(row=current_row, column=col_idx)
                cell.value = val
                cell.font = data_font
                cell.fill = row_fill
                cell.alignment = alignment
                cell.border = grid_border
                if num_fmt:
                    cell.number_format = num_fmt

            current_row += 1

        # 6. Summary Total Row
        ws.row_dimensions[current_row].height = 26
        ws.merge_cells(f"A{current_row}:K{current_row}")
        total_label_cell = ws[f"A{current_row}"]
        total_label_cell.value = f"TOTAL ({len(orders)} ORDERS)"
        total_label_cell.font = total_font
        total_label_cell.fill = total_fill
        total_label_cell.alignment = align_right

        # Borders for merged label cells
        for c in range(1, 12):
            ws.cell(row=current_row, column=c).border = double_bottom
            ws.cell(row=current_row, column=c).fill = total_fill

        # Total Subtotal, Tax, and Grand Total
        subtotal_sum = sum((float(o.pricing.subtotal) for o in orders), 0.0)
        tax_sum = sum((float(o.pricing.tax_total) for o in orders), 0.0)
        grand_total_sum = sum((float(o.pricing.grand_total) for o in orders), 0.0)

        for col_idx, sum_val in [(12, subtotal_sum), (13, tax_sum), (14, grand_total_sum)]:
            c_sum = ws.cell(row=current_row, column=col_idx)
            c_sum.value = sum_val
            c_sum.font = total_font
            c_sum.fill = total_fill
            c_sum.alignment = align_right
            c_sum.border = double_bottom
            c_sum.number_format = "₹#,##0.00"

        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf

    @staticmethod
    def generate_pdf_report(
        orders: list[Order],
        filter_label: str = "All Orders",
        brand_name: str = "Bharath Delight Foods",
    ) -> BytesIO:
        """
        Generates a styled, executive landscape A4 PDF report with ReportLab.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=42,
        )

        styles = getSampleStyleSheet()

        # Styles
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0F3D2E"),
            spaceAfter=3,
        )

        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=colors.HexColor("#C89B3C"),
            spaceAfter=10,
        )

        meta_style = ParagraphStyle(
            "ReportMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#4B5563"),
        )

        th_style = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.white,
            alignment=1,  # Center
        )

        td_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1F2937"),
        )

        td_bold_style = ParagraphStyle(
            "TableCellBold",
            parent=td_style,
            fontName="Helvetica-Bold",
        )

        td_center = ParagraphStyle(
            "TableCellCenter",
            parent=td_style,
            alignment=1,
        )

        td_right = ParagraphStyle(
            "TableCellRight",
            parent=td_style,
            alignment=2,
        )

        story = []

        # 1. Header Banner
        now_str = datetime.now(UTC).strftime("%d-%b-%Y %I:%M %p UTC")
        total_revenue = sum((o.pricing.grand_total for o in orders), Decimal("0.00"))

        header_table = Table([
            [
                Paragraph(brand_name.upper(), title_style),
                Paragraph(f"<b>Filter:</b> {filter_label}<br/><b>Generated:</b> {now_str}", meta_style)
            ],
            [
                Paragraph("EXECUTIVE ORDERS & SALES OPERATIONS REPORT", subtitle_style),
                Paragraph(f"<b>Total Count:</b> {len(orders)} Orders &nbsp;|&nbsp; <b>Total Volume:</b> INR {total_revenue:,.2f}", meta_style)
            ]
        ], colWidths=[520, 250])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))

        # 2. Gold Accent Separator Line
        sep_table = Table([[""]], colWidths=[770], rowHeights=[2])
        sep_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#C89B3C')),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(sep_table)
        story.append(Spacer(1, 12))

        # 3. KPI Mini Summary Cards
        paid_count = len([o for o in orders if o.payment_status == "paid"])
        delivered_count = len([o for o in orders if o.fulfillment_status == "delivered"])
        pending_count = len([o for o in orders if o.order_status == "pending_payment" or o.payment_status == "pending"])

        kpi_cells = [
            [
                Paragraph("<font color='#6B7280' size='7'>TOTAL ORDERS</font><br/><b><font color='#0F3D2E' size='11'>" + str(len(orders)) + "</font></b>", td_center),
                Paragraph("<font color='#6B7280' size='7'>TOTAL REVENUE</font><br/><b><font color='#0F3D2E' size='11'>INR " + f"{total_revenue:,.2f}" + "</font></b>", td_center),
                Paragraph("<font color='#6B7280' size='7'>PAID ORDERS</font><br/><b><font color='#2E7D32' size='11'>" + str(paid_count) + "</font></b>", td_center),
                Paragraph("<font color='#6B7280' size='7'>DELIVERED</font><br/><b><font color='#0F3D2E' size='11'>" + str(delivered_count) + "</font></b>", td_center),
                Paragraph("<font color='#6B7280' size='7'>PENDING</font><br/><b><font color='#C89B3C' size='11'>" + str(pending_count) + "</font></b>", td_center),
            ]
        ]
        kpi_table = Table(kpi_cells, colWidths=[154, 154, 154, 154, 154])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAF9')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 14))

        # 4. Orders Data Table
        # Columns: [Order # (85), Date (75), Customer (130), Phone/City (110), Items (110), Order St (80), Fulfill (80), Grand Total (100)] -> Total = 770 pt
        table_data = [
            [
                Paragraph("Order #", th_style),
                Paragraph("Date", th_style),
                Paragraph("Customer", th_style),
                Paragraph("Phone & Location", th_style),
                Paragraph("Items Summary", th_style),
                Paragraph("Order Status", th_style),
                Paragraph("Payment", th_style),
                Paragraph("Grand Total", th_style),
            ]
        ]

        for order in orders:
            d_str = order.created_at.strftime("%d-%b-%Y")
            c_name = f"{order.customer_snapshot.first_name or ''} {order.customer_snapshot.last_name or ''}".strip()
            if not c_name:
                c_name = order.shipping_address_snapshot.full_name or "Guest"

            phone = order.customer_snapshot.phone or order.shipping_address_snapshot.phone or "-"
            loc = f"{order.shipping_address_snapshot.city or ''}, {order.shipping_address_snapshot.state or ''}".strip(", ")
            phone_loc = f"{phone}<br/><font color='#6B7280' size='7'>{loc}</font>"

            # Format items briefly
            items_brief = ", ".join(f"{it.product_name} x {it.quantity}" for it in order.items)
            if len(items_brief) > 50:
                items_brief = items_brief[:47] + "..."

            order_st_color = (
                "#2E7D32" if order.order_status == "confirmed"
                else "#C89B3C" if order.order_status == "pending_payment"
                else "#DC2626"
            )
            pay_st_color = "#2E7D32" if order.payment_status == "paid" else "#DC2626" if order.payment_status == "failed" else "#C89B3C"

            order_st_html = f"<font color='{order_st_color}'><b>{order.order_status.replace('_', ' ').upper()}</b></font>"
            pay_st_html = f"<font color='{pay_st_color}'><b>{order.payment_status.upper()}</b></font>"

            table_data.append([
                Paragraph(f"<b>{order.order_number}</b>", td_style),
                Paragraph(d_str, td_center),
                Paragraph(f"<b>{c_name}</b><br/><font color='#6B7280' size='7'>{order.customer_snapshot.email}</font>", td_style),
                Paragraph(phone_loc, td_style),
                Paragraph(items_brief, td_style),
                Paragraph(order_st_html, td_center),
                Paragraph(pay_st_html, td_center),
                Paragraph(f"<b>INR {order.pricing.grand_total:,.2f}</b>", td_right),
            ])

        # Summary Row
        table_data.append([
            Paragraph("<b>TOTAL</b>", td_style),
            Paragraph(f"<b>{len(orders)} Orders</b>", td_center),
            Paragraph("", td_style),
            Paragraph("", td_style),
            Paragraph("", td_style),
            Paragraph("", td_style),
            Paragraph("", td_style),
            Paragraph(f"<b>INR {total_revenue:,.2f}</b>", td_right),
        ])

        orders_table = Table(
            table_data,
            colWidths=[80, 65, 140, 115, 120, 80, 75, 95],
            repeatRows=1,
        )

        table_styles = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F3D2E')),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#E5E7EB')),
            # Summary row styling
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E8EFEA')),
            ('LINEABOVE', (0,-1), (-1,-1), 1, colors.HexColor('#0F3D2E')),
            ('LINEBELOW', (0,-1), (-1,-1), 1.5, colors.HexColor('#0F3D2E')),
        ]

        # Zebra striping for data rows
        for i in range(1, len(orders) + 1):
            if i % 2 == 0:
                table_styles.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FAF9F6')))

        orders_table.setStyle(TableStyle(table_styles))
        story.append(orders_table)

        doc.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer


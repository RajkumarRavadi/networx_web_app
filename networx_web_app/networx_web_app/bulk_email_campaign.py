# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import time
from io import BytesIO

import frappe
from frappe import _
from frappe.utils import validate_email_address

try:
	import openpyxl
except ImportError:
	openpyxl = None  # type: ignore

MAX_RECIPIENTS = 100
MAX_SUBJECT_LEN = 200
MAX_MESSAGE_LEN = 500_000
MAX_DELAY_SECONDS = 120
MAX_BATCH_PAUSE_SECONDS = 600
MIN_BATCH_SIZE = 1
MAX_BATCH_SIZE = 500


def _can_use_bulk_email_tool():
	if frappe.session.user == "Guest":
		return False
	return "System Manager" in frappe.get_roles()


def parse_xlsx_upload(file_storage) -> dict:
	"""Parse first sheet of an .xlsx upload. Expects Name and Email columns (case-insensitive)."""
	if openpyxl is None:
		return {"error": _("openpyxl is not installed. Run bench setup requirements."), "contacts": []}

	if not file_storage or not file_storage.filename:
		return {"error": _("No file uploaded."), "contacts": []}

	filename = (file_storage.filename or "").lower()
	if not filename.endswith(".xlsx"):
		return {"error": _("Only .xlsx files are supported."), "contacts": []}

	skipped_invalid = 0
	skipped_empty = 0
	wb = None

	try:
		raw = file_storage.read()
		wb = openpyxl.load_workbook(BytesIO(raw), read_only=True, data_only=True)
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Bulk email: xlsx parse")
		return {"error": _("Could not read Excel file: {0}").format(str(e)), "contacts": []}

	try:
		sheet = wb.active
		rows = sheet.iter_rows(values_only=True)
		header_row = next(rows, None)
		if not header_row:
			return {"error": _("The spreadsheet is empty."), "contacts": []}

		name_idx = None
		email_idx = None
		for i, cell in enumerate(header_row):
			label = _normalize_header_cell(cell)
			if label == "name":
				name_idx = i
			elif label == "email":
				email_idx = i

		if name_idx is None or email_idx is None:
			return {
				"error": _("The first row must include columns named Name and Email."),
				"contacts": [],
			}

		contacts = []

		for row in rows:
			if row is None:
				continue
			name_val = _cell_str(row, name_idx)
			email_val = _cell_str(row, email_idx)
			if not email_val and not name_val:
				skipped_empty += 1
				continue
			if not email_val:
				skipped_invalid += 1
				continue
			email_val = email_val.strip()
			if not validate_email_address(email_val, throw=False):
				skipped_invalid += 1
				continue
			contacts.append({"name": name_val or "", "email": email_val})

	finally:
		if wb is not None:
			wb.close()

	if len(contacts) > MAX_RECIPIENTS:
		return {
			"error": _("More than {0} valid recipients. Reduce rows and try again.").format(MAX_RECIPIENTS),
			"contacts": [],
			"skipped_invalid": skipped_invalid,
			"skipped_empty": skipped_empty,
		}

	return {
		"contacts": contacts,
		"skipped_invalid": skipped_invalid,
		"skipped_empty": skipped_empty,
		"error": None,
	}


def _normalize_header_cell(cell) -> str:
	if cell is None:
		return ""
	return str(cell).strip().lower()


def _cell_str(row: tuple, idx: int) -> str:
	if idx >= len(row) or row[idx] is None:
		return ""
	return str(row[idx]).strip()


def _personalize(template: str, name: str, email: str) -> str:
	if not template:
		return ""
	out = template.replace("{{name}}", name or "")
	out = out.replace("{{email}}", email or "")
	return out


def _coerce_int(value, default: int, min_v: int, max_v: int) -> int:
	try:
		n = int(value)
	except (TypeError, ValueError):
		return default
	return max(min_v, min(max_v, n))


@frappe.whitelist(methods=["POST"])
def start_bulk_email_campaign():
	"""Accept multipart form: file (.xlsx), subject, message, delay_seconds, batch_size, batch_pause_seconds, send_as_html."""
	if not _can_use_bulk_email_tool():
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	files = frappe.request.files
	upload = files.get("file")
	if not upload:
		frappe.throw(_("Attach an .xlsx file with field name file."))

	parsed = parse_xlsx_upload(upload)
	if parsed.get("error"):
		frappe.throw(parsed["error"])

	contacts = parsed["contacts"]
	if not contacts:
		frappe.throw(_("No valid email rows found. Check Name and Email columns."))

	subject = (frappe.form_dict.get("subject") or "").strip()
	message = frappe.form_dict.get("message") or ""

	if not subject:
		frappe.throw(_("Subject is required."))
	if not message.strip():
		frappe.throw(_("Message is required."))

	if len(subject) > MAX_SUBJECT_LEN:
		frappe.throw(_("Subject is too long."))
	if len(message) > MAX_MESSAGE_LEN:
		frappe.throw(_("Message is too long."))

	delay_seconds = _coerce_int(frappe.form_dict.get("delay_seconds"), default=2, min_v=0, max_v=MAX_DELAY_SECONDS)
	batch_size = _coerce_int(frappe.form_dict.get("batch_size"), default=20, min_v=MIN_BATCH_SIZE, max_v=MAX_BATCH_SIZE)
	batch_pause_seconds = _coerce_int(
		frappe.form_dict.get("batch_pause_seconds"),
		default=60,
		min_v=0,
		max_v=MAX_BATCH_PAUSE_SECONDS,
	)
	send_as_html = frappe.form_dict.get("send_as_html") in ("1", "true", "True", True, "on")

	frappe.enqueue(
		"networx_web_app.networx_web_app.bulk_email_campaign.send_bulk_email_job",
		queue="long",
		contacts=contacts,
		subject_template=subject,
		message_template=message,
		delay_seconds=delay_seconds,
		batch_size=batch_size,
		batch_pause_seconds=batch_pause_seconds,
		send_as_html=send_as_html,
		enqueue_after_commit=True,
	)

	return {
		"queued": True,
		"recipient_count": len(contacts),
		"skipped_invalid": parsed.get("skipped_invalid", 0),
		"skipped_empty": parsed.get("skipped_empty", 0),
		"message": _("Bulk send job queued. Ensure a bench worker is processing the long queue."),
	}


def send_bulk_email_job(
	contacts,
	subject_template: str,
	message_template: str,
	delay_seconds: int = 2,
	batch_size: int = 20,
	batch_pause_seconds: int = 60,
	send_as_html: bool = False,
):
	"""Worker: send one email per contact with throttling. Log failures; no custom DocTypes."""
	sent = 0
	failed = 0
	since_batch_sleep = 0

	for contact in contacts:
		email = contact.get("email")
		name = contact.get("name") or ""
		if not email:
			failed += 1
			continue

		subject = _personalize(subject_template, name, email)
		body = _personalize(message_template, name, email)

		try:
			frappe.sendmail(
				recipients=[email],
				subject=subject,
				message=body,
				now=True,
				add_unsubscribe_link=0,
				with_container=bool(send_as_html),
			)
			sent += 1
		except Exception as e:
			failed += 1
			frappe.log_error(
				message=f"{email}: {frappe.get_traceback()}",
				title=f"Bulk email send failed: {email}",
			)

		since_batch_sleep += 1
		if batch_size > 0 and since_batch_sleep >= batch_size and batch_pause_seconds > 0:
			time.sleep(batch_pause_seconds)
			since_batch_sleep = 0

		if delay_seconds > 0:
			time.sleep(delay_seconds)

	frappe.logger().info(f"bulk_email_campaign job finished: sent={sent}, failed={failed}")

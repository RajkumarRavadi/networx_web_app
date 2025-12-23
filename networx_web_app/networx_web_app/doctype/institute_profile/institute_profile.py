import frappe
from frappe.model.document import Document


class InstituteProfile(Document):
    def before_save(self):
        # Copy name to institute_id if not set
        if not self.institute_id:
            self.institute_id = self.name


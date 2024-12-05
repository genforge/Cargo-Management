# Copyright (c) 2024, Osama and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FPLCrossStuffJob(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		assigned_at: DF.Datetime | None
		client: DF.Link | None
		container_number: DF.Data | None
		cross_stuff_performance_location: DF.Link | None
		freight_order_id: DF.Data | None
		job_type: DF.Link | None
		performance_details: DF.Link | None
		sales_order_number: DF.Data | None
		status: DF.Literal["", "Draft", "Assigned", "Completed", "Cancelled"]
	# end: auto-generated types
	pass

	def validate(self):
			if self.performance_details:
				self.status = "Completed"
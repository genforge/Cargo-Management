# Copyright (c) 2024, Osama and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import frappe
from frappe.utils import getdate, random_string

from cargo_management.cargo_management.utils.getJobTypebyID import get_job_type_by_id


class ContainerorVehicleRequest(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from cargo_management.cargo_management.doctype.container_or_vehicle_request_cdt.container_or_vehicle_request_cdt import ContainerorVehicleRequestcdt
        from frappe.types import DF

        amended_from: DF.Link | None
        booking_order_id: DF.Link | None
        cargo_type: DF.Literal["", "Containerised", "Non Containerised"]
        cross_stuff_performance: DF.Link | None
        request_date: DF.Datetime | None
        table_ktch: DF.Table[ContainerorVehicleRequestcdt]
        yard_location: DF.Link
    # end: auto-generated types

    def on_submit(self):
        try:
            self.create_CrossStuffFreight_orders()  # Create freight orders first
            # self.create_and_submit_sales_order()  # Attempt to create and submit Sales Order
        except Exception as e:
            frappe.db.rollback()  # Roll back changes if any error occurs
            frappe.throw(f"Booking Order submission failed due to: {str(e)}")

    def create_CrossStuffFreight_orders(self):
        Request = self.get('table_ktch')

        for item in Request:
            for _ in range(int(item.qty)):
                self.create_CFO(item)

    def create_CFO(self, item):
        size = item.size if item.size else None
        freight_order = frappe.get_doc({
            'doctype': 'FPL Freight Orders',
            'freight_order_number':  self.get_next_name("CFO-"),
            'sales_order_number': self.booking_order_id,
            'client': self.get_Client_from_BO(),
            'weight': None,
            'size': size,
            'jobs': []
        })

        # Determine transport type based on cargo type
        transport_type = "Rail (Train)" if self.cargo_type == "Containerised" else "Road (Truck)"

        # Add jobs to the freight order
        freight_order.append('jobs', {
            'job_name': self.get_service_type_name('Empty Pickup', transport_type),
            'status': 'Draft',
            'start_location': item.pickup_location,
            'end_location': self.yard_location
        })
        freight_order.append('jobs', {
            'job_name': self.get_service_type_name('Gate In', transport_type),
            'status': 'Draft',
            'start_location': self.yard_location,
            'end_location': self.yard_location
        })
        freight_order.append('jobs', {
            'job_name': self.get_service_type_name('Gate Out', transport_type),
            'status': 'Draft',
            'start_location': self.yard_location,
            'end_location': self.yard_location
        })

        freight_order.insert()

        if freight_order.jobs:
            freight_order.next_job = get_job_type_by_id(freight_order.jobs[0].job_id)
            freight_order.save()

        frappe.db.commit()

    def get_service_type_name(self, service_name, transport_mode):
        if service_name in ['Gate In', 'Gate Out']:
            service_type = frappe.get_value(
                "Service Type",
                {"name1": service_name},
                "name"
            )
        else:
            service_type = frappe.get_value(
                "Service Type",
                {"name1": service_name, "transport_mode": transport_mode},
                "name"
            )
        
        if service_type:
            return service_type
        else:
            frappe.throw(
                f"No Service Type found for name1: {service_name} and transport mode: {transport_mode}"
            )

    def get_Client_from_BO(self):
        """
        Fetches the client from the Booking Order associated with the current document's booking_order_id.
        """
        # Fetch the Booking Order document using the booking_order_id
        booking_order = frappe.get_doc("Booking Order", self.booking_order_id)
        # Return the client field from the Booking Order
        return booking_order.customer

    def get_next_name(self, key):
        try:
            current = frappe.get_last_doc('FPL Freight Orders')
            if current:
                name_parts = current.name.split('-')
                if name_parts:
                    next_number = int(name_parts[-1]) + 1
                    new_name = f"{key}{next_number:04d}"  # Pad with zeros if needed
                    return new_name
        except frappe.DoesNotExistError:
            return f"{key}0001"
        return f"{key}0001"
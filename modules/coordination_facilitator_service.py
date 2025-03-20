from .business_objective import BusinessObjective

class CoordinationFacilitatorService(BusinessObjective):
    def __init__(self, name, installations):
        super().__init__(name)
        self.installations = installations  # List of scheduled installations

    def schedule_installation(self, customer_id, partner_id, time_slot):
        """Schedule an installation with the given details."""
        installation = {
            'customer_id': customer_id,
            'partner_id': partner_id,
            'time_slot': time_slot
        }
        self.installations.append(installation)  # Store the scheduled installation
        print(f"Scheduled installation for customer {customer_id} with partner {partner_id} at {time_slot}")

    def reschedule(self, installation_id, new_time_slot):
        """Adjust an installation's time slot if needed."""
        pass  # Implement rescheduling logic

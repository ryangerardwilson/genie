from .business_objective import BusinessObjective

class CustomerInformerService(BusinessObjective):
    def __init__(self, name):
        super().__init__(name)

    def notify_customer(self, customer_id, message):
        """Send an update to the customer via App, WhatsApp, SMS, etc."""
        print(f"Notifying customer {customer_id}: {message}")

    def provide_tracking(self, customer_id):
        """Offer real-time installation tracking."""
        pass  # Implement tracking logic

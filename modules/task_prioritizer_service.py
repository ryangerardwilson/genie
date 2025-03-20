from .business_objective import BusinessObjective

class TaskPrioritizerService(BusinessObjective):
    def __init__(self, name, partner_tasks):
        super().__init__(name)
        self.partner_tasks = partner_tasks  # Dictionary of partner ID to task list

    # Properties
    prioritized_tasks = {}  # Store prioritized task lists per partner

    # Methods
    def prioritize_for_partner(self, partner_id):
        """Sort tasks for a partner based on urgency and importance."""
        tasks = self.partner_tasks.get(partner_id, [])
        self.prioritized_tasks[partner_id] = sorted(tasks, key=self.priority_score)
        return self.prioritized_tasks[partner_id]

    def priority_score(self, task):
        """Calculate task priority (e.g., deadline, customer impact)."""
        pass  # Implement scoring logic

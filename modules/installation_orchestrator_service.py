from .right_partner_identifier_service import RightPartnerIdentifierService
from .area_viability_assessor_service import AreaViabilityAssessorService
from .optimal_time_finder_service import OptimalTimeFinderService
from .expansion_trigger_service import ExpansionTriggerService
from .risk_preventer_service import RiskPreventerService
from .task_prioritizer_service import TaskPrioritizerService
from .customer_informer_service import CustomerInformerService
from .coordination_facilitator_service import CoordinationFacilitatorService
from .intervention_activator_service import InterventionActivatorService
from .partner_performance_optimizer_service import PartnerPerformanceOptimizerService

class InstallationOrchestratorService:
    def __init__(self):
        # Sample partner data
        sample_partners = [
            {'id': 1, 'location': 'loc1', 'capability': 0.9, 'intent': 0.8},
            {'id': 2, 'location': 'loc2', 'capability': 0.7, 'intent': 0.6},
        ]
        self.right_partner_service = RightPartnerIdentifierService("Identify Right Partner", sample_partners, None)
        self.area_viability_service = AreaViabilityAssessorService("Assess Area Viability", None)
        self.time_finder_service = OptimalTimeFinderService("Find Optimal Time", None)
        self.expansion_service = ExpansionTriggerService("Trigger Expansion", [], [])
        self.risk_preventer_service = RiskPreventerService("Prevent Risks", [])
        self.task_prioritizer_service = TaskPrioritizerService("Prioritize Tasks", {})
        self.customer_informer_service = CustomerInformerService("Inform Customers")
        self.coordinator_service = CoordinationFacilitatorService("Coordinate Schedules", [])
        self.intervention_service = InterventionActivatorService("Activate Interventions", [])
        self.partner_optimizer_service = PartnerPerformanceOptimizerService("Optimize Partners", sample_partners)

    def process_new_customer(self, customer_data):
        """Handle a new customer request from start to finish."""
        viability = self.area_viability_service.assess_viability(customer_data['location'], {})
        if viability > 0.5:  # Example threshold
            partner_id = self.right_partner_service.identify_best_partner(customer_data['location'], customer_data['preferences'])
            time_slot = self.time_finder_service.find_best_slot({}, customer_data['preferences'])
            self.coordinator_service.schedule_installation(customer_data['id'], partner_id, time_slot)
            self.customer_informer_service.notify_customer(customer_data['id'], "Installation scheduled")
            # Add to installations and monitor

    def monitor_installations(self):
        """Continuously monitor and manage ongoing installations."""
        self.risk_preventer_service.detect_risks()
        self.intervention_service.check_for_intervention()
        self.task_prioritizer_service.prioritize_for_partner(1)  # Example partner ID
        self.partner_optimizer_service.update_performance()

from modules.installation_orchestrator_service import InstallationOrchestratorService

if __name__ == "__main__":
    orchestrator = InstallationOrchestratorService()
    customer_data = {
        "id": 1,
        "location": "some_location",
        "preferences": "some_prefs"
    }
    orchestrator.process_new_customer(customer_data)
    orchestrator.monitor_installations()

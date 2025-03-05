class Protocol:
    @staticmethod
    def get_jsonType(handler):
        return {
            "Configuration": handler._handle_configuration,
            "ProductionOrder": handler._handle_production_order_init,
            "ProductionOrderConclusion": handler._handle_production_order_conclusion,
            "Received": handler._handle_received_message,
        }

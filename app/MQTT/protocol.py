class Protocol:
    @staticmethod
    def get_jsonType(handler):
        return {
            "Configuration": handler.handle_configuration,
            "ProductionOrder": handler.handle_production_order_init,
            "ProductionOrderConclusion": handler.handle_production_order_conclusion,
            "Received": handler.handle_received_message,
        }

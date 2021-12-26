class GeneratorService:
        def __init__(self, model_name='generic', api_key=None):
                self.model_name = model_name
                self.api_key = api_key
        
        def generate(self, context):
                return context

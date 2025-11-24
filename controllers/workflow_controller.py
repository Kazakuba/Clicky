import os
from models.workflow import Workflow

class WorkflowController:
    def __init__(self):
        appdata_local = os.environ.get('LOCALAPPDATA')
        if appdata_local:
            app_data_dir = os.path.join(appdata_local, "Clicky")
            if not os.path.exists(app_data_dir):
                os.makedirs(app_data_dir)
            
            self.workflows_dir = os.path.join(app_data_dir, "workflows")
        else:
            self.workflows_dir = "workflows"
        
        if not os.path.exists(self.workflows_dir):
            os.makedirs(self.workflows_dir)

    def save_workflow(self, workflow, filename):
        filepath = os.path.join(self.workflows_dir, filename + ".json")
        workflow.save(filepath)

    def load_workflow(self, filename):
        filepath = os.path.join(self.workflows_dir, filename + ".json")
        return Workflow.load(filepath)

    def list_workflows(self):
        if not os.path.exists(self.workflows_dir):
            return []
        return [f.split(".")[0] for f in os.listdir(self.workflows_dir) if f.endswith(".json")]
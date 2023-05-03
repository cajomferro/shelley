from task import Task


@system(uses={"task": "Task"})
class App:
    def __init__(self):
        self.task = Task()

    @op_initial_final
    def main(self):
        match self.task.init_trial():
            case "stop":
                self.task.stop_trial()
        return ""

import sys 
from toposort import toposort_flatten

class Task(object):
    def __init__(self, name, dependencies):
        self._steps = []
        self._name = name
        self.dependencies = dependencies

    @property
    def name(self):
        return self._name

    def __call__(self):
        for step, args, kwargs in self._steps:
            step(*args, **kwargs)

    def after(self, step, *args, **kwargs):
        self._steps.append((step, args, kwargs))
        return self

    def before(self, step, *args, **kwargs):
        self._steps.insert(0, (step, args, kwargs))
        return self

class DuplicateTaskException(Exception):
    pass

class UnknownTaskException(Exception):
    pass

class Builder(object):
    def __init__(self):
        self._tasks = {}

    def add(self, task):
        if task.name in self._tasks:
            raise DuplicateTaskException(task.name)

        self._tasks[task.name] = task

    def __getitem__(self, task_name):
        return self._tasks[task_name]

    def task_names(self):
        return self._tasks.keys()

    def _traverse(self, task_name, required_tasks):
        """ Finds all tasks needed to build task_name and adds them to required_tasks """
        if task_name not in self._tasks:
            raise UnknownTaskException(task_name)

        task = self._tasks[task_name]
        for dep in task.dependencies:
            if dep not in required_tasks:
                # TODO Detect cycles here. Adding task to required_tasks in reverse traversal is intetious
                self._traverse(dep, required_tasks)
        # NOTE No incremental build support yet. Traverse on the previous line should return version of
        # the dependency and here we should check if we need to run the task based on these versions
        required_tasks.add(task_name)

    def build(self, task_name):
        required_tasks = set()
        self._traverse(task_name, required_tasks)

        # NOTE This code utilizes simple single threaded approach. Parrallel task execution is must have here, but it's not implemented for the sake of simplicity

        task_tree = {task_name : set(self._tasks[task_name].dependencies) for task_name in required_tasks}
        inorder_task_names = toposort_flatten(task_tree)

        for task_name in inorder_task_names:
            sys.stdout.write(task_name + "...")
            sys.stdout.flush()
            self._tasks[task_name]()
            sys.stdout.write("[OK]\n")

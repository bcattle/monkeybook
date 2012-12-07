import re
from voomza.apps.backend.api import BackendFacebookUserConverter
from voomza.apps.backend.getter import ResultGetter
from voomza.apps.core.utils import merge_spaces


class TaskPipeline(object):
    """
    Runs a series of FQLTasks
    """
    _results = {}

    @property
    def results(self):
        return self._results


    def __init__(self, user):
        assert self.Meta
        assert self.Meta.tasks
        assert len(self.Meta.tasks) == len({task.name for task in self.Meta.tasks}) ,\
        'If more than one task have the same name, that\'s bad'

        self.user = user
        self.graph = user.profile.get_offline_graph()
        self.facebook = BackendFacebookUserConverter(self.graph)


    def run(self):
        """
        Pull the query from each FQL task,
        run them in a batch, then feed the results
        back one task at a time
        """
        tasks = self.Meta.tasks[:]
        # Run the queries
        queries = {task.name: merge_spaces(task.fql) for task in tasks}
        fql_results = self.facebook.open_facebook.batch_fql(queries)
        # The idea is that all the queries can run together
        # but the `on_results` functions need to go in a particular order
        tasks_that_ran = set()
        for task in tasks:
            if hasattr(task, 'depends_on') and not set(task.depends_on) - tasks_that_ran:
                # No outstanding dependencies, run
                task_results = fql_results[task.name]
                task_args = {dependency: self._results[dependency] for dependency in task.depends_on}
                self._results[task.name] = task.on_results(task_results, **task_args)
            else:
                # Naive, just send to the back of the line
                tasks.remove(task)
                tasks.append(task)
        return self._results


class Task(object):
    def __init__(self):
        assert self.fql
        assert self.on_results
        self.name = self._get_canonical_name(self.__class__.__name__)

    def _get_canonical_name(self, string):
        return re.sub(r'([A-Z])([A-Z])', r'\1_\2',
            re.sub(r'([a-zA-Z])([A-Z])', r'\1_\2', string)).lower()[:-5]


class FQLTask(Task):
    # Default, just returns a getter
    def on_results(self, results):
        return ResultGetter(results)

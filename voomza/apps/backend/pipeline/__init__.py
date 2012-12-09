import re, types
from django_facebook.api import FacebookUserConverter
from voomza.apps.backend.getter import ResultGetter
from voomza.apps.core.utils import merge_spaces, profileit


class TaskPipeline(object):
    """
    Runs a series of FQLTasks
    """
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
        self.facebook = FacebookUserConverter(self.graph)
        self._results = {}


class FqlTaskPipeline(TaskPipeline):
#    @profileit(name='pipeline-run.profile')
    def run(self):
        """
        Pull the query from each FQL task,
        run them in a batch, then feed the results
        back one task at a time
        """
        tasks = self.Meta.tasks[:]
        task_names = {task.name for task in tasks}
        # Assemble queries
        # A query can also be a list of related queries, whose results
        # will all be returned as a list to the calling Task
        queries = {}
        for task in tasks:
            # Double-check
            if hasattr(task, 'depends_on') and set(task.depends_on) - task_names:
                raise Exception('Task %s depends on %s but not all of those tasks are in the pipeline' % (task.name, str(task.depends_on)))

            if isinstance(task.fql, types.StringTypes):
                queries[task.name] = merge_spaces(task.fql)
            else:
                for index, query in enumerate(task.fql):
                    queries['%s_%d' % (task.name, index)] = merge_spaces(query)
        # Run the queries
        fql_results = self.facebook.open_facebook.batch_fql(queries)
        # The idea is that all the queries can run together
        # but the `on_results` functions need to go in a particular order
        tasks_that_ran = set()
        while tasks:
            task = tasks.pop(0)
            # Does the task have dependencies that still need to run?
            if hasattr(task, 'depends_on') and set(task.depends_on) - tasks_that_ran:
                # Naive, just send to the back of the line
                tasks.remove(task)
                tasks.append(task)
            else:
                # No outstanding dependencies, run
                # Did this task ask for a list of queries?
                if isinstance(task.fql, types.StringTypes):
                    # no
                    task_results = fql_results[task.name]
                else:
                    # yes, bummer. We need all keys of the form `task_name_n`
                    curr_task_keys = filter(lambda x: re.match(r'^%s_\d+$' % task.name, x), fql_results.keys())
                    task_results = [fql_results[key] for key in curr_task_keys]
                task_args = {}
                if hasattr(task, 'depends_on'):
                    task_args = {dependency: self._results[dependency] for dependency in task.depends_on}
                self._results[task.name] = task.on_results(task_results, **task_args)
                tasks_that_ran.add(task.name)
        return self._results


class Task(object):
    def __init__(self, name=None):
        assert self.on_results
        if name:
            self.name = name
        else:
            self.name = self._get_canonical_name(self.__class__.__name__)

    def _get_canonical_name(self, string):
        return re.sub(r'([A-Z])([A-Z])', r'\1_\2',
            re.sub(r'([a-zA-Z])([A-Z])', r'\1_\2', string)).lower()[:-5]


class FQLTask(Task):
    def __init__(self, name=None):
        assert self.fql
        super(FQLTask, self).__init__(name)

    # Default, just returns a getter
    def on_results(self, results):
        return ResultGetter(results)

#    @profileit(name='task-run.profile')
    def run(self, user):
        """
        Allow ourselves to run a task in isolation
        instantiate a dummy pipeline and run it
        """
        if hasattr(self, 'depends_on') and self.depends_on:
            raise Exception('Can\'t run task standalone if it has dependencies')

        class ThisTaskPipeline(FqlTaskPipeline):
            class Meta:
                tasks = [self]
        pipeline = ThisTaskPipeline(user)
        return pipeline.run()

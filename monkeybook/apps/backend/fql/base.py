import re, types, logging, time
from django_facebook.api import FacebookUserConverter
from monkeybook.apps.backend.getter import ResultGetter
from monkeybook.apps.core.utils import merge_spaces, profileit
from monkeybook.apps.backend.getter import process_photo_results

logger = logging.getLogger(__name__)


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
    def run(self, **kwargs):
        """
        Pull the query from each FQL task,
        run them in a batch, then feed the results
        back one task at a time
        """
        tasks = self.Meta.tasks[:]
        task_names = {task.name for task in tasks}
        tasks_from_kwargs = {name for name in kwargs.keys()}
        # Pass the kwargs through
        self._results = kwargs
        # Assemble queries
        # A query can also be a list of related queries, whose results
        # will all be returned as a list to the calling Task
        queries = {}
        for task in tasks:
            # Double-check
            if hasattr(task, 'depends_on') and set(task.depends_on) - task_names - tasks_from_kwargs:
                raise Exception('Task %s depends on %s but not all of those tasks are in the pipeline' % (task.name, str(task.depends_on)))
            if isinstance(task.fql, types.StringTypes):
                queries[task.name] = merge_spaces(task.fql)
            else:
                for index, query in enumerate(task.fql):
                    queries['%s_%d' % (task.name, index)] = merge_spaces(query)
            # Run the queries
        queries_start = time.time()
        fql_results = self.facebook.open_facebook.batch_fql(queries)
        queries_elapsed = time.time() - queries_start
        logger.info('FQL query in class %s ran, took %.2f secs' % (self.__class__.__name__, queries_elapsed))
        # The idea is that all the queries can run together
        # but the `on_results` functions need to go in a particular order
        # Start by adding any tasks that came in as kwargs to "already ran"
        tasks_that_ran = tasks_from_kwargs
        while tasks:
            task = tasks.pop(0)
            # Does the task have dependencies that still need to run?
            # (that aren't in kwargs)
            if hasattr(task, 'depends_on') and set(task.depends_on) - tasks_that_ran:
                # Naive, just send to the back of the line
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
                if hasattr(task, 'depends_on'):
                    # Dependencies either live in self._results or kwargs
                    for dependency in task.depends_on:
                        if dependency in kwargs:
                            continue
                        else:
                            kwargs[dependency] = self._results[dependency]
                    self._results[task.name] = task.on_results(task_results, **kwargs)
                self._results[task.name] = task.on_results(task_results)
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
    def run(self, user, **kwargs):
        """
        Allow ourselves to run a task in isolation
        instantiate a dummy pipeline and run it
        """
        self.user = user
        #        if hasattr(self, 'depends_on') and self.depends_on:
        #            raise Exception('Can\'t run task standalone if it has dependencies')

        class ThisTaskPipeline(FqlTaskPipeline):
            class Meta:
                tasks = [self]
        pipeline = ThisTaskPipeline(user)
        return pipeline.run(**kwargs)


class BasePhotoResultsTask(FQLTask):
    """
    A task that pulls our standard PHOTO_FIELDS
    """
    def on_results(self, results, photos_i_like):
        getter = process_photo_results(
            results,
        )
        return getter

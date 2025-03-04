from clearml import Task
from clearml.automation.controller import PipelineController


def pre_execute_callback_example(a_pipeline, a_node, current_param_override):
    # type (PipelineController, PipelineController.Node, dict) -> bool
    print('Cloning Task id={} with parameters: {}'.format(a_node.base_task_id, current_param_override))
    # if we want to skip this node (and subtree of this node) we return False
    # return True to continue DAG execution
    return True


def post_execute_callback_example(a_pipeline, a_node):
    # type (PipelineController, PipelineController.Node) -> None
    print('Completed Task id={}'.format(a_node.executed))
    # if we need the actual Task to change Task.get_task(task_id=a_node.executed)
    return


# Connecting ClearML with the current process,
# from here on everything is logged automatically
task = Task.init(project_name='examples', task_name='pipeline demo',
                 task_type=Task.TaskTypes.controller, reuse_last_task_id=False)

pipe = PipelineController(default_execution_queue='default', add_pipeline_tags=False)
pipe.add_step(name='stage_data', base_task_project='examples', base_task_name='pipeline step 1 dataset artifact')
pipe.add_step(name='stage_process', parents=['stage_data', ],
              base_task_project='examples', base_task_name='pipeline step 2 process dataset',
              parameter_override={'General/dataset_url': '${stage_data.artifacts.dataset.url}',
                                  'General/test_size': 0.25},
              pre_execute_callback=pre_execute_callback_example,
              post_execute_callback=post_execute_callback_example
              )
pipe.add_step(name='stage_train', parents=['stage_process', ],
              base_task_project='examples', base_task_name='pipeline step 3 train model',
              parameter_override={'General/dataset_task_id': '${stage_process.id}'})

# Starting the pipeline (in the background)
pipe.start()
# Wait until pipeline terminates
pipe.wait()
# cleanup everything
pipe.stop()

print('done')

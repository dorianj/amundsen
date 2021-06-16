import logging
import sys

from databuilder.stemma.tasks.generators import get_task_generator

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    task = sys.argv[1]
    task_class = get_task_generator(task)
    task_class().launch_job()

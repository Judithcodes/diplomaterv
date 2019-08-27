import os
import tensorflow as tf
import glob


class TensorboardWriter:
    def __init__(self, graph, tensorboard_log_path, tb_log_name, initialize_time):
        """
        Create a Tensorboard writer for a code segment, and saves it to the log directory as its own run

        :param graph: (Tensorflow Graph) the model graph
        :param tensorboard_log_path: (str) the save path for the log (can be None for no logging)
        :param tb_log_name: (str) the name of the run for tensorboard log
        :param new_tb_log: (bool) whether or not to create a new logging folder for tensorbaord
        """
        self.graph = graph
        self.tensorboard_log_path = tensorboard_log_path
        self.tb_log_name = tb_log_name
        self.writer = None
        # self.new_tb_log = new_tb_log
        self.initialize_time = initialize_time

    def enter(self):
        if self.tensorboard_log_path is not None:
            # latest_run_id = self._get_latest_run_id()
            # if self.new_tb_log:
            #     latest_run_id = latest_run_id + 1
            save_path = os.path.join(self.tensorboard_log_path, "{}_{}".format(self.tb_log_name, self.initialize_time))
            self.writer = tf.summary.FileWriter(save_path, graph=self.graph)
        return self.writer

    # def _get_latest_run_id(self):
    #     """
    #     returns the latest run number for the given log name and log path,
    #     by finding the greatest number in the directories.
    #
    #     :return: (int) latest run number
    #     """
    #     max_run_id = 0
    #     for path in glob.glob(self.tensorboard_log_path + "/{}_[0-9]*".format(self.tb_log_name)):
    #         file_name = path.split("/")[-1]
    #         ext = file_name.split("_")[-1]
    #         if self.tb_log_name == "_".join(file_name.split("_")[:-1]) and ext.isdigit() and int(ext) > max_run_id:
    #             max_run_id = int(ext)
    #     return max_run_id

    def exit(self, exc_type, exc_val, exc_tb):
        if self.writer is not None:
            self.writer.add_graph(self.graph)
            self.writer.flush()
import os
import datetime

class PathError(Exception):
    pass


class Logger:
    FILETYPE = '.txt'

    def __init__(self, log_folder, log_name):
        if not os.path.exists(log_folder):
            raise PathError(f'Path does not exist: {log_folder}')
        else:
            self.log_folder = log_folder
            self.log_name = log_name
            # specify file type
            self.file_name = log_name + self.FILETYPE

        self.full_path_name = log_folder + "/" + self.file_name
        if os.path.exists(self.full_path_name):
            counter = 1
            while os.path.exists(self.full_path_name + '_' + str(counter)):
                counter += 1
            self.full_path_name = self.full_path_name + '_' + str(counter)
        else:
            # create file
            print(self.full_path_name)
            with open(self.full_path_name, 'w', encoding='utf-8') as f:
                pass

    def log(self, message, dt=True):
        datestamp = str(datetime.datetime.utcnow())
        with open(self.full_path_name, 'a', encoding='utf-8') as log_file:
            if dt:
                log_file.write(f"{datestamp}: {message}")
            else:
                log_file.write(message)
            # add new line
            log_file.write('\n')
            log_file.close()


# logger = ErrorLogger('../Logs', 'just_a_test_210224')
# logger.log('Hello darkness my old friend')
# logger.log('Here we go again')

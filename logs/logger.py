import logging
import os
from datetime import datetime

Log_file=f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

log_path=os.path.join(os.getcwd(), "logs")
os.makedirs(log_path,exist_ok=True)

File_path=os.path.join(log_path, Log_file)

print(File_path)


logging.basicConfig(level=logging.INFO, 
        filename=File_path,
        format="[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s")
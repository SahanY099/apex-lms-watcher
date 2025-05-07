import sys
import time
from datetime import datetime

import yaml
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import EmptyInputValidator

from src.check_essay import check_for_essay
from src.check_mcq import check_for_mcq
from src.data_types import Config, Paper
from src.notify import notify

CHECK_INTERVAL = 60


def main():
    paper_number = inquirer.number(
        message="Enter paper number:",
        min_allowed=0,
        validate=EmptyInputValidator(),
    ).execute()
    type = inquirer.select(
        message="Paper type",
        choices=[
            Choice(Paper.PaperType.MCQ.value, name="MCQ"),
            Choice(Paper.PaperType.ESSAY.value, name="ESSAY"),
        ],
    ).execute()

    if type == Paper.PaperType.MCQ:
        checker = check_for_mcq
    elif type == Paper.PaperType.ESSAY:
        checker = check_for_essay

    try:
        check_count = 0
        while True:
            check_count += 1
            current_time = datetime.now().strftime("%H:%M:%S")
            paper = checker(paper_number)

            if paper:
                try:
                    notify(paper)
                    print("Exiting...")
                    sys.exit(0)
                except Exception as e:
                    print(e)
                    sys.exit(1)
            else:
                sys.stdout.write(
                    f"\rLast checked at {current_time} (#{check_count})..."
                )
                sys.stdout.flush()
                time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\nStopping PET exam watcher...")
        sys.exit(0)


if __name__ == "__main__":
    config = Config()

    with open(config.config_file_name, "w") as file:
        yaml.dump(
            config.model_dump(),
            file,
            default_flow_style=False,
            sort_keys=False,
        )

    main()

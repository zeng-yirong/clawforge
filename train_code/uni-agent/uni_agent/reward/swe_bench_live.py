from enum import Enum

from pydantic import BaseModel

START_TEST_OUTPUT = ">>>>> Start Test Output"
END_TEST_OUTPUT = ">>>>> End Test Output"


def parse_log_pytest(log: str) -> dict[str, str]:
    """
    Copied from SWE-bench/swebench/harness/constants/__init__.py
    """

    class TestStatus(Enum):
        FAILED = "FAILED"
        PASSED = "PASSED"
        SKIPPED = "SKIPPED"
        ERROR = "ERROR"
        XFAIL = "XFAIL"

    test_status_map = {}
    for line in log.split("\n"):
        if any([line.startswith(x.value) for x in TestStatus]):
            # Additional parsing for FAILED status
            if line.startswith(TestStatus.FAILED.value):
                line = line.replace(" - ", " ")
            test_case = line.split()
            if len(test_case) <= 1:
                continue
            test_status_map[test_case[1]] = test_case[0]
    return test_status_map


def default_pytest_parser(log: str) -> dict[str, str]:
    mapping = parse_log_pytest(log)
    for test in mapping.keys():
        if "pass" in mapping[test].lower():
            mapping[test] = "pass"
        elif "skip" in mapping[test].lower():
            mapping[test] = "skip"
        else:
            mapping[test] = "fail"
    return mapping


class SWEBenchLiveVerifySpec(BaseModel):
    metadata: dict

    @property
    def instance_id(self):
        return self.metadata["instance_id"]

    @property
    def gold_patch(self):
        return self.metadata["patch"]

    @property
    def eval_script(self):
        instance = self.metadata
        test_cmds = instance["test_cmds"]

        HEREDOC_DELIMITER = "EOF_114329324912"
        test_patch = instance["test_patch"]
        apply_test_patch_command = f"git apply -v - <<'{HEREDOC_DELIMITER}'\n{test_patch}\n{HEREDOC_DELIMITER}"
        eval_script_list = [
            "#!/bin/bash",
            "set -uxo pipefail",
            apply_test_patch_command,
            f": '{START_TEST_OUTPUT}'",
            *test_cmds,
            f": '{END_TEST_OUTPUT}'",
        ]
        eval_script = "\n".join(eval_script_list)
        return eval_script

    def _get_logs_eval(self, eval_output: str):
        instance = self.metadata
        if instance["log_parser"].lower().strip() == "pytest":
            log_parser = default_pytest_parser
        else:
            raise NotImplementedError(f"Log parser {instance['log_parser']} is not implemented.")

        if START_TEST_OUTPUT in eval_output and END_TEST_OUTPUT in eval_output:
            test_content = eval_output.split(START_TEST_OUTPUT)[1].split(END_TEST_OUTPUT)[0]
            status_map = log_parser(test_content)
            return status_map, True
        else:
            status_map = {}
            return status_map, False

    def get_eval_report(self, eval_output: str):
        eval_report = {
            "resolved": False,
            "found_eval_status": False,
            "test_status": None,
        }

        # step 1: get logs eval
        status_map, found = self._get_logs_eval(eval_output)
        eval_report["found_eval_status"] = found
        if not found:
            return eval_report

        # step 2: get eval tests report
        instance = self.metadata
        suc_list = [test for test in status_map.keys() if "pass" in status_map[test].lower()]
        fail_list = [test for test in status_map.keys() if "fail" in status_map[test].lower()]
        eval_ref = {
            "instance_id": self.instance_id,
            "PASS_TO_PASS": {
                "success": list(set(suc_list) & set(instance["PASS_TO_PASS"])),
                "failure": list(set(fail_list) & set(instance["PASS_TO_PASS"])),
            },
            "FAIL_TO_PASS": {
                "success": list(set(suc_list) & set(instance["FAIL_TO_PASS"])),
                "failure": list(set(fail_list) & set(instance["FAIL_TO_PASS"])),
            },
        }
        eval_report["test_status"] = eval_ref

        if (
            len(eval_ref["PASS_TO_PASS"]["failure"]) == 0
            and len(eval_ref["FAIL_TO_PASS"]["failure"]) == 0
            and len(eval_ref["FAIL_TO_PASS"]["success"]) > 0
        ):
            eval_report["resolved"] = True

        return eval_report

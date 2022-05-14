"""This formatter outputs the issues in JSON."""
import json
from datetime import datetime

from taint_module.helpers.vulnerabilities_helper.vulnerability_helper import SanitisedVulnerability


def report(
    vulnerabilities,
    file_obj,
    print_sanitised,
):
    """
    Prints issues in JSON format.
    Args:
        vulnerabilities: list of vulnerabilities to report
        file_obj: The output file object, which may be sys.stdout
    """
    TZ_AGNOSTIC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    time_string = datetime.utcnow().strftime(TZ_AGNOSTIC_FORMAT)

    machine_output = {
        "generated_at": time_string,
        "vulnerabilities": [
            vuln.as_dict()
            for vuln in vulnerabilities
            if print_sanitised or not isinstance(vuln, SanitisedVulnerability)
        ],
    }

    result = json.dumps(machine_output, indent=4)

    with file_obj:
        file_obj.write(result)

""" Robot test library - utils """
import json
from os.path import abspath


class Utils:
    """
    Utilities for robot tests
    """

    @staticmethod
    def make_dict_from_json_file(file_path):
        """
        Make JSON object from json file
        :param file_path: path to file
        :type file_path: str
        :return: JSON object
        """
        path = abspath(file_path)
        with open(path) as file:
            data = json.load(file)
        return data

    @staticmethod
    def update_dict_with_params(json_dict, params):
        """
        Go throw dict recursively and update key if present in parameters dict
        :param json_dict: dict
        :param params: dict
        :return: updated_dict: dict
        """

        def update_values_by_key(json_d, prms):
            for k in json_d.keys():
                for params_k, params_v in prms.items():
                    if k == params_k:
                        if params_v == "remove_me":
                            del json_d[k]
                        else:
                            json_d[k] = params_v
                if k in json_d.keys():  # if k was not deleted we continue
                    if isinstance(json_d[k], dict):
                        update_values_by_key(json_d[k], prms)
                    if isinstance(json_d[k], list):
                        for dct in json_d[k]:
                            update_values_by_key(dct, prms)
            return json_d

        updated_dict = update_values_by_key(json_dict, params)
        return updated_dict

    @staticmethod
    def construct_dq_check_response(dq_checks: list) -> list:
        """
        Update DQ checks results list from Athena to human readable list
        :param dq_checks: list
        :return: updated_dict: list
        """

        return [{'check_name': i['Data'][0]['VarCharValue'],
                 'check_result': 'PASSED' if not i['Data'][1]['VarCharValue'] else "FAILED",
                 'error': i['Data'][1]['VarCharValue']} for i in dq_checks]

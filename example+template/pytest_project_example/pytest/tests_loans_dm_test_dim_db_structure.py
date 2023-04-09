# run this with the command
# pytest tests_loans_dm_test_dim_db_structure.py ${CSV with expected result}


import csv
import json
import os
from collections import namedtuple
from csv import reader
from os import path

import allure
import pytest
from simple_settings import settings

from api.aws.athena import AthenaHelper
from constants import ROOT_PATH, DIM_METADATA

datapath = path.join(ROOT_PATH, 'data/loans/dump/')


def format_metadata():
    with open(path.join(datapath, DIM_METADATA), 'r') as f:
        data = json.loads(f.read())
    f = csv.writer(open(path.join(datapath, "dimMetadata.formatted"), "w+", newline=''))
    f.writerow(["target_database, table_name, data_type, col_name, pkeys, id_name"])
    for js in data:
        pkeys = list(k for k, v in js["pkeys"].items())
        id_name = js.get("id_name")
        columns_varchar = list(k for k, v in js["fields"].items() if v == 'string') + \
                          list(k for k, v in js["pkeys"].items() if v == 'string')
        columns_int = list(k for k, v in js["fields"].items() if v == 'int') + \
                          list(k for k, v in js["pkeys"].items() if v == 'int')
        columns_double = list(k for k, v in js["fields"].items() if v == 'double') + \
                          list(k for k, v in js["pkeys"].items() if v == 'double')
        columns_date = list(k for k, v in js["fields"].items() if v == 'date') + \
                          list(k for k, v in js["pkeys"].items() if v == 'date')
        columns_timestamp = list(k for k, v in js["fields"].items() if v == 'timestamp') + \
                          list(k for k, v in js["pkeys"].items() if v == 'timestamp')
        if columns_varchar:
            f.writerow([settings.DATAMARTS_LOANS, js["dim_name"], "varchar", ' '.join(columns_varchar),
                        ' '.join(pkeys), id_name])
        if columns_int:
            f.writerow([settings.DATAMARTS_LOANS, js["dim_name"], "integer", ' '.join(columns_int),
                        ' '.join(pkeys), id_name])
        if columns_double:
            f.writerow([settings.DATAMARTS_LOANS, js["dim_name"], "double", ' '.join(columns_double),
                        ' '.join(pkeys), id_name])
        if columns_date:
            f.writerow([settings.DATAMARTS_LOANS, js["dim_name"], "date", ' '.join(columns_date),
                        ' '.join(pkeys), id_name])
        if columns_timestamp:
            f.writerow([settings.DATAMARTS_LOANS, js["dim_name"], "timestamp", ' '.join(columns_timestamp),
                        ' '.join(pkeys), id_name])


def pytest_generate_tests(metafunc):
    """ Generate tests for test_table_structure """
    if 'csv_test_data' in metafunc.fixturenames:
        format_metadata()
        test_data_type = namedtuple('test_data', 'target_database, table_name, data_type, col_name, pkeys, id_name')
        input_data = []
        with open(path.join(datapath, "dimMetadata.formatted")) as f:
            csv_data = reader(f, delimiter=',', quotechar='"')
            next(csv_data)  # skip headers
            for row in csv_data:
                target_database, table_name, data_type, col_name, pkeys, id_name = [v.strip() for v in row]
                input_data.append(pytest.param(
                    test_data_type(
                        target_database.lower(),
                        table_name.lower(),
                        data_type.lower(),
                        sorted(list(set(col_name.lower().split()))),
                        sorted(list(set(pkeys.lower().split()))),
                        id_name.lower()), id=table_name)
                )
        metafunc.parametrize('csv_test_data', input_data)


class TestDB:
    @classmethod
    def teardown_class(cls):
        os.remove(path.join(datapath, "dimMetadata.formatted"))

    @pytest.mark.database_structure_loans
    def test_table_structure(self, request, csv_test_data):
        """ Check database structure """
        allure.dynamic.title(f'Verified columns for {request.node.callspec.id} '
                             f'table have expected data types in prepared zone')
        query = f"select column_name, data_type " \
                f"from information_schema.columns " \
                f"where table_schema = '{csv_test_data.target_database}' " \
                f"and table_name = '{csv_test_data.table_name}' "

        if csv_test_data.data_type:
            columns_list = ', '.join([f"'{c}'" for c in csv_test_data.col_name])
            query += f'and column_name in ({columns_list})'

        ah = AthenaHelper()
        ah.execute_query(database='*', query=query, output_location=settings.S3_BUCKET)

        table_dict = {}
        for r in ah.fetch():
            table_dict[r.column_name] = r.data_type

        assert len(csv_test_data.col_name) == len(table_dict), f'Wrong number of fields!\n' \
                                                               f'Expected: {csv_test_data.col_name};\n' \
                                                               f'Actual:   {sorted(table_dict.keys())}'

        assert csv_test_data.col_name == sorted(table_dict.keys()), 'Wrong field names!'

        if csv_test_data.data_type:
            assert csv_test_data.data_type == ' '.join(set(table_dict.values())), f'Wrong column types!\n{table_dict}'

    @pytest.mark.database_structure_loans
    def test_table_duplicates(self, request, csv_test_data):
        allure.dynamic.title(f'Verified columns for {request.node.callspec.id} '
                             f'table have unique primary keys')

        if csv_test_data.id_name:
            query = f"select {csv_test_data.id_name}, count(*) as cnt from \"{csv_test_data.target_database}\".{csv_test_data.table_name} " \
                    f"group by {csv_test_data.id_name} having count(*) > 1"

            ah = AthenaHelper()
            ah.execute_query(database='*', query=query, output_location=settings.S3_BUCKET)

            id_name_amount = []
            for r in ah.fetch():
                id_name_amount.append(r)

            assert len(id_name_amount) == 0, f'Ids are not unique: {id_name_amount}'

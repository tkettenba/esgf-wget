import os
import pytest

def pytest_addoption(parser):
    parser.addoption("--data", action="store", default="test_data.json",
                     help="test data filename")

@pytest.fixture
def data(request):
    data_file = request.config.getoption("--data")
    os.environ["WGET_API_TEST_DATA"] = data_file
    return(data_file)

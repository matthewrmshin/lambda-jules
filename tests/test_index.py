"""Tests for lambda handler that wraps JULES."""


import os
import pytest

import task.index


def test_handler_default():
    """Test the lambda handler function, default HTTP method."""
    ret = task.index.handler({})
    assert ret['statusCode'] == 200
    assert ret['body'] == task.index.__doc__


def test_handler_get():
    """Test the lambda handler function, GET HTTP method."""
    ret = task.index.handler({'httpMethod': 'GET'})
    assert ret['statusCode'] == 200
    assert ret['body'] == task.index.__doc__


def test_handler_post(monkeypatch):
    """Test the lambda handler function, POST HTTP method."""

    
    def mock_run_jules(event):
        return event['body']

    monkeypatch.setattr(task.index, 'run_jules', mock_run_jules)
    event = {'httpMethod': 'POST', 'body': 'turkey'}
    ret = task.index.handler(event)
    assert ret == {
        'statusCode': 200,
        'body': 'turkey',
        'headers': {'content-type': 'application/octet-stream'},
        'isBase64Encoded': True,
    }


@pytest.mark.parametrize('httpmethod', [('PUT',), ('DELETE',)])
def test_handler_unsupported_method(httpmethod):
    """Test the lambda handler function, unsupported HTTP method."""
    ret = task.index.handler({'httpMethod': httpmethod})
    assert ret['statusCode'] == 405
    assert ret['body'] == f'{httpmethod}: HTTP method not supported'


def test_run_jules(monkeypatch):
    """Test the :func:`task.index.run_jules` function."""
    mock_unpack_input_dict = {}

    def mock_unpack_input(body):
        mock_unpack_input_dict['body'] = body

    def mock_pack_output(outputdir):
        return 'SGVsbG8K'

    monkeypatch.setenv(
        'LAMBDA_JULES_EXE',
        os.path.join(os.path.dirname(__file__), 'mock-jules-exe'))
    orig_dir = os.getcwd()
    monkeypatch.setattr(task.index, 'unpack_input', mock_unpack_input)
    monkeypatch.setattr(task.index, 'pack_output', mock_pack_output)
    ret = task.index.run_jules({'body': 'heart+lung+liver'})
    assert mock_unpack_input_dict['body'] == 'heart+lung+liver'
    assert ret == 'SGVsbG8K'
    assert os.getcwd() == orig_dir


def test_unpack_input(tmpdir):
    """Test the :func:`task.index.unpack_input` function."""
    orig_dir = os.getcwd()
    os.chdir(tmpdir)
    input_path = os.path.join(os.path.dirname(__file__), 'test-input.txt')
    try:
        body = open(input_path).read()
        task.index.unpack_input(body)
        assert set(os.listdir()) == {'greet.txt', 'hello.txt'}
        assert open('greet.txt').read() == 'Greet\n'
        assert open('hello.txt').read() == 'Hello\n'
    finally:
        os.chdir(orig_dir)


def test_pack_output(tmpdir):
    """Test the :func:`task.index.pack_output` function."""
    for name, content in (('greet.txt', 'Greet'), ('hello.txt', 'Hello')):
        with open(os.path.join(tmpdir, name), 'w') as handle:
            handle.write(content)
    assert isinstance(task.index.pack_output(tmpdir), str)

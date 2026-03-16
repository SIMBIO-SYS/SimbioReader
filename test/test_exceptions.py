import sys
import types

import pytest

if "mystrtools" not in sys.modules:
    mystrtools_stub = types.ModuleType("mystrtools")
    mystrtools_stub.convert_case = lambda value, *_args, **_kwargs: value #type: ignore
    sys.modules["mystrtools"] = mystrtools_stub

from SimbioReader.exceptions import SizeError


def test_size_error_is_exception():
    err = SizeError(size=10, expected=20)
    assert isinstance(err, Exception)


def test_size_error_fields_and_args():
    err = SizeError(size=10, expected=20)
    assert err.size == 10
    assert err.expected == 20
    assert err.args == (10, 20)


def test_size_error_message():
    err = SizeError(size=10, expected=20)
    assert str(err) == "The file size is 10 but the expected size is 20"


def test_size_error_can_be_raised():
    with pytest.raises(SizeError, match="The file size is 10 but the expected size is 20"):
        raise SizeError(size=10, expected=20)

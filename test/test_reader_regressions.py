from pathlib import Path
from types import SimpleNamespace
from xml.dom.minidom import parse

import numpy as np
import pytest
from PIL.Image import Image
from rich.console import Console
from rich.panel import Panel

from SimbioReader.exceptions import SizeError
from SimbioReader.sr import SimbioObject, SimbioReader
from SimbioReader.tools import getElement, updateXML


PRODUCT = Path('test/data/sim_cal_stc_cruise_ico11_2024-04-08_001')
LABEL = next(PRODUCT.glob('*.lblx'))


def test_vihi_segment_show_without_filter():
    segment = object.__new__(SimbioObject)
    segment.channel = 'vihi'
    segment.file_name = Path('segment.dat')
    segment.exposure_time = '1'
    segment.data_structure = SimpleNamespace(show=lambda: Panel('Structure'))
    segment.detector = SimpleNamespace(show=lambda: Panel('Detector'))
    panel = segment.show()
    console = Console(record=True)
    console.print(panel)
    assert 'segment.dat' in console.export_text()


@pytest.mark.parametrize('channel, name', [
    ('stc', 'chanel'),
    ('stc', 'segment_001'),
    ('vihi', 'filter_panl'),
    ('vihi', 'segment_999'),
    (None, 'channel'),
])
def test_missing_reader_attributes_raise_attribute_error(channel, name):
    reader = object.__new__(SimbioReader)
    if channel is not None:
        reader.channel = channel

    with pytest.raises(AttributeError, match=name):
        getattr(reader, name)
    assert not hasattr(reader, name)
    assert getattr(reader, name, 'fallback') == 'fallback'


def make_object(tmp_path, *, offset=0, truncated=False, verbose=False, order='Last Index Fastest'):
    label = parse(str(LABEL))
    area = getElement(label, 'File_Area_Observational')
    updateXML(area, 'data_type', 'UnsignedLSB2')
    updateXML(area, 'offset', offset)
    updateXML(area, 'elements', 2, idx=0)
    updateXML(area, 'elements', 3, idx=1)
    updateXML(area, 'axis_index_order', order)
    values = np.array([0, 32767, 32768, 65535, 10, 20], dtype='<u2')
    binary = tmp_path / 'image.dat'
    binary.write_bytes(b'H' * offset + values.tobytes()[: -2 if truncated else None])
    return SimbioObject(str(binary), 'stc', getElement(label, 'img:Imaging'),
                        getElement(label, 'geom:Geometry'), area, verbose=verbose)


@pytest.mark.parametrize('offset', [0, 8])
@pytest.mark.parametrize('order', ['Last Index Fastest', 'First Index Fastest'])
def test_unsigned_pixels_offset_and_axis_order(tmp_path, offset, order):
    image = make_object(tmp_path, offset=offset, order=order).img
    assert image.shape == (2, 3)
    expected = np.array([0, 32767, 32768, 65535, 10, 20]).reshape(
        (2, 3), order='C' if order == 'Last Index Fastest' else 'F'
    )
    np.testing.assert_array_equal(image, expected)
    assert image.dtype == np.dtype('<u2')


@pytest.mark.parametrize('verbose', [False, True])
def test_truncated_array_always_rejected(tmp_path, verbose):
    with pytest.raises(SizeError):
        make_object(tmp_path, truncated=True, verbose=verbose)


def test_stop_scet_comes_from_stop_field(tmp_path, monkeypatch):
    label = parse(str(LABEL))
    updateXML(label, 'psa:spacecraft_clock_stop_count', '1/0777258317:00001')
    destination = tmp_path / 'product.lblx'
    destination.write_text(label.toxml())
    monkeypatch.setattr('SimbioReader.sr.Data', lambda **kwargs: SimpleNamespace())
    reader = SimbioReader(destination, updateCheck=False)
    assert reader.stop_scet == '1/0777258317:00001'
    assert reader.stop_scet != reader.start_scet


def test_vihi_summary_and_details_without_filters():
    reader = object.__new__(SimbioReader)
    reader.channel = 'vihi'
    reader.console = Console()
    reader.pdsLabel = Path('vihi.lblx')
    reader.info = lambda: Panel('Info')
    reader.target = SimpleNamespace(show=lambda: Panel('Target'))
    segment = SimpleNamespace(
        detector=SimpleNamespace(show=lambda **kwargs: Panel('Detector')),
        data_structure=SimpleNamespace(show=lambda **kwargs: Panel('Structure')),
    )
    reader.data = SimpleNamespace(segments=['segment_001'], segment_001=segment)
    assert isinstance(reader.summary(), Panel)
    assert isinstance(reader.show(all_info=True), Panel)


def test_image_returns_selected_filter_image():
    reader = object.__new__(SimbioReader)
    reader.channel = 'stc'
    reader.data = SimpleNamespace(
        filters=['panl', 'panh'],
        filter_panl=SimpleNamespace(img=np.zeros((2, 3), dtype=np.uint16)),
        filter_panh=SimpleNamespace(img=np.ones((4, 5), dtype=np.uint16)),
    )

    image = reader.image(filter_name='PANH')

    assert isinstance(image, Image)
    assert image.size == (5, 4)


def test_image_returns_selected_vihi_segment():
    reader = object.__new__(SimbioReader)
    reader.channel = 'vihi'
    reader.data = SimpleNamespace(
        segments=['segment_001', 'segment_002'],
        segment_001=SimpleNamespace(img=np.zeros((2, 3), dtype=np.float32)),
        segment_002=SimpleNamespace(img=np.ones((4, 5), dtype=np.float32)),
    )

    image = reader.image(segment=2)

    assert isinstance(image, Image)
    assert image.size == (5, 4)


@pytest.mark.parametrize('channel, data', [
    (
        'stc',
        SimpleNamespace(
            filters=['panl', 'panh'],
            filter_panl=SimpleNamespace(img=np.zeros((2, 3))),
            filter_panh=SimpleNamespace(img=np.zeros((2, 3))),
        ),
    ),
    (
        'vihi',
        SimpleNamespace(
            segments=['segment_001', 'segment_002'],
            segment_001=SimpleNamespace(img=np.zeros((2, 3))),
            segment_002=SimpleNamespace(img=np.zeros((2, 3))),
        ),
    ),
])
def test_image_requires_selector_for_multiple_items(channel, data):
    reader = object.__new__(SimbioReader)
    reader.channel = channel
    reader.data = data

    with pytest.raises(ValueError, match='multiple'):
        reader.image()

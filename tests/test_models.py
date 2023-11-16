from linse.util import data_path
from linse.models import MODELS, Model


def test_Model():
    model = MODELS['dolgo']
    assert model.info['compiler'] == 'Johann-Mattis List'
    assert len(model.tones) == 0
    assert len(model.vowels) == 1
    assert 'Model' in str(model)
    assert 'sca' in repr(model)
    assert 'â' in model
    assert model == Model(data_path().parent / 'models' / 'dolgo')

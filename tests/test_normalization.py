import pytest
from transform.mapping.name_normalizer import NameNormalizer

def test_name_normalization():
    """Test various football name edge cases."""
    norm = NameNormalizer.normalize
    assert norm('M. Salah ') == 'm salah'
    assert norm('Özil') == 'ozil'
    assert norm('Kévin De Bruyne') == 'kevin de bruyne'
    assert norm('Team-A (FC)') == 'team a fc'
    assert norm('  Multiple   Spaces  ') == 'multiple spaces'
    assert norm(None) == ''
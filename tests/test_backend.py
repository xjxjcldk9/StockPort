from stockport.portfolio import get_all_prices, get_price

period = '1mo'


def test_get_price_US():
    dat = get_price('AAPL', period)
    assert len(dat['AAPL']) > 0


def test_get_price_TW():
    dat = get_price('2330.TW', period)
    assert len(dat['2330.TW']) > 0


def test_get_prices_US():
    dat = get_price('AAPL ABNB', period)
    assert len(dat['AAPL']) > 0


def test_get_prices_TW():
    dat = get_price('2330.TW 2454.TW', period)
    assert len(dat['2330.TW']) > 0


def test_get_all_prices():
    assert len(get_all_prices('TW', period)) > 0
    assert len(get_all_prices('US', period)) > 0

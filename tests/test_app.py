from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_turbine_selection_and_charts():
    root = Path(__file__).parents[1]
    app = AppTest.from_file(str(root / "streamlit_app.py"), default_timeout=30).run()
    assert not app.exception
    assert [m.value for m in app.metric] == ["3","1","1","1"]
    for turbine, state in [("WT-001","HEALTHY"),("WT-002","WARNING"),("WT-003","CRITICAL")]:
        app.selectbox(key="turbine").select(turbine).run()
        assert not app.exception
        assert any(state in item.value for item in app.subheader)
    app.selectbox[1].select("vibration_mm_s").run()
    assert not app.exception

def test_invalid_threshold_order_shows_message():
    root = Path(__file__).parents[1]
    app = AppTest.from_file(str(root / "streamlit_app.py"), default_timeout=30).run()
    app.slider[0].set_value(100).run()
    app.slider[1].set_value(80).run()
    assert not app.exception
    assert "at least" in app.error[0].value

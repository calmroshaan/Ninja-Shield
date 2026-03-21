import os
import sys

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    data_dir = os.path.join(base_path, 'apify_fingerprint_datapoints', 'data')
    os.environ['BROWSERFORGE_DATA_DIR'] = data_dir

    # Monkey-patch apify_fingerprint_datapoints BEFORE any import uses it
    from pathlib import Path
    import apify_fingerprint_datapoints as _apify

    _data = Path(data_dir)

    _apify.get_browser_helper_file  = lambda: _data / 'browser-helper-file.json'
    _apify.get_header_network       = lambda: _data / 'header-network-definition.zip'
    _apify.get_headers_order        = lambda: _data / 'headers-order.json'
    _apify.get_input_network        = lambda: _data / 'input-network-definition.zip'
    _apify.get_fingerprint_network  = lambda: _data / 'fingerprint-network-definition.zip'
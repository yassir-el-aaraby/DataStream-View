from collections import deque
import copy
class FilterObjects:
    filtered_data_large = deque(maxlen=6600)
    filtered_data = []
    gmac = None
    dmac = None
    rssi = None
    # def __init__(self):
        
    def set_criteria(gmac, dmac, rssi):
        FilterObjects.gmac = [item.strip() for item in gmac.split(',')] if gmac is not None else None
        FilterObjects.dmac = [item.strip() for item in dmac .split(',')] if gmac is not None else None
        FilterObjects.rssi = int(rssi) if rssi else None
 

    def filter_and_store(obj):
        # Check if obj["gmac"] is in FilterObjects.gmac or if FilterObjects.gmac is empty or None
        gmac_condition = FilterObjects.gmac == [''] or FilterObjects.gmac == None or obj["gmac"] in FilterObjects.gmac
        # Check if obj["dmac"] is in FilterObjects.dmac or if FilterObjects.dmac is empty or None
        dmac_condition = FilterObjects.dmac == [''] or FilterObjects.dmac == None  or obj["dmac"] in FilterObjects.dmac
        # Check if obj["rssi"] is within the specified range or if FilterObjects.rssi is None
        rssi_condition = FilterObjects.rssi is None or (0 >= int(obj["rssi"]) >= int(FilterObjects.rssi))
        if gmac_condition and dmac_condition and rssi_condition:
            FilterObjects.filtered_data_large.appendleft(obj)
            FilterObjects.filtered_data = deque(copy.copy(obj) for obj in list(FilterObjects.filtered_data_large)[:100])

    def clear_filter(gmac_var, dmac_var, rssi_var):
        gmac_var.set("")
        dmac_var.set("")
        rssi_var.set("")
        FilterObjects.gmac = None
        FilterObjects.dmac = None
        FilterObjects.rssi = None
        FilterObjects.filtered_data = []
        
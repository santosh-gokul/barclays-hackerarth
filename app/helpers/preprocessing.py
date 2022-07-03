from app.data.items import item_data


def preprocess_item_dict(item_dict: dict):
    seen = []
    ctr_resp_items = {}
    return_dict = {'Data': []}
    for item in item_dict['Data']:
        if item['name'] in seen:
            seen.append(item['name'])
            ctr_resp_items[item['name']] = 0
            return_dict['Data'].append(item)
        else:
            ctr_resp_items[item['name']]+=1
            item['name']+="_"+str(ctr_resp_items[item['name']])
            return_dict['Data'].append(item)
    return return_dict

def get_item_list():
    item_name_list = []
    for item in item_data["Data"]:
        if item['outOfStock']=="FALSE":
            item_name_list.append(item['name'])
    return item_name_list

def get_store_item_map(store_name_list):
    store_item_map = {}
    for store in store_name_list:
        store_item_map[store] = {}
        for item_info in item_data['Data']:
            if item_info['outOfStock']=="FALSE":
                store_item_map[store][item_info['name']] = item_info

    return store_item_map

def getTotalItemWithinAStore(store: str, store_item_map):
    item_count = 0
    for item in store_item_map[store].values():
        if (int(item['availableQuantity'])>0):
            item_count+=1
    return item_count
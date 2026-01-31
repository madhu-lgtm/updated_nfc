# IMPORTENT CONTENUE WORK FROM HERE
def convert_data_to_writable_16_bytes(*field_sizes, **fields) -> bytes:
    """
    field_sizes: sequence of byte sizes (must sum <= 16)
    fields: keyword arguments in the same order as field_sizes
            - int  -> encoded as big-endian unsigned
            - str  -> UTF-8 truncated/padded to given size
    """
    bytes_in_one_block = 16
    if len(field_sizes) != len(fields):
        raise ValueError("Number of field sizes must match number of keyword fields")

    total_size = sum(field_sizes)
    if total_size > bytes_in_one_block:
        raise ValueError(f"Total field bytes {total_size} exceed 16")

    result = b""
    # preserve the order in which kwargs are passed
    for (name, value), size in zip(fields.items(), field_sizes):
        if isinstance(value, int):
            # encode integer as big-endian, exactly `size` bytes
            max_val = (1 << (8 * size)) - 1
            if not (0 <= value <= max_val):
                raise ValueError(f"Field '{name}' value {value} does not fit in {size} bytes")
            part = value.to_bytes(size, byteorder="big")
        elif isinstance(value, str):
            # encode string as UTF‑8, truncate/pad with 0x00 to exact size
            raw = value.encode("utf-8")[:size]
            part = raw + b"\x00" * (size - len(raw))
        else:
            raise TypeError(f"Unsupported type for field '{name}': {type(value)}")

        result += part

    # pad whole block to 16 bytes if needed
    if len(result) < bytes_in_one_block:
        result += b"\x00" * (bytes_in_one_block - len(result))

    return result

print(convert_data_to_writable_16_bytes(2,2,3,3,3,2,1,data_ver = 1, sig_offset = 40, batt_volt_max =25200, batt_volt_min = 22000, batt_total_cap = 22000, batt_c_rat = 10, bind_type = 1 ))
#print(convert_data_to_writable_16_bytes(8,8,batt_chem_type = "Li-ion",vendor_id="Vendor_1" ))
#print(convert_data_to_writable_16_bytes(1,2,2,3,1,7,cell_count = 6 ,cell_volt_max = 4200 ,cell_volt_min = 3700 ,cell_cap = 22000 ,cell_c_rat = 10,cell_config = "1S6P"))











#https://www.perplexity.ai/search/how-to-convert-string-to-hexa-vvtUAh8ZSxyPJE4lBzXDDQ


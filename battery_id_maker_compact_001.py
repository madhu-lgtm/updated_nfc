def convert_data_to_writable_16_bytes(*args,**kwargs):
    no_of_bytes = 0
    bytes_in_one_block = 16
    num_byte_cond = False

    # print(type(args))
    # print(type(kwargs))

    for arg in args: #Number og bytes must be less then 16
        # print(arg)
        no_of_bytes += arg

    if no_of_bytes <= bytes_in_one_block:
        num_byte_cond = True
    else:
        num_byte_cond = False
    

    # print(f"no_of_bytes = {no_of_bytes}") 
        
    # for key,val in kwargs.items():
    #     print(f"{key} = {val}")
    
    if num_byte_cond == True :
        count = 0
        writable_bytes = b""
        total_writable_bytes = b""
        for key,val in kwargs.items():
            # print(f"{val} is {type(val)}")
            if type(val) is int:
                pad = args[count] 
                data_str = f"{val:0{pad}x}"
                for p in range(pad):
                    writable_byte = bytes.fromhex(data_str[(pad+p):(pad-p)])
                print(data_str)

            elif type(val) is str:
                pass
            count += 1
    

convert_data_to_writable_16_bytes(2,2,3,3,3,2,1,data_ver = 1, sig_offset = 1, batt_volt_max = 1, batt_volt_min = 0, batt_total_cap = 1, batt_c_rat = 1, bind_type = 1 )

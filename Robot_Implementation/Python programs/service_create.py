ant_hill_list = []

def id_to_ant_hill(id):
    ant_hill = {'ah_number':None, 'is_qah':None, 'service_1':None, 'service_2':None, "trash":None}
    binary_string = bin(id)[2:]
    binary_string = '0'*(8-len(binary_string)) + binary_string #To add preceding zeros
    ant_hill['is_qah'] = int(binary_string[0],2)
    ant_hill['ah_number'] = int(binary_string[1:3],2)
    ant_hill['service_2'] = int(binary_string[3:5],2)
    ant_hill['service_1']  = int(binary_string[5:7],2)
    ant_hill['trash'] = int(binary_string[7])
    return ant_hill

def create_all_services():
    global ant_hill_list
    block_services = []
    trash_services = []
    final_services = []

    for ant_hill in ant_hill_list:
        ant_hill_node = ant_hill['ah_number']+11
        services = []
        if(ant_hill['service_1']):
            services.append((ant_hill_node,0,1,ant_hill['service_1']))
        if(ant_hill['service_2']):
            services.append((ant_hill_node,0,2,ant_hill['service_2']))
        if(ant_hill['trash']):
            trash = None
            if(ant_hill['service_1']):
                trash = 2
            elif(ant_hill['service_2']):
                trash = 1
            services.append((ant_hill_node,1,trash,None))
        #print(services)
        if(ant_hill['is_qah']):
            final_services.extend(services)
        else:
            for service in services:
                if(service[1] == 1):
                    trash_services.append(service)
                else:
                    block_services.append(service)

    while(block_services and trash_services):
        if(not final_services or final_services[-1][1] == 1):
            service = block_services.pop()
            final_services.append(service)
        else:
            last_service = final_services[-1]
            flag1 = 1
            for service in trash_services:
                if(service[0] == last_service[0]):
                    trash_services.remove(service)
                    final_services.append(service)
                    flag1 = 0
                    break
            if(flag1):
                present_node = final_services[-1][0]
                opposite_nodes_list = [[11,14],[12,13]]
                for nodes in opposite_nodes_list:
                    if(present_node in nodes):
                        opposite_node = sum(nodes) - present_node
                flag2 = 1
                for service in block_services:
                    if(service[0] == opposite_node):
                        flag2 = 0
                        break
                if(flag2):
                    for service in trash_services:
                        if(service[0] == opposite_node):
                            trash_services.remove(service)
                            final_services.append(service)
            if(last_service == final_services[-1]):
                service = block_services.pop()
                final_services.append(service)

    final_services.extend(block_services)
    final_services.extend(trash_services)
    return final_services

l = [6,33,208,99]
for i in l:
    ant_hill_list.append(id_to_ant_hill(i))

res = create_all_services()
print(res)
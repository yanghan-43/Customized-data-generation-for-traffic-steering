from config import *

def cell_barring(cells, cells_x_coordinates, cells_y_coordinates, pes_x_coordinates, pes_y_coordinates):
    for cell in cells:
        if cell.cell_barring_flag == 1:

            distance = {}
            remove_pe_list = []
            handover_num = int(cell.load - 45)
            for i in range(len(pes_x_coordinates[cell.id])):
                x = pes_x_coordinates[cell.id][i]
                y = pes_y_coordinates[cell.id][i]
                distance.update({i: (pow(cells_x_coordinates[cell.id] - x, 2) + pow(cells_y_coordinates[cell.id] - y, 2))})

            j = 1
            if j <= handover_num:
                max_key = max(distance, key=lambda x: distance[x])
                remove_pe_list.append(max_key)
                distance.pop(max_key)

            for k in range(len(remove_pe_list)):
                pe_id = remove_pe_list[k]
                for cell_id in OUTFLOW_SETTING[cell.id]:
                    if (pow(pes_x_coordinates[cell.id][pe_id],cells_x_coordinates[cell_id])
                            + pow(pes_y_coordinates[cell.id][pe_id],cells_y_coordinates[cell_id])) <= (CELL_RADIUS/30)*(CELL_RADIUS/30):
                        pes_x_coordinates[cell_id].append(pes_x_coordinates[cell.id][pe_id])
                        pes_y_coordinates[cell_id].append(pes_y_coordinates[cell.id][pe_id])
                        pes_x_coordinates[cell.id].pop(pe_id)
                        pes_y_coordinates[cell_id].pop(pe_id)
                        break

        cell.radius = cell.radius + 20
    return pes_x_coordinates, pes_y_coordinates

